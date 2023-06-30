from kiteconnect import KiteTicker
import datetime
from mongo import *
from execOrder import *

client = ConnectDB()
db = client['algoTrading']
collection = db["userDetails"]
tokens = [260105,256265,257801]
user = collection.find_one({"name" : "SIDDHARTH LAHOTY"})
# kws = KiteTicker(apiKey, accToken)
kws = KiteTicker(user["apikey"],user["acc_token"])
# counter = 0
def on_ticks(ws, ticks,counter = 0):
    
    tokens = [260105,256265,257801]
    print("on tick called")
    orderCollection = db["orders"]
    activeStike = orderCollection.find({"status":{"$in":["Active","trailingSL"]}},{"instrument_token":1,"_id":0})
    activeStikeList = list(activeStike)
    for strike in activeStikeList:
        if strike["instrument_token"] not in tokens:
            tokens.insert(len(tokens),strike["instrument_token"])
    
    inactiveStrike = orderCollection.find({"status":"Closed"},{"instrument_token":1,"_id":0})
    inactiveStrike = list(inactiveStrike)
    # print(inactiveStrike,"inactive strikeeeeee")
    str = list()
    for strike in inactiveStrike:
        str.insert(0,strike["instrument_token"])
    # print(str,"strrrrrrr")
    kws.unsubscribe(str)
    # print(tokens,"tokenssssss")

    kws.subscribe(tokens)
    kws.set_mode(kws.MODE_LTP,tokens)
    
    for scripdata in ticks:

        listScript = []
        listScript.insert(0,scripdata)
        isorderPlaced = fetchData(scripdata)

        # print(isorderPlaced,'is order placed',len(tokens),tokens)
        
        
        

def on_connect(ws, response): 
    
   
    print(tokens,"strikessssss")
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_LTP, tokens)
   

kws.on_ticks = on_ticks
kws.on_connect = on_connect

kws.connect()

# def on_close(ws, code, reason):
#     pass

# def on_error(ws, code, reason):
#     print("closed connection on error: {} {}".format(code, reason))


# def on_noreconnect(ws):
#     print("Reconnecting the websocket failed")


# def on_reconnect(ws, attempt_count):
#     print("Reconnecting the websocket: {}".format(attempt_count))

# def on_order_update(ws, data):
#     print("order update: ", data)



# kws.on_close = on_close
# kws.on_error = on_error
# kws.on_noreconnect = on_noreconnect
# kws.on_reconnect = on_reconnect
# kws.on_order_update = on_order_update

