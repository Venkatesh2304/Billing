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
import pickle
import os
import webbrowser
app = Flask(__name__)
@app.route('/billdownload/<x>',methods=['POST','GET'])
def download(x) :
    return send_file('D:\\dataprint\\output\\'+x,as_attachment=True)
@app.route('/billquery')
def query() :
    f=open('todaybills.txt')
    x=eval(f.read())
    return render_template('query.html',values=x)
@app.route('/billprint')
def billprint() :
    f=open('config.txt')
    config=eval(f.read())
    f.close()
    return render_template('billprint.html',name=config['name'])
@app.route('/print',methods=['POST'])
def prints() :
    if useraccess['bill']==False :
        return "Contact Developer ( 6382247549 )"
    bills=[]
    print(request.method)
    print(request.form)
    types=request.form['types']
    if types=='Second Copy' :
        types=1
    else :
        types=2
    x=request.form['p']
    for i in x.split('**') :
        if i=='' :
            continue
        else :
            try :
              billfrom=i.split('-')[0]
              billto=i.split('-')[1]
              bills.append([billfrom,billto])
            except Exception as e:
                print(e)
    #dataprint
    bills1=[]
    for i in bills :
      if i not in bills1 :
          bills1.append(i)
    path='D:\\dataprint\\'
    y=downbills.main(bills,path,int(types))
    return redirect('/billprint')
@app.route('/start/<count_bills>')
def start(count_bills) :
    if useraccess['bill']==False :
        return "Contact Developer ( 6382247549 )"
    #importbills.main(int(count_bills))
    global log 
    log = Log(50)
    log.start()
    return render_template('start.html')

@app.route('/status')
def status() :
    print(log.__dict__)
    return  "1"
 

@app.route('/billindex')
def index() :
    if useraccess['bill']==False :
        return "Contact Developer ( 6382247549 )"
    return render_template('index.html')
log = 0 
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
f=open('config.bin','rb')
userdata=pickle.load(f)
f.close()
doc_ref = db.collection(u'user').document(userdata['user'])
doc = doc_ref.get()
if doc.exists:
    global useraccess
    useraccess=doc.to_dict()
else :
    print('Contact Developer')
    sys.exit()
webbrowser.open('http://127.0.0.1:5000/billindex')
app.run(threaded=True)
