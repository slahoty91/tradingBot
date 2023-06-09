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
trend = "BEARISH"
testing = True
# Index tokens
indexTokens = [260105,256265,257801]



def fetchData(data):
    print("From fetch data",data)
    current_time = datetime.now().time()
    if start_time <= current_time <= end_time:
        firstFiveMin(data,end_time,current_time)
    if current_time > end_time:
        collection = db["levels"]
        levels = collection.find({"instrument_token" : data["instrument_token"],"status":"Active"})
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
    print(len(levels),"level lengthhhhhh",tradingprice)
    firstFiveMinTrade = True
    current_time = datetime.now().time()
    conditionTime = datetime.strptime("9:30", "%H:%M").time()
    startSwing = datetime.strptime("9:30", "%H:%M").time()
    exitTime = datetime.strptime("15:20","%H:%M").time()
    
    for lev in levels:
        # checkSupResStatus(lev,tradingprice)
        # Add tiem bound condition
        # print(lev["levelDetails"]["level"],"levvvvvvvv",lev["levelDetails"]["type"])
        # return
        rangeLow = 0
        rangeUp = 0
        if lev["name"] == "NIFTY 50" or lev["name"] == "NIFTY FIN SERVICE":
            
            entryCE =  lev["levelDetails"]["level"]+5
            entryPE =  lev["levelDetails"]["level"]-5
            if lev["levelDetails"]["type"] == "fiveMinRes" or lev["levelDetails"]["type"] == "fiveMinSup":
                rangeUp =  lev["levelDetails"]["level"] + 15
                rangeLow = lev["levelDetails"]["level"] - 15
        
        if lev["name"] == "NIFTY BANK":
            entryCE =  lev["levelDetails"]["level"] + 10
            entryPE =  lev["levelDetails"]["level"] - 10
            if lev["levelDetails"]["type"] == "fiveMinRes" or lev["levelDetails"]["type"] == "fiveMinSup":
                rangeUp =  lev["levelDetails"]["level"] + 30
                rangeLow = lev["levelDetails"]["level"] - 30
            
        
        if current_time <= conditionTime:
            
            levelCollection = db["levels"]
            filterQuery = {
               "instrument_token": istToken,
                "status": {"$ne":"Closed"},
                "levelDetails.type":{'$nin':["fiveMinRes","fiveMinSup"]},
                "levelDetails.level":{
                    "$gte": rangeLow,
                    "$lte": rangeUp
                }
            } 

            levelToAvoid = levelCollection.count_documents(filterQuery)
            if levelToAvoid > 0:
                firstFiveMinTrade = False
            
            print(levelToAvoid,filterQuery,"filter queryyyyyyy",firstFiveMinTrade)
            if (lev["levelDetails"]["type"] == "fiveMinRes" and tradingprice > entryCE and lev["status"] == "Active") and trend != "BEARISH" and firstFiveMinTrade == True:
                
                return placeOrder(tradingprice, istToken, "CE",lev)
            
            if (lev["levelDetails"]["type"] == "fiveMinSup" and tradingprice < entryPE and lev["status"] == "Active") and trend != "BULLISH" and firstFiveMinTrade == True:
                return placeOrder(tradingprice, istToken, "PE",lev)

        if current_time >= startSwing:
            # print(tradingprice,entryCE,lev["levelDetails"]["level"],"entryyyy")
            if (lev["levelDetails"]["type"] == "support") and lev["levelDetails"]["level"]<tradingprice<entryCE and lev["status"] == "Active" and trend != "BEARISH":
                return placeOrder(tradingprice, istToken, "CE",lev)
            
            if lev["levelDetails"]["type"] == "resistance" and entryPE<tradingprice<lev["levelDetails"]["level"] and lev["status"] == "Active" and trend != "BULLISH":
                return placeOrder(tradingprice, istToken, "PE",lev)
            

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
    print(status,"statuss from place order",token,level)
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
        if testing == "False" and purchasePrice < 100:
            risk = 0
            if 70 < purchasePrice < 100:
                risk = 6

            if  purchasePrice <= 70:
                risk = 7

            sl = purchasePrice - risk
            tar = purchasePrice + risk*riskToReward

        count = collection.count_documents({})
        print(count,"from count documentssss")
        orderStatus = ""
        if testing == False:
            orderStatus = orderData[len(orderData)-1]['status']
        status = "Active"
        if orderStatus == "REJECTED":
            status = "Closed"

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
            "qty": strike[3],
            "status": status,
            "testing": testing
        }
        orderCollection = db["orders"]
        orderCollection.insert_one(obj)
        
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
        qty = result[0]["qty"]
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
                # if result[0]["indexName"]
                orderId = PlaceSellOrderMarketNFO(result[0]["strike"],qty)
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
            status = "Closed"
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
    filterObjRes = {
                "name": instData["name"],
                "status":"Passive",
                "levelDetails.type":"resistance",
                "levelDetails.level":{"$gt":upperVal["last_price"]}
            }
        
        
    filterObjSup = {
            "name": instData["name"],
            "status":"Passive",
            "levelDetails.type":"support",
            "levelDetails.level":{"$lt":lowerVal["last_price"]}
        }
    # if trend == "SIDEWAYS":

        
        

        
    # if trend == "BULLISH":
    #      filterObjRes = {
    #             "name": instData["name"],
    #             "levelDetails.type":"resistance",
    #             "levelDetails.level":{"$gt":upperVal["last_price"]}
    #         }

    #      filterObjSup = {
    #             "name": instData["name"],
    #             "levelDetails.type":"support",
    #             "levelDetails.level":{"$lt":upperVal["last_price"]}
    #         }
         
    # if trend == "BEARISH":
    #     filterObjRes = {
    #         "name": instData["name"],
    #         "levelDetails.type":"resistance",
    #         "levelDetails.level":{"$gt":lowerVal["last_price"]}
    #     }

    #     filterObjSup = {
    #         "name": instData["name"],
    #         "levelDetails.type":"resistance",
    #         "levelDetails.level":{"$lt":lowerVal["last_price"]}
    #     }

    reRes = collection.update_many(
            filterObjRes,
            {
                "$set":{"status":"Active"}
            })
    reSup = collection.update_many(
                filterObjSup,
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
    expiry = "2023-07-13"
    if instrument_token == 260105:
        name = "BANKNIFTY"
        qty = lot*25
    
    if instrument_token == 256265:
        name = "NIFTY"
        qty = lot*50

    if instrument_token == 257801:
        name = "FINNIFTY"
        expiry = "2023-07-18"
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
    
    levelCollection = db["levels"]

    if level["interchangable"] == True:
        
        if level["name"] == "NIFTY BANK" and level["levelDetails"]["type"] == "resistance" and level["levelDetails"]["level"] + 50 < indexAt < level["levelDetails"]["level"] + 60:
            
            
            res = levelCollection.update_one({
                "id": level["id"],
                "levelDetails.type": "resistance",
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

        if level["name"] == "NIFTY BANK" and level["levelDetails"]["type"] == "support" and level["levelDetails"]["level"] - 60 < indexAt < level["levelDetails"]["level"] - 50:
            
            res = levelCollection.update_one({
                "id": level["id"],
                "levelDetails.type": "support",
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
        
        if (level["name"] == "NIFTY 50" or level["name"] =="NIFTY FIN SERVICE") and level["levelDetails"]["type"] == "resistance" and level["levelDetails"]["level"] + 20 < indexAt < level["levelDetails"]["level"] + 25:
        
            
            res = levelCollection.update_one({
                "id": level["id"],
                "levelDetails.type": "resistance",
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
            

        if (level["name"] == "NIFTY 50" or level["name"] =="NIFTY FIN SERVICE") and level["levelDetails"]["type"] == "support" and level["levelDetails"]["level"] - 25 < indexAt < level["levelDetails"]["level"] - 20:
            
            
            res = levelCollection.update_one({
                "id": level["id"],
                "status": {"$ne": "Closed"},
                "levelDetails.type": "support"
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
        
        # if res.modified_count>0:
        #     msg = ["Level with ID",level["id"],"and type",level["levelDetails"]["type"],", from index",level["name"],"at,",str(indexAt),"interchanged"]
        #     result = " ".join(msg)
        #     SendMsg(result)
    
    currentTime = datetime.now().time()
    start_time = datetime.strptime("9:29:50", "%H:%M:%S").time()
    end_time = datetime.strptime("9:29:58", "%H:%M:%S").time()
    if start_time <= currentTime <= end_time:
        if level["levelDetails"]["type"] == "support" and level["levelDetails"]["level"] > indexAt:
            filterQuery = {
                "id": level["id"],
                "status": "Active"
            }
            updateQuery = {
                "set":{
                    "status": "Passive"
                }
            }
        
        if level["levelDetails"]["type"] == "resistance" and level["levelDetails"]["level"] < indexAt:
            filterQuery = {
                "id": level["id"],
                "status": "Active"
            }
            updateQuery = {
                "set":{
                    "status": "Passive"
                }
            }
        res = levelCollection.update_one(filterQuery,updateQuery)
        if res.modified_count>0:
            msg = ["Level with ID",level["id"],"and type",level["levelDetails"]["type"],", from index",level["name"],"at,",str(indexAt),"changed to passive"]
            result = " ".join(msg)
            SendMsg(result)
    return

def changeType():
    return