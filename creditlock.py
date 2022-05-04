from IMP.main import * 
import json 
with open('creditschema.json') as f : 
    schema = json.loads(f.read())
path = "D:\\"
driver = login(path)
load = ajax_plain(driver,"/rsunify/app/partyMasterScreen/retrivePartyMasterScreenData?partyCode=D-P1511&_=1651643417816")
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
	




#null = { parHULCreditBills,parHULCreditLimit ,parHULCreditDays ,parDETSCreditBills ,parDETSCreditLimit ,parDETSCreditDays ,parFNBCreditBills ,parFNBCreditLimit ,parFNBCreditDays ,parPPCreditBills ,parPPCreditLimit ,parPPCreditDays }