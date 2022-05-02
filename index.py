from flask import Flask,render_template,request,redirect,send_file
from os import remove
from importbills import *
import secondarybills
import downbills
from time import sleep
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import webbrowser
from flask_cors import CORS
from collections import defaultdict
import dill as pickle 

app = Flask(__name__)
CORS(app)
def save() :
   with open("logs.pkl", "wb") as f : 
     pickle.dump(Logs,f) 
 

def getstringbills(arr) : 
   if len(arr) > 0 : 
     return arr[0] + ' - ' + arr[-1]
   else : 
       print(arr)
       return "" 

class Date :
    def __init__(self) : 
        self.logs = []
        self.bills = []
        self.lines_count = {}
        self.creditlock = [] 
        self.collection = []
        self.success = 0 
        self.failure = 0 
    def addlogs(self,count_bills = 50) :
        print("New Process started")
        log = Log(count_bills,self) 
        print(log,"done")
        self.current_log = log
        log.start()
        self.failure += (1 if log.failure else 0 )
        self.success += (0 if log.failure else 1 )
        self.bills += log.bills
        for key,value in log.lines_count.items() : 
            if key not in self.lines_count.keys() :
                self.lines_count[key] = value
        self.lines_count.update(log.lines_count)
        self.collection += [ collection["parCode"] for collection in  log.filtered_collection ]
        print(log.collection,log.bills,self.bills,log.creditlock )
        if log.collection == 1   : 
               self.creditlock = log.creditlock
        save()
        return  { "stats" : { "Current Process Bills Count" :len(log.bills)  ,'Current Process Collection Count' : len(log.collection)  ,
                 "Today Total Bills Count": len(self.bills)  ,'Today Total Collection Count' : len(self.collection) ,
                 "Bills (Total) " : getstringbills(self.bills)   , "Bills (Last Sync) " : getstringbills(log.bills)  ,
                 "SuccessFull" : self.success , "Failures" : self.failure }  ,
                 "creditlock" : self.creditlock } 
       

@app.route('/start/<count>',methods = ["POST"])
def start(count) :
    res = today.addlogs()
    return res  

@app.route('/status',methods = ["POST"])
def status() :
    return today.current_log.status()
   
 

@app.route('/billindex')
def index() :
    return app.send_static_file('index.html')
try : 
  with open('logs.pkl','rb') as f : 
   Logs = pickle.load(f)
except :
    print("New Logs created , Before is stuck couldnt retrieve ")
    Logs = defaultdict(Date)
#with open('logs.pkl','rb') as f : 
#   Logs = pickle.load(f)

today = Logs[datetime.now().strftime('%d/%m/%Y')]
dates = list(Logs.keys())
dates.sort(key = lambda date : datetime.strptime(date,'%d/%m/%Y'))
if len(dates) >= 10 : 
  dates = dates[-10:]
Logs = {key:value for key,value in Logs.items() if key in dates }




webbrowser.open('http://127.0.0.1:5000/billindex')
app.config['JSON_SORT_KEYS'] = False
app.run(threaded=True)
