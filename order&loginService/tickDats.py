from kiteconnect import KiteTicker
import datetime
from mongo import *
from execOrder import *

# accToken = 'U5NGn6cMfpgqrGr2RC0831YfVXLHzBln'
# apiKey = 'k55bdfkr27eqguv6'
# Temprory adding strike data for sl target function as of now tick data is being automatically being added for strike  3050241
# tokens = [260105]
# kws = KiteTicker(apiKey, accToken)
client = ConnectDB()
db = client['algoTrading']
collection = db["userDetails"]
tokens = [260105]
user = collection.find_one({"name" : "SIDDHARTH LAHOTY"})
# kws = KiteTicker(apiKey, accToken)
kws = KiteTicker(user["apikey"],user["acc_token"])
# counter = 0
def on_ticks(ws, ticks,counter = 0):
    tokens = [260105]
    print("on tick called")
    orderCollection = db["orders"]
    activeStike = orderCollection.find({"status":{"$in":["Active","trailingSL"]}},{"instrument_token":1,"_id":0})
    activeStikeList = list(activeStike)
    print(activeStikeList,"activeStrikeList")
    strikeArr = []
    for strike in activeStikeList:
        if strike["instrument_token"] not in tokens:
            tokens.insert(len(tokens),strike["instrument_token"])
    # CurrentDateTime = datetime.datet
    # CurrentTime = datetime.time(CurrentDateTime.hour, CurrentDateTime.minute, CurrentDateTime.second)
    # endtime = datetime.time(14, 23, 0)
    # if CurrentTime > endtime: 
    #     kws.stop()
    #     kws.unsubscribe(tokens)
    #     kws.close()
        # raise SystemExit
    print(tokens,"tokenssssss")
    kws.subscribe(tokens)
    kws.set_mode(kws.MODE_LTP,tokens)
    for scripdata in ticks:
       
       
        print(scripdata, scripdata['last_price'])
        
        listScript = []
        listScript.insert(0,scripdata)
        print(tokens,'beofr iffffffffff')
        print(scripdata)
        isorderPlaced = fetchData(scripdata)
        # print(isorderPlaced,"isOrderPlaceddddd")
        print(isorderPlaced,'is order placed',len(tokens),tokens)
        # and condition is temprory removve it after including time condition
        # if(isorderPlaced != False and len(tokens) == 1 and isorderPlaced != None):
        #     print('hiii if condition satisfied')
        #     tokens.append(isorderPlaced)
        #     print(tokens,'inside ifffffffffffff')
        #     kws.subscribe(tokens)
        #     kws.set_mode(kws.MODE_LTP,tokens)
        
        

def on_connect(ws, response): 
    
    # print("on connect called") 
    print(tokens,"strikessssss")
    ws.subscribe(tokens)
    #ws.set_mode(ws.MODE_FULL, tokens)
    ws.set_mode(ws.MODE_LTP, tokens)
    # ws.set_mode(ws.MODE_QUOTE, [tokens[1]])    
    # ws.set_mode(ws.MODE_FULL, [tokens[2]])



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

kws.on_ticks = on_ticks
kws.on_connect = on_connect

# kws.on_close = on_close
# kws.on_error = on_error
# kws.on_noreconnect = on_noreconnect
# kws.on_reconnect = on_reconnect
# kws.on_order_update = on_order_update

kws.connect()