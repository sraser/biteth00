import time
import pyupbit
import telegram

access = ""
secret = ""
bot = telegram.Bot(token='')
chat_id =

inter = "minute240"
def get_ma(ticker):
    dfma = pyupbit.get_ohlcv(ticker, interval=inter, count=22, period=1)
    ma5 = dfma['close'].rolling(5).mean().iloc[-1]
    ma20 = dfma['close'].rolling(20).mean().iloc[-1]
    ma5p = dfma['close'].rolling(5).mean().iloc[-2]
    ma20p = dfma['close'].rolling(20).mean().iloc[-2]
    return ma5, ma20, ma5p, ma20p

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

upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

btc_state = 0
eth_state = 0
btc_buy_price = 0
btc_sell_price = 0
eth_buy_price = 0
eth_sell_price = 0

btc_ini = get_balance("BTC")
eth_ini = get_balance("ETH")
time.sleep(0.2)
btcma5, btcma20, btcma5p, btcma20p = get_ma("KRW-BTC")
time.sleep(0.2)
ethma5, ethma20, ethma5p, ethma20p = get_ma("KRW-ETH")
bot.sendMessage(chat_id=chat_id, text="재접속")
if btc_ini != 0 :
    btc_state = 1
    btc_buy_price = btc_ini
if eth_ini != 0 :
    eth_state = 1
    eth_buy_price = eth_ini
if btcma5 >= btcma20 and btc_state == 0:
    btc_state = 1
if ethma5 >= ethma20 and btc_state == 0:
    eth_state = 1



while True:
    try:
        current_priceBTC = get_current_price("KRW-BTC")
        btcfee = 5000 / current_priceBTC
        btc = get_balance("BTC")
        btcma5, btcma20, btcma5p, btcma20p = get_ma("KRW-BTC")
        time.sleep(0.1)

        current_priceETH = get_current_price("KRW-ETH")
        ethfee = 5000 / current_priceETH
        eth = get_balance("ETH")
        ethma5, ethma20, ethma5p, ethma20p = get_ma("KRW-ETH")
        time.sleep(0.1)

        krw = get_balance("KRW")

        if btcma5 >= btcma20 and btcma5p < btcma20p and btc_state == 0:
            btcbuycall = 0
            if eth > ethfee :
                btcbuycall = btcbuycall + 1
            if krw > 5000 and btc < btcfee:
                upbit.buy_market_order("KRW-BTC", krw / (2-btcbuycall) * 0.9995)
                btc_buy_price = current_priceBTC
                btc_state = 1
                msg = "BTC 매수 = %.2f" % (btc_buy_price)
                bot.sendMessage(chat_id=chat_id, text=msg)
            time.sleep(0.2)

        if ethma5 >= ethma20 and ethma5p < ethma20p and eth_state == 0:
            ethbuycall = 0
            if btc > btcfee :
                ethbuycall = ethbuycall + 1
            if krw > 5000 and eth < ethfee:
                upbit.buy_market_order("KRW-ETH", krw / (2-ethbuycall) * 0.9995)
                eth_buy_price = current_priceETH
                eth_state = 1
                msg = "ETH 매수 = %.2f" % (eth_buy_price)
                bot.sendMessage(chat_id=chat_id, text=msg)
            time.sleep(0.2)

        if btcma5 <= btcma20 and btcma5p > btcma20p and btc_state == 1:
            upbit.sell_market_order("KRW-BTC", btc)
            btc_state = 0
            btc_sell_price = current_priceBTC
            cpt = (btc_buy_price - btc_sell_price) / btc_buy_price + 1
            msg = "BTC 매도 %.2f , 수익률 = %.2f %%" % (btc_sell_price, cpt)
            bot.sendMessage(chat_id=chat_id, text=msg)

        if ethma5 <= ethma20 and ethma5p > ethma20p and eth_state == 1:
            upbit.sell_market_order("KRW-ETH", eth)
            eth_sell_price = current_priceETH
            cpt = (eth_buy_price - eth_sell_price) / eth_buy_price + 1
            msg = "BTC 매도 %.2f , 수익률 = %.2f %%" % (eth_sell_price, cpt)
            eth_state = 0
            bot.sendMessage(chat_id=chat_id, text=msg)
        time.sleep(60)

    except Exception as e:
        print(e)
        time.sleep(1)
