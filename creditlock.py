from IMP.main import * 
import json 
with open('creditschema.json') as f : 
    schema = json.loads(f.read())

def releaseslock(driver,partyid) : 
 date = driver.execute_script(" return new Date().getTime() ")
 party_base = ("D-"+str(partyid).split('-')[1]).upper()
 party_div = str(partyid).split("-")[0] 
 load = ajax_plain(driver,"/rsunify/app/partyMasterScreen/retrivePartyMasterScreenData?partyCode="+party_base+"&_="+str(date) )
 data = {}
 for key,value in schema.items() :
    val = load[0][value[0]] 
    if value[1] == "int" : 
        val = int(val) 
    elif value[1] == "float" : 
        val = float(val)
    else : 
        val = str(val)
    data[key] = val 
 clg = [] 
 divsion_map = {"D":"DETS","P":"PPA","N":"NUTS","F":"FNB" }
 for partyclg in load[1:]  : 
    temp = {'partyPlg': 8, 'noOfCrditBills': 2 , 'creditLimit': 1 , 'creditPeriod': 3 }
    tempclg = {}
    for key,value in temp.items() :
        
        tempclg[key] = str(partyclg[value])
    clg.append(tempclg)  
 data["partyCreditPlgDetails"] = clg 
 data = str(data) 
 data = data.replace("NaN","null")
 result = data_ajax(driver,"setcredit",{"url":'/rsunify/app/partyMasterScreen/savePartyMasterScreenData', "data" : data },"form") 
 console.log(result)

def getlockdetails(driver,party_data) :  
  url_rec = 'https://leveredge102.hulcd.com/rsunify/app/billing/partyinfo.do?partyId=_parId_&partyCode=_parCode_&parCodeRef=_parCodeRef_&parHllCode=_parCodeHll_&plgFlag=true&salChnlCode=&isMigration=true&blhSourceOfOrder=0'
  for key,value in party_data.items() : 
      url_rec = url_rec.replace('_'+key+'_',str(value))
  req = ajax_plain(driver,url_rec)  
  outstanding = req["collectionPendingBillVOList"] 
  breakup = [ [bill["pendingDays"],bill["outstanding"]]  for bill in outstanding ]
  breakup.sort(key=lambda x: x[0],reverse=True)
  breakup = "/".join( [ str(bill[0])+"*"+str(bill[1]) for bill in breakup ] )
  return { "billsutilised" : req["creditBillsUtilised"] , "creditlimit": breakup } 

def releaselock(driver,party_data) :  
  # party_data = { "parCode": "P-P18078" , "parCodeHll": "HUL-413724D-P3364","parCodeRef": "D-P18078" , "parId": 5582 }
  url_rec = 'https://leveredge102.hulcd.com/rsunify/app/billing/partyinfo.do?partyId=_parId_&partyCode=_parCode_&parCodeRef=_parCodeRef_&parHllCode=_parCodeHll_&plgFlag=true&salChnlCode=&isMigration=true&blhSourceOfOrder=0'
  for key,value in party_data.items() : 
      url_rec = url_rec.replace('_'+key+'_',str(value))
  req = ajax_plain(driver,url_rec)
  
  response = {"parCodeRef":party_data["parCodeRef"] ,"parCodeHll":party_data["parCodeHll"] ,"showPLG":req["showPLG"], "creditLimit":req["creditLimit"],
                 "creditDays":req["creditDays"],"newlimit":int(req["creditBillsUtilised"])+1  } 
  url_send = 'https://leveredge102.hulcd.com/rsunify/app/billing/updatepartyinfo.do?partyCodeRef=_parCodeRef_&creditBills=_newlimit_&creditLimit=_creditLimit_&creditDays=0&panNumber=&servicingPlgValue=_showPLG_&plgPartyCredit=true&parHllCode=_parCodeHll_'
  for key,value in response.items() : 
      url_send = url_send.replace('_'+key+'_',str(value))
  url_send = url_send.replace('+','%2B')
  res = ajax_plain(driver,url_send) 
  
  
  
  
  
  
  



#null = { parHULCreditBills,parHULCreditLimit ,parHULCreditDays ,parDETSCreditBills ,parDETSCreditLimit ,parDETSCreditDays ,parFNBCreditBills ,parFNBCreditLimit ,parFNBCreditDays ,parPPCreditBills ,parPPCreditLimit ,parPPCreditDays }