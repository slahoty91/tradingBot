from datetime import datetime
import os
from kiteconnect import KiteConnect
import mongo

client = mongo.ConnectDB()
db = client["algoTrading"]
collection = db["userDetails"]

users = collection.find_one({"name" : "SIDDHARTH LAHOTY"},{"_id":0,"apikey":1,"acc_token":1})
print(users,"from ordersssssss")
# pw = os.chdir("/Users/siddharthlahoty/Desktop/AlogoTrading/order&loginService/acc_auth")
# acc_token_path = "access_token.txt"
# acc_token = open(acc_token_path,'r').read().split()
kite = KiteConnect(users["apikey"])
data = kite.set_access_token(users["acc_token"])

def placeBuyOrderMarketNSE(tradingsymbol, qty):

    try:
        orderid = kite.place_order(variety=kite.VARIETY_REGULAR,
                                tradingsymbol=tradingsymbol,
                                exchange=kite.EXCHANGE_NSE,
                                transaction_type=kite.TRANSACTION_TYPE_BUY,
                                quantity=qty,
                                order_type=kite.ORDER_TYPE_MARKET,
                                product=kite.PRODUCT_CNC,
                                validity=kite.VALIDITY_DAY
                                )
    except Exception as e:
        print("Order placement failed: {}".format(e))
    return orderid

# PlaceBuyOrderMarketNSE("SBIN",1)

def fakeOrder(price,strike):
    obj = [{
	
        "order_timestamp" : datetime.now(),
        "average_price" : price,
        "strike": strike
    }]
    return obj

def PlaceSellOrderMarketNSE(tradingsymbol, qty):
    print("Sell order caled")
    orderid = 1
    try:
        orderid = kite.place_order(variety=kite.VARIETY_REGULAR,
                                   tradingsymbol=tradingsymbol,
                                   exchange=kite.EXCHANGE_NSE,
                                   transaction_type=kite.TRANSACTION_TYPE_SELL,
                                   quantity=qty,
                                   order_type=kite.ORDER_TYPE_MARKET,
                                   product=kite.PRODUCT_CNC,
                                   validity=kite.VALIDITY_DAY
                                   )
    except Exception as e:
        print("Order placement failed:{}".format(e))
    return orderid

# order = PlaceSellOrderMarketNSE("SBIN",1)
# print(order)

# PLACE NFO ORDER 
def PlaceBuyOrderMarketNFO(tradingsymbol, qty):
    print(kite.VARIETY_REGULAR)
    orderid = 1
    try:
        orderid = kite.place_order(variety=kite.VARIETY_REGULAR,
                                tradingsymbol=tradingsymbol,
                                exchange=kite.EXCHANGE_NFO,
                                transaction_type=kite.TRANSACTION_TYPE_BUY,
                                quantity=qty,
                                order_type=kite.ORDER_TYPE_MARKET,
                                product=kite.PRODUCT_NRML,
                                validity=kite.VALIDITY_DAY
                                )
    except Exception as e:
        print("Order placement failed: {}".format(e))
    return orderid
# BANKNIFTY23MAY43700CE
# PlaceBuyOrderMarketNFO("BANKNIFTY23MAY43700CE",25)

def PlaceSellOrderMarketNFO(tradingsymbol, qty):
    print("Sell order caled")
    orderid = 1
    try:
        orderid = kite.place_order(variety=kite.VARIETY_REGULAR,
                                   tradingsymbol=tradingsymbol,
                                   exchange=kite.EXCHANGE_NFO,
                                   transaction_type=kite.TRANSACTION_TYPE_SELL,
                                   quantity=qty,
                                   order_type=kite.ORDER_TYPE_MARKET,
                                   product=kite.PRODUCT_NRML,
                                   validity=kite.VALIDITY_DAY
                                   )
    except Exception as e:
        print("Order placement failed:{}".format(e))
    return orderid

def orderHistory(orderId):
    try:

        orderData = kite.order_history(orderId)
        return orderData
    except Exception as e:
        print("Order history failed{}".format(e))

# ord = orderHistory(230703500203518)
# print("order history",len(ord),ord[len(ord)-1])
# print(ord[4],'orddddddd',len(ord))
# time = ord[4]['order_timestamp']
# print(time)
# print(time.strftime("%Y-%m-%d %H:%M:%S"),datetime.now())
# for h in his:
#     print(h['order_timestamp'])
# PlaceSellOrderMarketNFO("BANKNIFTY23MAY43700CE",25)
