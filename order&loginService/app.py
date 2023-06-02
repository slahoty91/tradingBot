from kiteconnect import KiteConnect
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from pyotp import TOTP
import time

def launchBrowser(key_secret):
   i = 0
   kite = KiteConnect(key_secret[0])
   chrome_options = Options()
   chrome_options.binary_location="../Google Chrome"
   chrome_options.add_argument("disable-infobars")
   chrome_options.add_argument('--headless')
   driver = webdriver.Chrome()

   driver.get(kite.login_url())
   driver.implicitly_wait(10)
   username = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
   password = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
   username.send_keys(key_secret[2])
   password.send_keys(key_secret[3])
   driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
   print('before pinnnnnnnnn')
   
   pin = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/form/div[1]/input')
   totp = TOTP(key_secret[4])
   token = totp.now()
   print(token,'tokennnnnnnnnnnn')
   pin.send_keys(token)
#    driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()
   print(username)
   time.sleep(2)
   request_token=driver.current_url.split('request_token=')[1][:32]
   print(request_token,'requestTokennnnnnnnn')
   driver.quit()
   return request_token
#    with open('request_token.txt', 'w') as the_file:
#     the_file.write(request_token)
#     driver.quit()
#     i += i
#     if i > 0:
#        return
#    while(True):
#        pass

def autoLogin():
    rqToken = ''
    pw = os.chdir("/Users/siddharthlahoty/Desktop/AlogoTrading/order&loginService/acc_auth")
    token_path = "ap_key.txt"
    key_secret = open(token_path,'r').read().split()

    print(key_secret,'keyyyyy',key_secret[0])
    
    rqToken = launchBrowser(key_secret)
    print('line 57')
    if rqToken != '':
        print(rqToken)
        kite = KiteConnect(api_key=key_secret[0])
        data = kite.generate_session(rqToken, api_secret=key_secret[1])
        print(data["access_token"],'access_token')
        with open('/Users/siddharthlahoty/Desktop/AlogoTrading/order&loginService/acc_auth/access_token.txt', 'w') as file:
         file.write(data["access_token"])
    print('line 60')
    # request_token = open("/Users/siddharthlahoty/Desktop/AlogoTrading/app.py",'r').read()
    # key_secret = open("/Users/siddharthlahoty/Desktop/AlogoTrading/acc_auth/ap_key.txt",'r').read().split()
    # print(request_token,key_secret,'line 51')
    # kite = KiteConnect(api_key=key_secret[0])
    # data = kite.generate_session(request_token, api_secret=key_secret[1])
    # print(data["access_token"],'access_token')
    # with open('acc_auth/access_token.txt', 'w') as file:
    #     file.write(data["access_token"])

autoLogin()

