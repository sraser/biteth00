import time
import pyupbit
import datetime
import numpy as np
import telegram

access = ""
secret = ""

def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    return pyupbit.get_current_price(ticker)

def get_bestk(ticker):
    bestk = 0
    bestror = 0
    df = pyupbit.get_ohlcv(ticker, count=7, period=1)
    for k in np.arange(0.3, 1.0, 0.05):
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)
        df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'],
                             1)
        df['hpr'] = df['ror'].cumprod()
        if df.iloc[-1]['hpr'] > bestror:
            bestk = k
            bestror = df.iloc[-1]['hpr']
    return bestk, bestror

upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

btc_state = 0
eth_state = 0

btc_ini = get_balance("BTC")
eth_ini = get_balance("ETH")

if btc_ini != 0 :
    btc_state = 1
if eth_ini != 0 :
    eth_state = 1

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        bot = telegram.Bot(token='1895925551:AAEu0Axf5JbQULDuWLtmnJ6DQ1QKW97zbYE')
        chat_id = 1636335355

        bestcalkBTC, bestcalrorBTC = get_bestk("KRW-BTC")
        target_price = get_target_price("KRW-BTC", bestcalkBTC)
        current_price = get_current_price("KRW-BTC")
        btcfee = 5000 / target_price
        btc = get_balance("BTC")
        time.sleep(0.1)

        bestcalkETH, bestcalrorETH  = get_bestk("KRW-ETH")
        target_priceETH = get_target_price("KRW-ETH", bestcalkETH)
        current_priceETH = get_current_price("KRW-ETH")
        ethfee = 5000 / target_priceETH
        eth = get_balance("ETH")
        time.sleep(0.1)

        krw = get_balance("KRW")

        if start_time < now < start_time + datetime.timedelta(seconds=15):
            btcratio = (target_price - current_price) / current_price * 100
            ethratio = (target_priceETH - current_priceETH) / current_priceETH * 100
            msgBTC = "BTC : k = %.2f , 목표 = %d , \n7일최대 = %.4f %%, 요구상승 : %.2f %%" % (bestcalkBTC, target_price, bestcalrorBTC*100, btcratio)
            msgETH = "ETH : k = %.2f , 목표 = %d , \n7일최대 = %.4f %%, 요구상승 : %.2f %%" % (bestcalkETH, target_priceETH, bestcalrorETH*100, ethratio)
            msgKRW = "오늘의 시드머니 = %d 원" % (krw)
            bot.sendMessage(chat_id=chat_id, text=msgBTC)
            bot.sendMessage(chat_id=chat_id, text=msgETH)
            bot.sendMessage(chat_id=chat_id, text=msgKRW)
            time.sleep(15)

        if start_time + datetime.timedelta(seconds=15) < now < end_time - datetime.timedelta(seconds=30):
            if target_price < current_price:
                btcbuycall = 0
                if eth > ethfee :
                    btcbuycall = btcbuycall + 1]
                if krw > 5000 and btc < btcfee:
                    upbit.buy_market_order("KRW-BTC", krw / (2-btcbuycall) * 0.9995)
                    btc_state = 1
                time.sleep(0.2)
            if target_priceETH < current_priceETH:
                ethbuycall = 0
                if btc > btcfee :
                    ethbuycall = ethbuycall + 1
                if krw > 5000 and eth < ethfee:
                    upbit.buy_market_order("KRW-ETH", krw / (2-ethbuycall) * 0.9995)
                    eth_state = 1
                time.sleep(0.2)
            time.sleep(30)

        else:
            if btc_state == 1:
                upbit.sell_market_order("KRW-BTC", btc)
                btc_state = 0
                cpt = current_price / target_price * 100 - 100
                msg = "오늘의 BTC 수익률 = %.2f %%" % (cpt)
                bot.sendMessage(chat_id=chat_id, text=msg)
            if eth_state == 1:
                upbit.sell_market_order("KRW-ETH", eth)
                cpt = current_priceETH / target_priceETH * 100 - 100
                msg = "오늘의 ETH 수익률 = %.2f %%" % (cpt)
                eth_state = 0
                bot.sendMessage(chat_id=chat_id, text=msg)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
