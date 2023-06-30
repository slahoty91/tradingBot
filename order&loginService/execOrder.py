from datetime import datetime, time, timedelta
import random
from mongo import *
from order import PlaceBuyOrderMarketNFO, orderHistory, PlaceSellOrderMarketNFO, fakeOrder
from sendTelegramMsg import SendMsg



target = 10
stoppLoss = 5
lot = 1
riskToReward = 2


client = ConnectDB()
db = client["algoTrading"]

curTime = datetime
start_time = datetime.strptime("9:15:2", "%H:%M:%S").time()
end_time = datetime.strptime("9:20", "%H:%M").time()
firstFiveMinCounter = 0
# trend  "BULLISH", "BEARISH", "SIDEWAYS"
trend = "SIDEWAYS"
testing = True
# Index tokens
indexTokens = [260105,256265,257801]
firstFiveMinTrade = False


def fetchData(data):
    print("From fetch data",data)
    current_time = datetime.now().time()
    if start_time <= current_time <= end_time:
        firstFiveMin(data,end_time,current_time)
    if current_time > end_time:
        collection = db["levels"]
        levels = collection.find({"instrument_token" : data["instrument_token"],"status":{"$ne":"Closed"}})
        levels = list(levels)

        if data['instrument_token'] in indexTokens :
            return checkCondition(data['last_price'], data['instrument_token'],levels)

        if data["instrument_token"] not in indexTokens:
            
            if testing == True:
                updateSlTarForTesting(data)
            return checkTargetAndSL(data)
            
        
    return False

def updateSlTarForTesting(data):
    
    ordersCollection = db["orders"]
    # ordersCollection.find_one({"instrument_token" : instToken},{})
    curPrice = data["last_price"]
    stloss = (curPrice - (curPrice * stoppLoss)/100)
    tar = (curPrice + (curPrice * target)/100)
    if data["last_price"] < 100:
        risk = 6
        stloss = curPrice - risk
        tar = curPrice + risk*riskToReward
    res = ordersCollection.update_one(
        {
            "instrument_token" : data["instrument_token"],
            "updateForTesing":{"$exists": False},
            "status": "Active"
        },
        {"$set":{
            "stopLoss": stloss,
            "target": tar,
            "price": curPrice,
            "updateForTesing": True
        }}
    )
    order = ordersCollection.find_one(
        {
            "instrument_token" : data["instrument_token"],
            "status": "Active"
        },
        {
            "indexName": 1,
            "indexAt":1,
            "_id":0
        }
    )

    if res.modified_count>0:
        msg = "Testing order placed, price "+ str(curPrice) + " sl of "+ str(stloss) + " and target of "+ str(tar) + " for " + order["indexName"] +" "+ str(order["indexAt"])
        SendMsg(msg)
    return

def checkCondition(tradingprice,istToken,levels):

    current_time = datetime.now().time()
    conditionTime = datetime.strptime("9:30", "%H:%M").time()
    startSwing = datetime.strptime("9:30", "%H:%M").time()
    exitTime = datetime.strptime("15:20","%H:%M").time()
    
    for lev in levels:
        checkSupResStatus(lev,tradingprice)
        # Add tiem bound condition
        # print(lev,"levvvvvvvv")
        # return
        if lev["name"] == "NIFTY 50" or lev["name"] == "NIFTY FIN SERVICE":
            entryCE =  lev["levelDetails"]["level"]+5
            entryPE =  lev["levelDetails"]["level"]-5
        
        if lev["name"] == "NIFTY BANK":
            entryCE =  lev["levelDetails"]["level"]+10
            entryPE =  lev["levelDetails"]["level"]-10
        if current_time <= conditionTime and firstFiveMinTrade == True:

            if (lev["levelDetails"]["type"] == "fiveMinRes" and tradingprice + 10 >lev["levelDetails"]["level"] and lev["status"] == "Active") and trend != "BEARISH":
                return placeOrder(tradingprice, istToken, "CE",lev)
            
            if (lev["levelDetails"]["type"] == "fiveMinSup" and tradingprice - 10 < lev["levelDetails"]["level"] and lev["status"] == "Active") and trend != "BULLISH":
                return placeOrder(tradingprice, istToken, "PE",lev)

        if current_time >= startSwing:
           
            if (lev["levelDetails"]["type"] == "support") and lev["levelDetails"]["level"]<tradingprice<entryCE and lev["status"] == "Active":
                return placeOrder(tradingprice, istToken, "CE",lev)
            
            if lev["levelDetails"]["type"] == "resistance" and entryPE<tradingprice<lev["levelDetails"]["level"] and lev["status"] == "Active":
                return placeOrder(tradingprice, istToken, "PE",lev)
            
               
            # if (lev["levelDetails"]["type"] == "testedSup" and lev["levelDetails"]["level"] + 25<=tradingprice<lev["levelDetails"]["level"] + 35 and lev["status"] == "Active"):
            #     return placeOrder(tradingprice, istToken, "CE",lev)
            
            # if (lev["levelDetails"]["type"] == "testedRes" and lev["levelDetails"]["level"] - 35>=tradingprice>lev["levelDetails"]["level"] - 25 and lev["status"] == "Active"):
            #     return placeOrder(tradingprice, istToken, "PE",lev)

        # if current_time > exitTime:
        #     return exitOrder()

    return False

def placeOrder(price, token,type,level):
  
    collection = db["orders"]
    status = collection.find_one({
        "parent_instrument_token" : token,
        "status":{
            "$in":["Active","trailingSL"]
        }},
        {
            "status":1,"_id":0
        })
    # for now do one trade at a time
    print(status,"statuss from place order")
    if status == None :

        strike = selectStrike(token,price,type)
        if testing == False:
            orderId = PlaceBuyOrderMarketNFO(strike[0],strike[3])
            orderData = orderHistory(orderId)
        else:
            orderId  = random.randint(10000,99999)
            orderData = fakeOrder(price,strike[0])
        orderTime = orderData[len(orderData)-1]['order_timestamp'].strftime("%H:%M:%S.%f") 
        purchasePrice = orderData[len(orderData)-1]['average_price']
        sl = purchasePrice - (purchasePrice * stoppLoss)/100
        tar = purchasePrice + (purchasePrice * target)/100

        count = collection.count_documents({})
        print(count,"from count documentssss")


        obj = { 
            # "orderId":orderId,
            "sno": (count + 1),
            "orderId": str(orderId),
            "instrument_token": strike[2],
            "type": type,
            "parent_instrument_token": token,
            "indexAt": price,
            "strike": strike[0],
            "indexName": strike[1],
            "price": orderData[len(orderData)-1]['average_price'],
            "executedAt": orderTime,
            "levelId": level["id"],
            "levelStatus": level["status"],
            "levelType": level["levelDetails"]["type"],
            "stopLoss": sl,
            "target": tar,
            "status": "Active"
        }
        orderCollection = db["orders"]
        orderCollection.insert_one(obj)
        orderMasterTable = db["ordersMasterTable"]
        res = orderMasterTable.update_one({},{
            "$set":{"orderCount":{"$inc":1}}
        },True)
        levevCollection = db["levels"]
        levevCollection.update_one(
            {
                "id": level["id"]
            },
            {
                "$set" :{
                    "status": "Intrade",
                },
                "$push":{
                    "tradeResults":{
                        "orderId":str(orderId),
                        "result": "NA"
                        }
                },
                "$inc": {"levelDetails.testCount": 1}
            })
        # Don't forget to update after introducing real money
        if testing == False:
            msg = "Order placed " + str(orderId) + " is placed at "+ str(price)+ " with strike,"+ str(strike[0]) + " and purchase price "+ str(purchasePrice) +" stoploss "+ str(sl) +" target "+ str(tar)
            SendMsg(msg)

        return strike[2]
    
    return False

def checkTargetAndSL(data):

    orderCollection = db["orders"]
    result = orderCollection.find(
        {
            "instrument_token" : data["instrument_token"],
            "status":{"$in":["Active","trailingSL"]}
            }
        )
    result = list(result)
    print(data,'from checkTarget and sl',len(result))
    if(len(result) == 1):
        stpLss = result[0]["stopLoss"]
        target = result[0]["target"]
        purchasePrice = result[0]["price"]
        currentPrice = data["last_price"]
        trailsSLtrigger = purchasePrice + (purchasePrice*5/100)
        trailSL = purchasePrice + (purchasePrice*1/100)
        # WORKING WITH 1:2 RR
        # if(trailsSLtrigger <= currentPrice):
        #     resultOrder = orderCollection.update_one(
        #         {
        #             "instrument_token" : data["instrument_token"],
        #             "status": "Active"
        #         },
        #         {
        #             "$set":{
        #                 "stopLoss":trailSL,
        #                 "stopLossTrailed":True,
        #                 "trailsSLtrigger":trailsSLtrigger,
        #                 "status":"trailingSL"
        #                 },
                    
        #         })
        #     if resultOrder.modified_count >0:
        #         msg = "SL Updated with for oreder id " + str(result[0]["orderId"])
        #         SendMsg(msg)
        # print(target,data["last_price"],stpLss,"from checkTarget and sl")
        if (stpLss >= data["last_price"] or target <= data["last_price"]):
            print("sell order called")
            if testing == True:
                orderId = random.randint(10000,99999)
                orderData = fakeOrder(data["last_price"],result[0]["strike"])
            # orderData = orderHistory(orderId)
            else:
                orderId = PlaceSellOrderMarketNFO(result[0]["strike"])
                orderData = orderHistory(orderId)
            orderTime = orderData[len(orderData)-1]['order_timestamp'].strftime("%H:%M:%S.%f")
            sellPrice = orderData[len(orderData)-1]['average_price']
            trade = -purchasePrice + sellPrice
            tradeResult = ""
            if purchasePrice >= sellPrice:
                tradeResult = "Loss"
            else:
                tradeResult = "Profit"

            obj = {
                "orderId": str(orderId),
                "instrument_token": data["instrument_token"],
                "qty": 1,
                "price": sellPrice,
                "executedAt": orderTime,
                "status": "Closed"
            }
            # order = orderCollection.find_one({})
            orderRes = orderCollection.update_one({
                "instrument_token": data["instrument_token"],
                "status": {"$in":["Active","trailingSL"]}
            }, {
                "$set": {
                    "sellOrder": obj,
                    "tradeResult": tradeResult,
                    "bookedAmount": trade,
                    "status": "Closed",
                    }
            })
           
            # update support resistance table
            print("just before level update")
            status = "Passive"
            # if tradeResult == "Loss":
            #     status = "Passive"

            levelCollection = db["levels"]
            filterObj = {
                "tradeResults": {
                    "$elemMatch":{"orderId":result[0]["orderId"]}
                }
                }
            updateObj = {
                    "$set":{
                        "status": status,
                        "lastTradeTime": orderTime,
                        "tradeResults.$.result": tradeResult
                    },
                    "$inc":{"levelDetails.testCount":1}
                }
            print(filterObj,updateObj,"filter and update objectssss")
            levelRes = levelCollection.update_one(
                filterObj,
                updateObj
                )
            print(levelRes.acknowledged,levelRes.matched_count,levelRes.matched_count,"level res")
            # Send msg for trade closing
            
            if orderRes.acknowledged:
                msg = "Trade closed with order id "+str(orderId)+", trade result as " + tradeResult + " and booked amout as " + str(trade)
                
                SendMsg(msg)
            
            return (data["instrument_token"],"SELL ORDER")
            
    return False



def myFunc(e):
    return e['last_price']
def firstFiveMin(data,endT,curT):
    collectionName = db["firstFiveMinData"]
    collectionName.insert_one(data)
    time_diff = datetime.combine(datetime.min, endT) - datetime.combine(datetime.min, curT)
    time_diff_sec = time_diff.total_seconds()
    collectionName = db["levels"]
    countFiveMinSupport = collectionName.count_documents({
        "status":{"$ne":"Closed"},
        "levelDetails.type":{"$in":["fiveMinSup","fiveMinRes"]}
        })
    if countFiveMinSupport > 0:
        return
    if(time_diff_sec<= 3 and countFiveMinSupport == 0): 
       for token in indexTokens:
        getFiveMinLevels(token)
        
    return

def getFiveMinLevels(token):

    collectionName = db["firstFiveMinData"]
    val = collectionName.find({"instrument_token" : token},{"last_price":1,"_id":0})
    val = list(val)
    val.sort(key=myFunc)
    lowerVal = val[0]
    upperVal = val[len(val)-1]
    collection = db["levels"]
    count = collection.count_documents({})
    indCollection = db["instrumentNSE"]
    instData = indCollection.find_one(
        {
            "instrument_token": token},
            {"_id":0, "name": 1}
        )

    obj = [{
        "id": "Level-0"+str(count+1),
        "name" : instData["name"],
        "tradingsymbol" : instData["name"],
        "interchangable" : False,
        "status" : "Active",
        "instrument_token" : token,
        "levelDetails" : {
        "level" : lowerVal["last_price"],
        "type" : "fiveMinSup",
        "testCount" : 0,
        "interChanged" : False
        },
    },
    {
        "id": "Level-0"+str(count+2),
        "name" : instData["name"],
        "tradingsymbol" : instData["name"],
        "interchangable" : False,
        "status" : "Active",
        "instrument_token" : token,
        "levelDetails" : {
        "level" : upperVal["last_price"],
        "type" : "fiveMinRes",
        "testCount" : 0,
        "interChanged" : False
        }
    }]
    collection = db["levels"]
    res = collection.insert_many(obj)
    filterObj = {
            "name": instData["name"],
            "levelDetails.type":"resistance",
            "levelDetails.level":{"$gt":upperVal["last_price"]}
        }
    re = collection.update_many(
        filterObj,
        {
            "$set":{"status":"Active"}
        })
    
    filterObj = {
            "name": instData["name"],
            "levelDetails.type":"support",
            "levelDetails.level":{"$lt":lowerVal["last_price"]}
        }
    res = collection.update_many(
            filterObj,
        {
            "$set":{"status":"Active"}
        })

def selectStrikePrice(ltp,name,type):
        
    if name == "NIFTY" and type == "CE":
        str = (ltp / 50)
        sel = (ltp % 50)
        str = int(str)
        if sel > 50:
            str = str + 1
        str = (str * 50)
        return str
    
    if name == "NIFTY" and type == "PE":
        str = (ltp / 50)
        sel = (ltp % 50)
        str = int(str)
        if sel < 50:
            str = str + 1
        str = (str * 50)
        return str
    
    if (name == "BANKNIFTY" or name == "FINNIFTY") and type == "CE":
        str = (ltp / 100)
        sel = (ltp % 100)
        str = int(str)
        if sel > 100:
            str = str + 1
        str = (str * 100)
        return str
    
    if (name == "BANKNIFTY" or name == "FINNIFTY") and type == "PE":
        str = (ltp / 100)
        sel = (ltp % 100)
        str = int(str)
        if sel < 100:
            str = str + 1
        str = (str * 100)
        return str


def selectStrike(instrument_token, ltp, type):
    
    name = ""
    expiry = "2023-07-06"
    if instrument_token == 260105:
        name = "BANKNIFTY"
        qty = lot*25
    
    if instrument_token == 256265:
        name = "NIFTY"
        qty = lot*50

    if instrument_token == 257801:
        name = "FINNIFTY"
        expiry = "2023-07-04"
        qty = lot*40

    strike = selectStrikePrice(ltp,name,type)
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
    result = collection.find_one(query, projection)
    symbol = result["tradingsymbol"]
    strikeToken = result["instrument_token"]
    return (symbol,name,strikeToken,qty)


def exitOrder():
    orderCollection = db["orders"]
    orders = orderCollection.find({"status": "Active"})
    ordersList = list(orders)
    for order in ordersList:
        # place exit order
        fakeOrder(1234,order["strike"])
    levelCollection = db["levels"]
    levelCollection.update_many({},{"$set":{"status":"Closed"}})
    return





# CHANGING STATUS MANUALLY FOR NOW
def checkSupResStatus(level, indexAt):
    
    # orderCol = db["orders"]
    # orders = orderCol.find({},{"tradeResult":1,"_id":0})
    # orderList = list(orders)
    # for ord in orderList:
    # print(level)
    if level["interchangable"] == True:
        
        if level["name"] == "NIFTY BANK" and level["levelDetails"]["type"] == "resistance" and level["levelDetails"]["level"] +28 < indexAt < level["levelDetails"]["level"] + 35:
            
            levelCollection = db["levels"]
            res = levelCollection.update_one({
                "id": level["id"],
                "status": {"$ne": "Closed"}
            },
            {
              "$set":{
                  "interchangable": False,
                  "status": "Active",
                  "levelDetails.interChanged": True,
                  "interchangedAt": indexAt,
                  "levelDetails.type": "support",

              }  
            })
        
            if res.modified_count>0:
                msg = ["Level with ID",level["id"],", from index",level["name"],"at,",str(indexAt),"converted to Support"]
                result = " ".join(msg)
                SendMsg(result)

        if level["name"] == "NIFTY BANK" and level["levelDetails"]["type"] == "support" and level["levelDetails"]["level"] - 35 < indexAt < level["levelDetails"]["level"] - 28:
            levelCollection = db["levels"]
            res = levelCollection.update_one({
                "id": level["id"],
                "status": {"$ne": "Closed"}
            },
            {
              "$set":{
                  "interchangable": False,
                  "status": "Active",
                  "levelDetails.type": "resistance",
                  "interchangedAt": indexAt,
                  "levelDetails.interChanged": True,
              }  
            })
        
            if res.modified_count>0:
                msg = ["Level with ID",level["id"],", from index",level["name"],"at,",str(indexAt),"converted to Resistance"]
                result = " ".join(msg)
                SendMsg(result)
        
        if (level["name"] == "NIFTY 50" or level["name"] =="NIFTY FIN SERVICE") and level["levelDetails"]["type"] == "resistance" and level["levelDetails"]["level"] +14 < indexAt < level["levelDetails"]["level"] + 20:
        
            levelCollection = db["levels"]
            res = levelCollection.update_one({
                "id": level["id"],
                "status": {"$ne": "Closed"}
            },
            {
              "$set":{
                  "interchangable": False,
                  "status": "Active",
                  "levelDetails.type": "support",
                  "interchangedAt": indexAt,
                  "levelDetails.interChanged": True,
              }  
            })
            
        
            if res.modified_count>0:
                msg = ["Level with ID",level["id"],", from index",level["name"],"at,",str(indexAt),"converted to Support"]
                result = " ".join(msg)
               
                SendMsg(result)

        if (level["name"] == "NIFTY 50" or level["name"] =="NIFTY FIN SERVICE") and level["levelDetails"]["type"] == "support" and level["levelDetails"]["level"] - 20 < indexAt < level["levelDetails"]["level"] - 14:
            
            levelCollection = db["levels"]
            res = levelCollection.update_one({
                "id": level["id"],
                "status": {"$ne": "Closed"}
            },
            {
              "$set":{
                  "interchangable": False,
                  "status": "Active",
                  "levelDetails.type": "resistance",
                  "interchangedAt": indexAt,
                  "levelDetails.interChanged": True
              }  
            })
        
            if res.modified_count>0:
                msg = ["Level with ID",level["id"],", from index",level["name"],"at,",str(indexAt),"converted to Support"]
                result = " ".join(msg)
                SendMsg(result)
            

    return

def changeType():
    return