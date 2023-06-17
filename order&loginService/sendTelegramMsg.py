import requests
from mongo import ConnectDB

client = ConnectDB()
db = client["algoTrading"]
usersCollection = db["userDetails"]

def SendMsg(msg):

    res = usersCollection.find_one({"name": "SIDDHARTH LAHOTY"},{"_id":0,"telegramInfo":1})
    print(res)
    bot_token = res["bot_token"]
    botchatId = res["botchatId"]
    sendText = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id=" + botchatId + "&text="+msg
    print(sendText,"<<<<<<send text")
    resp = requests.get(sendText)
    return resp.json()