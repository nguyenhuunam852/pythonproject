from pymongo import MongoClient
import json
client = MongoClient('mongodb://localhost:27017/?readPreference=primary&authSource=admin&appname=MongoDB%20Compass&ssl=false')
db = client.acronym_word

def checkWord(word):
    ct = db.word.find({'text': word.upper()}).count()
    if(ct==0):
        return 1
    print('xoa '+word)
    return 0

        

