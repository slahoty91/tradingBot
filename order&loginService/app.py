from kiteconnect import KiteConnect
import mongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from pyotp import TOTP
import time
client = mongo.ConnectDB()
db = client["algoTrading"]

def getUserDetails():
   collection = db["userDetails"]
   user = collection.find_one({})
   return user

# getUserDetails()

def launchBrowser(userDetails):
   
   kite = KiteConnect(userDetails["apikey"])
   chrome_options = Options()
   chrome_options.binary_location="../Google Chrome"
   chrome_options.add_argument("disable-infobars")
   chrome_options.add_argument('--headless')
   driver = webdriver.Chrome()

   driver.get(kite.login_url())
   driver.implicitly_wait(10)

   username = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
   password = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
   username.send_keys(userDetails["userName"])
   password.send_keys(userDetails["password"])
   driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
   pin = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/form/div[1]/input')
   tkn = userDetails["totpToken"]
   totp = TOTP(tkn)
   token = totp.now()
   pin.send_keys(token)
   time.sleep(2)
   request_token=driver.current_url.split('request_token=')[1][:32]
   driver.quit()
   return request_token

def autoLogin():
    rqToken = ''
    user = getUserDetails()
    rqToken = launchBrowser(user)
    if rqToken != '':
         print(rqToken)
         kite = KiteConnect(user["apikey"]) 
         data = kite.generate_session(rqToken,user["apiSecrete"])
         print(data["access_token"],'access_token')
         collection = db['userDetails']
         collection.update_one({"name":"SIDDHARTH LAHOTY"},{"$set":{"acc_token":data["access_token"]}})

autoLogin()