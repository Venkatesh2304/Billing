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

def get(self,critical_lines=10) :
 def getajax(name) :
     return ajax.split('_'+name+'_')[1]
 with open('ajax.txt') as f :
     ajax = f.read()
 global driver
 driver = login(path)
 date=datetime.now() 
 driver.maximize_window()
 
 self.on("sync")
 self.sync["log"] = driver.execute_script(getajax('sync'))
 self.off("sync")

 self.on("prevbills")
 prevbills = driver.execute_script(getajax('getdelivery'))['billHdBeanList']
 if prevbills == None :
     prevbills = []
 self.prevbills["log"] = [bill['blhRefrNo'] for bill in prevbills ]
 self.off("prevbills")

 self.on("collection")
 data = data_ajax(driver,"getmarketorder",{"url" : "/rsunify/app/quantumImport/validateload.do","importdate":(date- timedelta(days = 1 )).strftime("%Y-%m-%d"),
                                      "orderdate":(date- timedelta(days = 1 )).strftime("%Y-%m-%d")})
 collection_data = data["quantumCollectionList"]
 self.collection["log"] = data_ajax(driver,"setcollection",{"url" : "/rsunify/app/quantumImport/importSelectedCollection","date":date.strftime("%d/%m/%Y"),
                     "rand": random.randint(100,999) ,"collections" : json.dumps(collection_data) }) 
 self.off("collection")

 self.on("order")
 order_data = data["quantumImportList"]
 orders = defaultdict(list)
 for order in order_data : 
     orders[order["orderNumber"]].append(order)
 def filterorders() :
     filtered = [] 
     for orderno , items in  orders.items() :
        itm_det = items[0]
        if len(items) <= 50 and "WHOLE" not in itm_det["mkmName"]   :
            filtered += items
     return filtered 
 filtered = filterorders()
 print(set([shop["parName"] for shop in filtered ]))
 x = input()
 self.order["log"] = data_ajax(driver,"setmarketorder",{"url" : "/rsunify/app/quantumImport/importSelected","date":date.strftime("%d/%m/%Y"),
                     "rand": random.randint(100,999) ,"orders" : json.dumps(filtered) }) 
 logfilepath = self.order["log"]["filePath"]
 logfile = download(driver,logfilepath,override = True)
 self.off("delivery")

 self.on("delivery")
 bills = driver.execute_script(getajax('getdelivery'))['billHdBeanList']
 bills = [bill for bill in bills if bill['blhRefrNo'] not in prevbills ]
 setdelivery = getajax('setdelivery').replace('_data_',json.dumps(bills))
 self.delivery["log"] = setdelivery 
 self.off("delivery")

 if bills!=None :
  result = driver.execute_script(setdelivery)['result'] 
 if bills != None : 
  billfrom = str(bills[0]['blhRefrNo'])
  billto = str(bills[-1]['blhRefrNo'])
 else :
     return "No bills available"
 _pdf = getajax('billpdf').replace('_billfrom_',billfrom).replace('_billto_',billto) 
 _txt = getajax('billtxt').replace('_billfrom_',billfrom).replace('_billto_',billto)
 intial = listdir(path) 
 try :
  pdf = driver.execute_script(_pdf)
  txt = driver.execute_script(_txt)
  for sleep in range(0,200) : 
     files = list( (set(listdir(path))^set(intial))& set(listdir(path)) )
     if pdf in files and txt in files :
         return {'pdf':pdf,'txt':txt,'bills':billfrom+'-'+billto}
     else :
         time.sleep(0.5)
 except Exception as e :
   print("Bill Downloaded failed")
   print("Error : ",e)
   return "Bill Download Failed "


class Log : 
   def __init__(self,count):
       self.time = datetime.now()
       self.count = count 
       self.error = ""
       self.last = ""
       self.start = time.time()
       attributes = ["sync","prevbills" , "collection" , "order" ,"delivery" ,"download"]
       for name in attributes : 
        setattr(self,name,{"status":0,"log":""})
       self.files  = get(self,count)
       try : 
           self.files  = get(self,count)  
       except Exception as e : 
           self.total_time = time.time() - self.start 
           self.error = e 
           self.files  = None
       self.total_time = time.time() - self.start
   def on(self,name) : 
       getattr(self,name)["status"] = 1
       print("Started ",name)
   def off(self,name) :
       getattr(self,name)["status"] = 0
       print(getattr(self,name)["log"])
       print("Ended ",name)
   def report(self) : 
       for key , value in self.__dict__() :
           print(key,' : ',value)




path='D:\\dataprint\\'
def main(count_bills=10) :
   start = time.time()
   log = Log(count_bills)
   files = log.files 
   if files is None : 
       print("Failed")
   if type(files) == str : 
        print(files)
        return False 
   elif type(files) == dict : 
         orignal = files['pdf']
         duplicate = files['txt']
         bills = files['bills']
   else :
       print("Something wen wrong(files) : ",files,type(files))
       return False
   rename(path+orignal,path+'output\\'+orignal)
   print("ok")
   secondarybills.main(path+duplicate,path+'output\\'+duplicate.split('.')[0]+'.docx')

   log.secondcopy = path+'output\\'+duplicate.split('.')[0]+'.docx' 
   log.firstcopy = path+'output\\'+orignal

   win32api.ShellExecute (0,'print',path+'output\\'+duplicate.split('.')[0]+'.docx',None, '.', 0 )
   win32api.ShellExecute (0,'print',path+'output\\'+orignal,None, '.', 0 )
   print('sucessfully finsihed in',time.time() -start,'seconds')
   logs = []
   #with open('log.pkl') as f : 
   #   logs = pickle.load()
   logs.append(log)
   if len(logs) > 1000 : 
       logs = logs[-1000:]
   with open('log.pkl','w+') as f :
     pickle.dump(f,logs)
       


main(10)

