from selenium import webdriver
from datetime import datetime
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from os import listdir,remove,rename
from datetime import datetime
#import winsound
#from pdfcombiner import pdfcombine
import secondarybills
from IMP.main import *
from warnings import filterwarnings
filterwarnings("ignore")
import win32api 
import json
from selenium.webdriver.support.ui import Select
from datetime import timedelta 
from collections import defaultdict
import random
import pickle 
import traceback
import inspect
from creditlock import *

path = "D:\\dataprint\\"
def getajax(name) :
     return ajax.split('_'+name+'_')[1]
with open('ajax.txt') as f :
     ajax = f.read()

class logdict(dict) : 
    def __init__(self) :
        self.status = 0 
        self.log = ""
        self.ajax = ""
def creditunlock(driver,pdata) :
   for party_data in pdata : 
     releaselock(driver,party_data)

def interpret(file,valid_partys,driver) : 
   with open(file) as f : 
      ikea_log = f.read()
   ikea_log = ikea_log.split('Order import process started')[-1]
   ikea_log = ikea_log.split('\n')
   tempcreditlock = []
   for log in ikea_log : 
       if "Credit Bills" in log :
           tempcreditlock.append(log.split(',')[1])
   creditlock = {}
   for party in tempcreditlock :
      party = party.replace(' ','')
      if  party in valid_partys.keys() :
             party_data = valid_partys[party]
             party_data["billsutilised"] = getlockdetails(driver,party_data) 
             creditlock[party] = valid_partys[party] 
   return creditlock

class Log : 
   def __init__(self,count,today,creditrelease = {}):
       self.time = datetime.now()
       self.process_time = defaultdict(lambda:-1)
       self.date = datetime.now() 
       self.count = int(count) 
       self.error = ""
       self.last = ""
       self.start_time = time.time()
       self.bills = []
       self.filtered_collection = []
       self.lines_count = {}
       self.creditlock = {}
       self.today = today 
       self.failure = False
       print(creditrelease)
       if len(creditrelease.keys()) ==  0 : 
           self.creditrelease = [] 
       else : 
           self.creditrelease =   [ data for name,data in creditrelease.items() if data["status"]  ]
       self.attrib = ["sync","prevbills","collection","order","delivery","download","printbill"]
       for name in self.attrib :
          setattr(self,name,logdict())
   def start(self) :     
       driver = login(path)
       process = self.process
       args = (driver,)
       process("sync",args)
       process("prevbills",args)
       process("collection",args)
       #process("order",args)
       self.Order(driver)
       process("delivery",args)
       if "bills" in self.__dict__.keys()  and self.bills is not None and len(self.bills) != 0 :
           process("download",args)
           process("printbill",args)
       self.stop_time = time.time()
       self.time  = self.stop_time - self.start_time
   def process(self,name,args) : 
      start_time = time.time()
      getattr(self,name).status = 2
      try : 
       getattr(self,name).log =  getattr(self,name[0].upper() + name[1:])(*args) 
       getattr(self,name).status = 1  
      except Exception as e: 
       getattr(self,name).log = str(e)
       getattr(self,name).status = -1
       self.error = str(e)
       self.failure =  True
      self.process_time[name] = time.time() - start_time 
      print(name , ' : ',getattr(self,name).log )
   def Sync(self,driver) : 
       self.sync.ajax = getajax('sync')
       return driver.execute_script(self.sync.ajax)
   def Prevbills(self,driver) :
       self.prevbills.ajax = getajax('getdelivery')
       prevbills = driver.execute_script(self.prevbills.ajax)['billHdBeanList']
       if prevbills == None :
          prevbills = []
       return [bill['blhRefrNo'] for bill in prevbills ]
   def Collection(self,driver) :
       self.marketorder = data_ajax(driver,"getmarketorder",{"url" : "/rsunify/app/quantumImport/validateload.do","importdate":(self.date- timedelta(days = 1 )).strftime("%Y-%m-%d"),
                                      "orderdate":(self.date- timedelta(days = 1 )).strftime("%Y-%m-%d")})
       collection_data = self.marketorder["quantumCollectionList"]
       self.filtered_collection = [ collection for collection in collection_data  if collection["parCode"] not in self.today.collection ] 
       return data_ajax(driver,"setcollection",{"url" : "/rsunify/app/quantumImport/importSelectedCollection",
                                "date":self.date.strftime("%d/%m/%Y"), "rand": random.randint(100,999) ,"collections" : json.dumps(self.filtered_collection) })
   def Order(self,driver) :
      pdata = self.creditrelease.copy()
      creditunlock(driver,pdata)
      order_data = self.marketorder["quantumImportList"]
      orders = defaultdict(list)
      for order in order_data : 
          orders[order["orderNumber"]].append(order) 
      def filterorders() :
          filtered = [] 
          for orderno , items in  orders.items() :
             itm_det = items[0]
             if (orderno in self.allowed_bills and len(items) <= self.count and "WHOLE" not in itm_det["mkmName"]   and 
                                                         sum( [ item["tur"]*item["totAllocQty"] for item in items ] ) > 100)  :
                 filtered += items
          return filtered 
      self.lines_count = { orderno:len(order) for orderno,order in orders.items() } #dummy rechanged
      self.allowed_bills = []
      self.repeated_bills = []
      for orderno,lines in self.lines_count.items() : 
        if orderno not in self.today.lines_count.keys() :
            self.allowed_bills.append(orderno)
        else :
            if self.today.lines_count[orderno] == lines : 
                self.allowed_bills.append(orderno)
            else :
                self.repeated_bills.append(orderno)
      filtered = filterorders()
      self.orders = filtered 
      valid_partys = defaultdict(lambda : {"billvalue" : 0 } )
      for order in  self.orders : 
         if order["assignQty"] != 0 : 
               billvalue = valid_partys[order["parName"].replace(' ','')]["billvalue"] + (order["tur"]*order["assignQty"]) 
               valid_partys[order["parName"].replace(' ','')] = {"parCode": order["parCode"] , "parCodeHll": order["parCodeHll"],
                             "billvalue":round(billvalue,2)  ,"salesman":order["salName"],"parCodeRef": order["parCodeRef"] , "parId": order["parId"],"status":False }
      self.order.log  =  data_ajax(driver,"setmarketorder",{"url" : "/rsunify/app/quantumImport/importSelected","date":self.date.strftime("%d/%m/%Y"),
                          "rand": random.randint(100,999) ,"orders" : json.dumps(filtered) }) 
      logfilepath = self.order.log["filePath"]
      logfile = download(driver,logfilepath,override = True)
      self.logfile = logfile 
      self.creditlock = interpret(logfile,valid_partys,driver)
      return self.order.log 
   def Delivery(self,driver) : 
     delivery_all_json = driver.execute_script(getajax('getdelivery'))['billHdBeanList']
     delivery_all_json = delivery_all_json if delivery_all_json is not None else [] #None error tto empty list 
     self.allbills  =  [ bill['blhRefrNo'] for bill in delivery_all_json ]
     delivery_bills_json = [bill for bill in delivery_all_json if bill['blhRefrNo'] not in self.prevbills.log ]
     self.detailed_bills = delivery_bills_json
     self.bills =  [  bill['blhRefrNo'] for bill in delivery_bills_json ]
     self.delivery.ajax = getajax('setdelivery').replace('_data_',json.dumps(delivery_bills_json))
     result = "No Bills" if self.bills==None else driver.execute_script(self.delivery.ajax)['result']
     return result
   def Download(self,driver) :
      self.billfrom = str(self.bills[0])
      self.billto = str(self.bills[-1])
      _pdf = getajax('billpdf').replace('_billfrom_',self.billfrom).replace('_billto_',self.billto) 
      _txt = getajax('billtxt').replace('_billfrom_',self.billfrom).replace('_billto_',self.billto)
      intial = listdir(path) 
      pdf = driver.execute_script(_pdf).split('/')[-1]
      txt = driver.execute_script(_txt).split('/')[-1]
      for sleep in range(0,200) : 
        files = list( (set(listdir(path))^set(intial))& set(listdir(path)) )
        if pdf in files and txt in files :
            self.pdf = pdf 
            self.txt = txt 
            break 
        else :
            time.sleep(0.5)
      return (pdf,txt)
   def Printbill(self,driver,print_type = {"original":1,"duplicate":1}) : 
     original = self.pdf 
     duplicate = self.txt 
     rename(path+original,path+'output\\'+original)
     secondarybills.main(path+duplicate,path+'output\\'+duplicate.split('.')[0]+'.docx')
     self.secondcopy = path+'output\\'+duplicate.split('.')[0]+'.docx' 
     self.firstcopy = path+'output\\'+original  
     for i in range(0,print_type["duplicate"] ) :  
        win32api.ShellExecute (0,'print',path+'output\\'+duplicate.split('.')[0]+'.docx',None, '.', 0 )
     for i in range(0,print_type["original"] ) :
        win32api.ShellExecute (0,'print',path+'output\\'+original,None, '.', 0 )
     return "Finished Printing"
   def status(self) :
     res = {}
     for attr in self.attrib : 
       attrib = getattr(self,attr)   
       classes =  ["unactive","green","blink","red"] 
       res[attr] = {"status" : attrib.status , "log":attrib.log ,"time": round(self.process_time[attr],2) ,
                    "class" : (classes[attrib.status]) } 
     return res 
   def manualprint(self,bills_list,print_type) : 
       driver = login(path) 
       for bills in bills_list : 
            self.bills = bills 
            self.Download(driver) 
            self.Printbill(driver,print_type) 
            print("finsihed : ",self.bills)
            
            
