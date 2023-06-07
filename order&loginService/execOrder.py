from datetime import datetime, time, timedelta
import random
from mongo import *
from order import placeBuyOrderMarketNSE, orderHistory, PlaceSellOrderMarketNSE, fakeOrder

# support = [43583,4000]
# resistance = [43682,44360]
expiry = "2023-06-01"
target = 15
stoppLoss = 2
client = ConnectDB()
db = client["algoTrading"]

start_time = datetime.strptime("11:00", "%H:%M").time()
end_time = datetime.strptime("13:22", "%H:%M").time()
firstFiveMinCounter = 0
# trend  "BULLISH", "BEARISH", "SIDEWAYS"
trend = "BULLISH"

def fetchData(data):

    print(data,'from fetch data')
    current_time = datetime.now().time()
    if start_time <= current_time <= end_time:
        print("startTime=",start_time,"currentTime",current_time,"endTime=",end_time)
        firstFiveMin(data,end_time,current_time)
    collection = db["levels"]
    levels = collection.find({"instrument_token" : data["instrument_token"],"status":{"$ne":"Closed"}})
    levels = list(levels)
    if data["instrument_token"] != 260105:
        checkTargetAndSL(data)
    if data['instrument_token'] == 260105:
        return checkCondition(data['last_price'], data['instrument_token'],levels)
    return False

support = list()
resistance = list()

def checkCondition(tradingprice,istToken,levels):

    
    print("check conditionssss for orders",levels)
    
    for lev in levels:
        # print(lev,"from for loopppppp")
        checkSupResStatus(lev,tradingprice)
        # Add tiem bound condition
        if (lev["levelDetails"]["type"] == "fiveMinRes" and tradingprice >lev["levelDetails"]["level"] and lev["status"] == "Active" and (trend == "BULLISH" or trend == "SIDEWAYS")):
            return placeOrder(tradingprice, istToken, "CE",lev)
        
        if (lev["levelDetails"]["type"] == "fiveMinSup" and tradingprice < lev["levelDetails"]["level"] and lev["status"] == "Active" and (trend == "BEARISH" or trend == "SIDEWAYS")):
            return placeOrder(tradingprice, istToken, "PE",lev)

        if (lev["levelDetails"]["type"] == "support") and lev["levelDetails"]["level"]<tradingprice<lev["levelDetails"]["level"]+200 and lev["status"] == "Active":
            return placeOrder(tradingprice, istToken, "CE",lev)
        
        if (lev["levelDetails"]["type"] == "testedSup" and lev["levelDetails"]["level"] + 25<=tradingprice<lev["levelDetails"]["level"] + 35 and lev["status"] == "Active"):
            return placeOrder(tradingprice, istToken, "CE",lev)
        
        if (lev["levelDetails"]["type"] == "testedRes" and lev["levelDetails"]["level"] - 35>=tradingprice>lev["levelDetails"]["level"] - 25 and lev["status"] == "Active"):
            return placeOrder(tradingprice, istToken, "PE",lev)
        
        if lev["levelDetails"]["type"] == "resistance" and lev["levelDetails"]["level"]-10<tradingprice<lev["levelDetails"]["level"]:
            return placeOrder(tradingprice, istToken, "PE",lev)
    
    print(support,'supportttttttt',resistance,'resistanceeeeeeeee')

    return

def checkSupResStatus(level, indexAt):
    print("checkSupResStatus function calllll",level,indexAt)
    current_time = datetime.now().time()
    lev = level["levelDetails"]["level"]
    collection = db["levels"]
    # change firstFiveMin to normal support after 25 min of starting the market
    if indexAt >= (lev + 35):
        res = collection.update_one(
            {
                "id": level["id"],
                "levelDetails.type": "support"
            },
            {
                "$set":{"status":"Active"}
            })
        
        re = collection.update_one(
            {
                "id": level["id"],
                "interchangable": True,
                "levelDetails.type": "resistance"
            },
            {
                "$set":{
                    "status":"Active",
                    "levelDetails.type": "support",
                    "levelDetails.interChanged": True
                }
            })
        
        print(res,"from checkSupResStatus",re)

    if indexAt <= (lev - 35):
        res = collection.update_one(
            {
                "id": level["id"],
                "interchangable": True,
                "levelDetails.type": "resistance"
            },
            {
                "$set":{"status":"Active"}
            })
        
        re = collection.update_one(
            {
                "id": level["id"],
                "interchangable": True,
                "levelDetails.type": "support"
            },
            {
                "$set":{
                    "status":"Active",
                    "levelDetails.type": "resistance",
                    "levelDetails.interChanged": True
                }
            })
    
    # val = level["lastTradeTime"]
    # print(val,"value of lastTradeTime")
    if "lastTradeTime" in level:
        targetTime = level["lastTradeTime"] + timedelta(minutes=3)
        print(targetTime,"from check supRes lastTradeTime")
        if current_time > targetTime and level["status"] == "Passive":
            collection.update_one(
            {
                "id":lev["id"]
            },
            {
                "$set":{"status":"Active"}
            })
    tradeResult = level["tradeResults"]
    if level["levelDetails"]["testCount"] >= 3 and tradeResult[len(tradeResult)-1]["result"] == "Loss":
        collection.update_one(
            {
                "id":lev["id"]
            },
            {
                "$set":{"status":"Closed"}
            })
    # change support to active after level reached sup + 10 to active and place order at sup + 20
    if tradeResult[len(tradeResult)-1]["result"] == "Loss" and lev < indexAt  <= lev + 10 :
        collection.update_one(
            {
                "id":lev["id"],
                "levelDetails.type": "support"
            },
            {
                "$set":{
                    "status": "Active",
                    "levelDetails.type": "testedSup"
                }
            })
    if tradeResult[len(tradeResult)-1]["result"] == "Loss" and lev - 10 > indexAt  >= lev :
        collection.update_one(
            {
                "id":lev["id"],
                "levelDetails.type": "resistance"
            },
            {
                "$set":{
                    "status": "Active",
                    "levelDetails.type": "testedRes"
                }
            })
    if tradeResult[len(tradeResult)-1]["result"] == "Profit" and level["levelDetails"]["type"] == "testedRes":
        collection.update_one(
            {
                "id":lev["id"],
                "levelDetails.type": "testedRes"
            },
            {
                "$set":{
                    "status": "Active",
                    "levelDetails.type": "resistance"
                }
            })
        collection.update_one(
            {
                "id":lev["id"],
                "levelDetails.type": "testedSup"
            },
            {
                "$set":{
                    "status": "Active",
                    "levelDetails.type": "support"
                }
            })
    conditionTime = datetime.strptime("9:45", "%H:%M").time()
    if current_time > conditionTime and (trend == "SIDEWAYS" or trend == "BULLISH") and (level["levelDetails"]["type"] == "fiveMinRes" or level["levelDetails"]["type"] == "fiveMinSup") and indexAt >= (lev + 15):
       
        collection.update_one(
            {
                "id":lev["id"],
            },
            {
                "$set":{
                    "status": "Active",
                    "levelDetails.type": "support"
                }
            })
    
    if current_time > conditionTime and (trend == "SIDEWAYS" or trend == "BEARISH") and (level["levelDetails"]["type"] == "fiveMinRes" or level["levelDetails"]["type"] == "fiveMinSup") and indexAt <= (lev - 15):
       
        collection.update_one(
            {
                "id":lev["id"],
            },
            {
                "$set":{
                    "status": "Active",
                    "levelDetails.type": "resistance"
                }
            })
        # trend == "BULLISH" indexAt <= (lev - 15)
    
    if current_time > conditionTime and (trend == "BULLISH") and (level["levelDetails"]["type"] == "fiveMinRes" or level["levelDetails"]["type"] == "fiveMinSup") and indexAt <= (lev - 15):
       
        collection.update_one(
            {
                "id":lev["id"],
            },
            {
                "$set":{
                    "status": "Passive",
                    "levelDetails.type": "support"
                }
            })
        
    if current_time > conditionTime and (trend == "BEARISH") and (level["levelDetails"]["type"] == "fiveMinRes" or level["levelDetails"]["type"] == "fiveMinSup") and indexAt >= (lev + 15):
       
        collection.update_one(
            {
                "id":lev["id"],
            },
            {
                "$set":{
                    "status": "Passive",
                    "levelDetails.type": "resistance"
                }
            })
    
    return

def placeOrder(price, token,type,level):
    print("place order called>>>>>")

    # collection = db["orders"]
    # status = collection.find_one({"indexName" : "BANKNIFTY","status":"Active"},{"status":1,"_id":0})
    # print(status,'statussssssss From order placed')
    # below not is to handle syntax and not condition
    # if status == None :
    print("from status == None")
    strike = selectStrike(token,price,type)
    # orderId = placeBuyOrderMarketNSE("YESBANK",1)
    # orderData = orderHistory(orderId)
    orderId  = random.randint(10000,99999)
    orderData = fakeOrder(price)
    orderTime = orderData[len(orderData)-1]['order_timestamp']
    purchasePrice = orderData[len(orderData)-1]['average_price']
    sl = purchasePrice - (purchasePrice * stoppLoss)/100
    tar = purchasePrice + (purchasePrice * target)/100
    obj = { 
        # "orderId":orderId,
        "orderId": orderId,
        "instrument_token": strike[2],
        "parent_instrument_token": token,
        "indexAt": price,
        "strike": strike[0],
        "indexName": strike[1],
        "price": orderData[len(orderData)-1]['average_price'],
        "executedAt": orderTime,
        "levelId": level["id"],
        "levelStatus": level["status"],
        "levelType": level["levelDetails.type"],
        "stopLoss": sl,
        "target": tar,
        "status": "Active"
    }
    print(obj,'objjjjj from order',strike)
    collection.insert_one(obj)
    collection = db["levels"]
    collection.update_one(
        {
            "id": level["id"]
        },
        {
            "$set" :{
                "status": "Intrade",
            },
            "$push":{
                "tradeResults":{"orderId":orderId}
            },
            "$inc": {"levelDetails.testCount": 1}
        })
    # print('after obj inserted in order collection')
    return strike[2]
    # else: 
    #     print("status from else",status)

def checkTargetAndSL(data):
    print(data,'from checkTarget and sl')
    orderCollection = db["orders"]
    result = orderCollection.find(
        {
            "parent_instrument_token" : 260105,
            "status":{"$in":["Active","trailingSL"]}
            }
        )
    # print(result)
    result = list(result)
    print(result,'resultttttttt')
    if(len(result)> 1):
        print("PANIC SOMETHING HAS GONE WRONG CLOSE ALL TRADES")
    if(len(result) == 1):
        stpLss = result[0]["stopLoss"]
        target = result[0]["target"]
        purchasePrice = result[0]["price"]
        currentPrice = data["last_price"]
        print("purchase price=",purchasePrice,"current price=", data["last_price"],"stpLss=",stpLss)
        # Add LOGIC IF IT STAYS AT LEAST AFTER 3 MINS
        if(purchasePrice <= currentPrice):
            print("TRAIL stpLss HERE TILL PURCHASE PRICE")
            orderCollection.update_one(
                {
                    "indexName" : "BANKNIFTY",
                    "status": "Active"
                },
                {
                    "$set":{"stopLoss":purchasePrice},
                    "status":"trailingSL"
                })
        if (stpLss >= data["last_price"] or target <= data["last_price"]):
            print("EXECUTE SELL ORDER")
            # orderId = PlaceSellOrderMarketNSE("YESBANK",1)
            orderId = random.randint(10000,99999)
            # orderData = orderHistory(orderId)
            orderData = fakeOrder(data["last_price"])
            orderTime = orderData[len(orderData)-1]['order_timestamp']
            sellPrice = orderData[len(orderData)-1]['average_price']
            trade = ((purchasePrice - sellPrice)/purchasePrice)*100
            tradeResult = ""
            if purchasePrice >= sellPrice:
                tradeResult = "Loss"
            else:
                tradeResult = "Profit"

            obj = {
                "orderId": orderId,
                "instrument_token": data["instrument_token"],
                "qty": 1,
                "price": sellPrice,
                "executedAt": orderTime,
                "status": "Closed"
            }
            orderCollection.update_one({
                "indexName" : "BANKNIFTY"
            }, {
                "$set": {
                    "sellOrder": obj,
                    "tradeResult": tradeResult,
                    "pecentageBooked": trade,
                    "status": "Closed",
                    }
            })
            # update support resistance table
            status = "Active"
            if tradeResult == "Loss":
                status = "Passive"

            levelCollection = db["levels"]
            levelCollection.update_one(
                {
                    "tradeResults":{"$eleMatch":{"orderId":orderId}},
                },
                {
                    "$set":{
                        "status": status,
                        "lastTradeTime": orderTime,
                        "tradeResults.$.result": tradeResult
                    }
                },
                {
                    "$inc":{"levelDetails.testCount":1}
                })
        print(stpLss, target,'sl and targettttttttt')
    return



def myFunc(e):
    return e['last_price']
def firstFiveMin(data,endT,curT):
    print('from first five min',data)
    collectionName = db["firstFiveMinData"]
    collectionName.insert_one(data)
    time_diff = datetime.combine(datetime.min, endT) - datetime.combine(datetime.min, curT)
    time_diff_sec = time_diff.total_seconds()
    print(time_diff,"time diffranceeeeeee")
    collectionName = db["levels"]
    countFiveMinSupport = collectionName.count_documents({"levelDetails.type":{"$in":["fiveMinSup","fiveMinRes"]}})
    print(countFiveMinSupport,"count from first five min")
    if countFiveMinSupport > 0:
        return
    if(time_diff_sec<= 5 and countFiveMinSupport == 0): 
        print("from if in first five min")
        collectionName = db["firstFiveMinData"]
        val = collectionName.find({"instrument_token" : 260105},{"last_price":1,"_id":0})
        val = list(val)
        # print(val,'')
        val.sort(key=myFunc)
        # print(val)
        lowerVal = val[0]
        upperVal = val[len(val)-1]
        collection = db["levels"]
        count = collection.count_documents({})
        print(count,"count Documents level")
        obj = [{
            "id": "Level-0"+str(count+1),
            "name" : "NIFTY BANK",
            "tradingsymbol" : "NIFTY BANK",
            "interchangable" : False,
            "status" : "Active",
            "instrument_token" : 260105,
            "levelDetails" : {
            "level" : lowerVal["last_price"],
            "type" : "fiveMinSup",
            "testCount" : 0,
            "interChanged" : False
            },
        },
        {
            "id": "Level-0"+str(count+2),
            "name" : "NIFTY BANK",
            "tradingsymbol" : "NIFTY BANK",
            "interchangable" : False,
            "status" : "Active",
            "instrument_token" : 260105,
            "levelDetails" : {
            "level" : upperVal["last_price"],
            "type" : "fiveMinRes",
            "testCount" : 0,
            "interChanged" : False
            }
        }]
        # now save in support and resistance table
        print(obj,"objecttttttt")
        collection = db["levels"]
        res = collection.insert_many(obj)
        print(res, "result from insert data")
        filterObj = {
                "levelDetails.type":"resistance",
                "levelDetails.level":{"$gt":upperVal["last_price"]}
            }
        print(filterObj,'filterObj resistance')
        re = collection.update_many(
            filterObj,
            {
                "$set":{"status":"Active"}
            })
        
        print(re,'resultttt from first five min update resistance')
        filterObj = {
                "levelDetails.type":"support",
                "levelDetails.level":{"$lt":lowerVal["last_price"]}
            }
        re = collection.update_many(
                filterObj,
            {
                "$set":{"status":"Active"}
            })
        print(filterObj,"filterObj support")
        
    return

def selectStrikePrice(ltp):
        
    str = (ltp / 100)
    sel = (ltp % 100)
    str = int(str)
    if sel > 50:
        str = str + 1
    str = (str * 100)
    return str


def selectStrike(instrument_token, ltp, type):
    if instrument_token == 260105:
        name = "BANKNIFTY"
        strike = selectStrikePrice(ltp)
        collection = db["instrumentNFO"]
        query = {
            "name": name,
            "strike": strike,
            "instrument_type": type,
            "expiry": expiry
        }
        projection = {
            "instrument_token": 1,
            "tradingsymbol": 1,
            "_id": 0
        }
        # print(query)
        result = collection.find_one(query, projection)
        symbol = result["tradingsymbol"]
        strikeToken = result["instrument_token"]
        return (symbol,name,strikeToken)


# selectStrikePrice(40720)
