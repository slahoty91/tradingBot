# import pymongo

# client = pymongo.MongoClient('mongodb://localhost:27017/algoTrading')

from pymongo import MongoClient

def ConnectDB():
            # Provide the mongodb atlas url to connect python to mongodb using pymongo
            CONNECTION_STRING = "mongodb://localhost:27017/"
                
                # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
            client = MongoClient(CONNECTION_STRING)
                
                # Create the database for our example (we will use the same database throughout the tutorial
            return client
 