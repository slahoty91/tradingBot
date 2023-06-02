from kiteconnect import KiteConnect
import pandas as pd
import os
import csv
from mongo import *
from dateutil import parser
pw = os.chdir("/Users/siddharthlahoty/Desktop/AlogoTrading/acc_auth")
acc_token_path = "access_token.txt"
acc_token = open(acc_token_path,'r').read().split()
print(acc_token,"access tokennnnnnnnnnnn")
kite = KiteConnect(api_key="k55bdfkr27eqguv6")
data = kite.set_access_token(acc_token[0])

client = ConnectDB()
db = client['algoTrading']
def download_instruments(exch):
    lst = []
    if exch == 'NSE':
        lst = kite.instruments(exchange=kite.EXCHANGE_NSE)
    else:
        lst = kite.instruments(exchange=kite.EXCHANGE_NFO)
    return lst

def insertData(data,exchange):
    colection 
    if exchange == 'NSE':
        colection = db['instrumentNSE']
    if exchange == 'NFO':
        colection = db['instrumentNFO']
        for item in data:
            item['expiry'] = item['expiry'].strftime('%Y-%m-%d')
    try:
        colection.insert_many(data)
    except Exception as e:
        print("Insert failed: {}".format(e))

dataNFO = download_instruments('NFO')


insertData(dataNFO,'NSE')

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


     