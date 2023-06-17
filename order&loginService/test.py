# import mongo

# client = mongo.ConnectDB()
# db = client["algoTrading"]
# collection = db["levels"]

# count = collection.count_documents({})
# print(count,'counttttttttt')

# def myFunc(e):
#   return e['last_price']

# levels = [{'last_price': 44107.0}, {'last_price': 44106.4}, {'last_price': 44105.6}, {'last_price': 44106.65}, {'last_price': 44109.3}, {'last_price': 44109.7}, {'last_price': 44118.2}, {'last_price': 44118.2}, {'last_price': 44121.95}, {'last_price': 44119.7}, {'last_price': 44119.05}, {'last_price': 44116.55}, {'last_price': 44115.75}, {'last_price': 44116.95}, {'last_price': 44114.75}, {'last_price': 44113.8}, {'last_price': 44113.85}, {'last_price': 44111.85}, {'last_price': 44112.05}, {'last_price': 44110.15}, {'last_price': 44109.2}, {'last_price': 44110.3}, {'last_price': 44111.45}, {'last_price': 44110.25}, {'last_price': 44107.5}, {'last_price': 44109.15}, {'last_price': 44107.7}, {'last_price': 44108.05}, {'last_price': 44111.05}, {'last_price': 44110.25}, {'last_price': 44110.25}, {'last_price': 44109.0}, {'last_price': 44113.75}, {'last_price': 44114.4}, {'last_price': 44112.8}, {'last_price': 44112.95}, {'last_price': 44111.05}, {'last_price': 44109.2}, {'last_price': 44110.75}, {'last_price': 44104.2}, {'last_price': 44108.9}, {'last_price': 44108.4}, {'last_price': 44108.05}, {'last_price': 44110.3}, {'last_price': 44110.85}, {'last_price': 44106.8}, {'last_price': 44108.15}, {'last_price': 44104.1}, {'last_price': 44105.4}, {'last_price': 44103.8}, {'last_price': 44100.95}, {'last_price': 44102.95}, {'last_price': 44099.6}, {'last_price': 44098.45}, {'last_price': 44095.5}, {'last_price': 44094.7}, {'last_price': 44096.05}, {'last_price': 44098.15}, {'last_price': 44102.3}, {'last_price': 44095.6}, {'last_price': 44097.0}, {'last_price': 44100.75}, {'last_price': 44095.65}, {'last_price': 44104.1}, {'last_price': 44096.45}, {'last_price': 44098.55}, {'last_price': 44100.45}, {'last_price': 44100.8}, {'last_price': 44101.0}, {'last_price': 44103.2}, {'last_price': 44102.05}, {'last_price': 44105.05}, {'last_price': 44108.6}, {'last_price': 44105.05}, {'last_price': 44101.3}, {'last_price': 44110.85}, {'last_price': 44110.35}, {'last_price': 44109.9}, {'last_price': 44105.2}, {'last_price': 44107.75}, {'last_price': 44109.8}]

# levels.sort(key=myFunc)
# # print(levels)

# obj = [{
#     "id": "Level-0"+str(count+1),
#     "name" : "NIFTY BANK",
#     "tradingsymbol" : "NIFTY BANK",
#     "interchangable" : False,
#     "status" : "Active",
#     "instrument_token" : 260105,
#     "levelDetails" : {
#       "level" : levels[0]["last_price"],
#       "type" : "fiveMinSup",
#       "testCount" : 0,
#       "interChanged" : False
#     },
# },{
#     "id": "Level-0"+str(count+2),
#     "name" : "NIFTY BANK",
#     "tradingsymbol" : "NIFTY BANK",
#     "interchangable" : False,
#     "status" : "Active",
#     "instrument_token" : 260105,
#     "levelDetails" : {
#       "level" : levels[len(levels)-1]["last_price"],
#       "type" : "fiveMinRes",
#       "testCount" : 0,
#       "interChanged" : False
#     }
# }]
# print(obj,'objecttttttt')
# collection.insert_many(obj)

import random
from datetime import datetime, time, timedelta

from bson import BSON

# num = random.randint(10000,99999)
# print(num)
# start_time = datetime(2023, 6, 5, 10, 30)  # 10:30 AM

# # Subtract 2 hours from the datetime
# new_time = start_time - timedelta(hours=2)

# # Print the new time
# print(new_time)

# current_time = datetime.now().time()

# # Time stored in a variable (replace with your own time)
# stored_time = datetime.strptime("10:20", "%H:%M").time()

# # Calculate the time difference
# time_diff = datetime.combine(datetime.min, current_time) - datetime.combine(datetime.min, stored_time)

# # Print the result
# print(time_diff)
# current_time = datetime.now().time()
# stored_time = datetime.strptime("10:20", "%H:%M").time()
# if current_time > stored_time:
#     print("hiiii")

# trendSch = {
#     "up":"BULLISH",

# }
# print(trendSch)

# level = {'id': 'Level-08', 'name': 'NIFTY BANK', 'tradingsymbol': 'NIFTY BANK', 'interchangable': False, 'status': 'Active', 'instrument_token': 260105, 'levelDetails': {'level': 44212.0, 'type': 'fiveMinSup', 'testCount': 0, 'interChanged': False}}

# if hasattr(level,"tradeResults"):
#     tradeResult = level["tradeResults"]
#     print(tradeResult,"tradeResulttttttttt")
# else:
#     print("notttttt")
# obj = {'orderId': 57725, 'instrument_token': 12833794, 'parent_instrument_token': 260105, 'indexAt': 44414.9, 'strike': 'BANKNIFTY2360144400CE', 'indexName': 'BANKNIFTY', 'price': 44414.9, 'executedAt': datetime.time(11, 20, 26, 791789), 'levelId': 'Level-07', 'levelStatus': 'Active', 'levelType': 'support', 'stopLoss': 43526.602, 'target': 51077.135, 'status': 'Active'}

# my_time_str = obj['executedAt'].strftime("%H:%M:%S.%f") 
# print(my_time_str)
# bson_data = BSON.encode({'time': my_time_str})
# print(bson_data,"bson data")
# from mongo import ConnectDB
# client = ConnectDB()
# db = client["algoTrading"]
# collection = db["orders"]
# status = collection.find_one({"indexName" : "IFTY","status":"Active"},{"status":1,"_id":0})
# print(status)
# obj = { 'id': 'Level-013', 'name': 'NIFTY BANK', 'tradingsymbol': 'NIFTY BANK', 'interchangable': False, 'status': 'Passive', 'instrument_token': 260105, 'levelDetails': {'level': 44096.0, 'type': 'support', 'testCount': 347, 'interChanged': False}, 'tradeResults': [{'orderId': 29122, 'result': 'Loss'}, {'orderId': 33339, 'result': 'Loss'}], 'lastTradeTime': '09:39:05.097376'}
# print(hasattr(obj,"tradeResults"))
# if "tradeResults" in obj:
#     print("Hiiiiiii")
# start_time = datetime.strptime("15:00:10", "%H:%M:%S").time()
# current_time = datetime.now().time()
# end_time = datetime.strptime("15:20", "%H:%M").time()
# if start_time <= current_time <= end_time:
#     print(start_time)



# def sendMsg():
#     bot_token = "6270701562:AAFNW56fYAdhUqHNB-a2szT3GFOKbeOjJn8"
#     botchatId = "5143995071"
#     sendText = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + botchatId + "&text="+"Helllo from the other side"
#     print(sendText,"<<<<<<send text")
#     resp = requests.get(sendText)
#     return resp.json()

# print(sendMsg())

# 5143995071
# 

# from sendTelegramMsg import *
# from sendTelegramMsg import SendMsg

# SendMsg("hiiii")
tt = "hiiiii"

print(str(tt))