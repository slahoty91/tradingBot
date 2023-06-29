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




     