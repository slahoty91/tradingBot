from kiteconnect import KiteConnect
import datetime
from mongo import *


exchange = ["NSE","NFO"]

client = ConnectDB()
db = client['algoTrading']
def getKiteObj():
   collection = db["userDetails"]
   user = collection.find_one({})
   kite = KiteConnect(user["apikey"]) 
   kite.set_access_token(user["acc_token"])
   return kite

def download_instruments(exch):
    lst = []
    kite = getKiteObj()
    if exch == 'NSE':
        lst = kite.instruments(exchange=kite.EXCHANGE_NSE)
    if exch == 'NFO':
        lst = kite.instruments(exchange=kite.EXCHANGE_NFO)
    return lst


# download_instruments('NSE')

def insertData():
    
    for exch in exchange:
        strikeList = download_instruments(exch)
        if exch == "NFO":
            collection = db["instrumentNFO"]
            for strike in strikeList:
                strike["expiry"] = strike["expiry"].strftime('%Y-%m-%d')
        
        if exch == "NSE":
            collection = db["instrumentNSE"]
        
        collection.insert_many(strikeList)


insertData()





# def insertData(data,exchange):
#     print(len(data),exchange,data[0])
#     if exchange == 'NSE':
#         colection = db['instrumentNSE']
#         for item in data:
#             print(item,"inside forrrrr")
#             item['expiry'] = item['expiry'].strftime('%Y-%m-%d')
#     if exchange == 'NFO':
#         print("inside ifffff")
#         colection = db['instrumentNFO']
#         for item in data:
#             print(item,"inside forrrrr")
#             item['expiry'] = item['expiry'].strftime('%Y-%m-%d')
#             print(item,"data inside iffff")
#     try:
#         # print(data[0])
#         colection.insert_many(data)
#     except Exception as e:
#         print("Insert failed: {}".format(e))

# dataNFO = download_instruments('NFO')


# insertData(dataNFO,'NSE')

# colectionName = db['instrumentNFO']
# try:
#     colectionName.insert_many(dataNFO)
# except Exception as e:
#         print("Insert failed: {}".format(e))

# dataNSE = download_instruments('NSE')

# count = 0

     

# collectionName = db['instrumentNSE']
# try:
#     collectionName.insert_many(dataNSE)
# except Exception as e:
#     print("Insert failer{}".format(e))


     