import mongo

client = mongo.ConnectDB()
db = client["algoTrading"]
collection = db["levels"]

count = collection.count_documents({})
print(count,'counttttttttt')

def myFunc(e):
  return e['last_price']

levels = [{'last_price': 44107.0}, {'last_price': 44106.4}, {'last_price': 44105.6}, {'last_price': 44106.65}, {'last_price': 44109.3}, {'last_price': 44109.7}, {'last_price': 44118.2}, {'last_price': 44118.2}, {'last_price': 44121.95}, {'last_price': 44119.7}, {'last_price': 44119.05}, {'last_price': 44116.55}, {'last_price': 44115.75}, {'last_price': 44116.95}, {'last_price': 44114.75}, {'last_price': 44113.8}, {'last_price': 44113.85}, {'last_price': 44111.85}, {'last_price': 44112.05}, {'last_price': 44110.15}, {'last_price': 44109.2}, {'last_price': 44110.3}, {'last_price': 44111.45}, {'last_price': 44110.25}, {'last_price': 44107.5}, {'last_price': 44109.15}, {'last_price': 44107.7}, {'last_price': 44108.05}, {'last_price': 44111.05}, {'last_price': 44110.25}, {'last_price': 44110.25}, {'last_price': 44109.0}, {'last_price': 44113.75}, {'last_price': 44114.4}, {'last_price': 44112.8}, {'last_price': 44112.95}, {'last_price': 44111.05}, {'last_price': 44109.2}, {'last_price': 44110.75}, {'last_price': 44104.2}, {'last_price': 44108.9}, {'last_price': 44108.4}, {'last_price': 44108.05}, {'last_price': 44110.3}, {'last_price': 44110.85}, {'last_price': 44106.8}, {'last_price': 44108.15}, {'last_price': 44104.1}, {'last_price': 44105.4}, {'last_price': 44103.8}, {'last_price': 44100.95}, {'last_price': 44102.95}, {'last_price': 44099.6}, {'last_price': 44098.45}, {'last_price': 44095.5}, {'last_price': 44094.7}, {'last_price': 44096.05}, {'last_price': 44098.15}, {'last_price': 44102.3}, {'last_price': 44095.6}, {'last_price': 44097.0}, {'last_price': 44100.75}, {'last_price': 44095.65}, {'last_price': 44104.1}, {'last_price': 44096.45}, {'last_price': 44098.55}, {'last_price': 44100.45}, {'last_price': 44100.8}, {'last_price': 44101.0}, {'last_price': 44103.2}, {'last_price': 44102.05}, {'last_price': 44105.05}, {'last_price': 44108.6}, {'last_price': 44105.05}, {'last_price': 44101.3}, {'last_price': 44110.85}, {'last_price': 44110.35}, {'last_price': 44109.9}, {'last_price': 44105.2}, {'last_price': 44107.75}, {'last_price': 44109.8}]

levels.sort(key=myFunc)
# print(levels)

obj = [{
    "id": "Level-0"+str(count+1),
    "name" : "NIFTY BANK",
    "tradingsymbol" : "NIFTY BANK",
    "interchangable" : False,
    "status" : "Active",
    "instrument_token" : 260105,
    "levelDetails" : {
      "level" : levels[0]["last_price"],
      "type" : "fiveMinSup",
      "testCount" : 0,
      "interChanged" : False
    },
},{
    "id": "Level-0"+str(count+2),
    "name" : "NIFTY BANK",
    "tradingsymbol" : "NIFTY BANK",
    "interchangable" : False,
    "status" : "Active",
    "instrument_token" : 260105,
    "levelDetails" : {
      "level" : levels[len(levels)-1]["last_price"],
      "type" : "fiveMinRes",
      "testCount" : 0,
      "interChanged" : False
    }
}]
print(obj,'objecttttttt')
# collection.insert_many(obj)