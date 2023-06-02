from datetime import datetime, time
from mongo import *
from order import placeBuyOrderMarketNSE, orderHistory, PlaceSellOrderMarketNSE, fakeOrder

support = [43583,44000]
resistance = [43682,44360]
expiry = "2023-06-01"
target = 10
stoppLoss = 2.5
client = ConnectDB()
db = client["algoTrading"]
current_time = datetime.now().time()
start_time = time(9, 15)
end_time = time(9, 20)

def fetchData(data):
    print(data,'from fetch data')
    if start_time <= current_time <= end_time:
        firstFiveMin(data,end_time,current_time)
    if data["instrument_token"] != 260105:
        checkTargetAndSL(data)
    # If INSTRUMENT TOKEN IN OF INDEX SEND HERE
    if data['instrument_token'] == 260105:
        return checkCondition(support, resistance, data['last_price'], data['instrument_token'])
    return False

def checkCondition(support,resistance,tradingprice,istToken):
    for sup in support:
        # print('from support for',tradingprice,sup,(tradingprice - sup))
        if (sup <= tradingprice<=sup+100):
            return placeOrder(tradingprice, istToken, "CE")
            # return True
    
    for res in resistance:
        # print('from res for',tradingprice)
        if( res-10<=tradingprice<= res):
            print('oreder placed put',tradingprice)
            return

    return

def checkTargetAndSL(data):
    print(data,'from checkTarget and sl')
    collection = db["orders"]
    result = collection.find({"parent_instrument_token" : 260105})
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
        if(purchasePrice <= currentPrice):
            print("TRAIL stpLss HERE TILL PURCHASE PRICE")
            collection.update_one(
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
            orderId = "230531601394633"
            # orderData = orderHistory(orderId)
            orderData = fakeOrder(data["last_price"])
            orderTime = orderData[len(orderData)-1]['order_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            sellPrice = orderData[len(orderData)-1]['average_price']
            trade = ((purchasePrice - sellPrice)/purchasePrice)*100
            if purchasePrice >= (sellPrice + (sellPrice*1)/100):
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
            collection.update_one({
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
        print(stpLss, target,'sl and targettttttttt')
    return

def placeOrder(price, token,type):

    collection = db["orders"]
    status = collection.find_one({"indexName" : "BANKNIFTY","status":"Active"},{"status":1,"_id":0})
    print(status,'statussssssss From order placed')
    # below not is to handle syntax and not condition
    if status == None :
        print("from status == None")
        strike = selectStrike(token,price,type)
        # orderId = placeBuyOrderMarketNSE("YESBANK",1)
        # orderData = orderHistory(orderId)
        orderData = fakeOrder(price)
        orderTime = orderData[len(orderData)-1]['order_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        purchasePrice = orderData[len(orderData)-1]['average_price']
        sl = purchasePrice - (purchasePrice * stoppLoss)/100
        tar = purchasePrice + (purchasePrice * target)/100
        obj = { 
            # "orderId":orderId,
            "orderId": 1234,
            "instrument_token": strike[2],
            "parent_instrument_token": token,
            "indexAt": price,
            "strike": strike[0],
            "indexName": strike[1],
            "price": orderData[len(orderData)-1]['average_price'],
            "executedAt": orderTime,
            "stopLoss": sl,
            "target": tar,
            "status": "Active"
        }
        print(obj,'objjjjj from order',strike)
        collection.insert_one(obj)
        # print('after obj inserted in order collection')
        return strike[2]
    else: 
        print("status from else",status)


def myFunc(e):
    return e['last_price']
def firstFiveMin(data,endT,curT):
    print('from first five min')
    collectionName = db["firstFiveMinData"]
    collectionName.insert_one(data)
    if(curT == endT): 
        val = collectionName.find({"instrument_token" : 260105},{"last_price":1,"_id":0})
        val = list(val)
        # print(val,'')
        val.sort(key=myFunc)
        print(val)
        lowerVal = val[0]
        upperVal = val[len(val)-1]

        # now save in support and resistance table
        # collectionName = db["supportResistanceLevel"]
        
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
