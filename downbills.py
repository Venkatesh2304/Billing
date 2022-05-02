from selenium import webdriver
import os
import secondarybills
import win32api
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
def waituntil(x,y=60) :
 global driver
 for i in range(y):
  try :
    driver.execute_script(x)
    break
  except:
    time.sleep(1)
    print(1,x)
 if i==y:
   try :
     driver.execute_script('document.querySelector("body > div.panel.window.ui-draggable.ui-resizable.ui-resizable-disabled.messager-window > div.dialog-button.messager-button > a").click();')    
     time.sleep(1)
     driver.execute_script(x)
   except :
    x=1/0
def main(bills,path,types) :
    global driver
    path='D:\\dataprint\\'
    f=open('config.txt')
    config=eval(f.read())
    sleeptime=int(config['sleeptime'])
    headless=config['headless']
    user=config['user']
    password=config['pass']
    rs=config['rs']
    website=config['website']
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    prefs = {'download.default_directory' : path }
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(r'chromedriver.exe',options=options)
    driver.maximize_window()
    driver.get(website)
    searchbox = driver.find_element_by_xpath('//*[@id="userName"]')
    searchbox.send_keys(user)
    searchbox1 = driver.find_element_by_xpath('//*[@id="password"]')
    searchbox1.send_keys(password)
    searchbox = driver.find_element_by_xpath('//*[@id="databaseName"]')
    searchbox.send_keys(rs)
    but = driver.find_element_by_xpath('//*[@id="gologin"]')
    but.click()
    #checking for captcha and fro login loading main page 
    while True:
     try :
      menu=driver.find_element(By.ID, "ikea_home_menu_search") 
      break
     except :
      captcha=driver.find_element(By.ID,'cap_question')
      captcha=captcha.get_attribute('innerText')
      captcha=captcha.replace('=','')
      captcha=captcha.split('+')
      try :
       captcha=[int(i.strip()) for i in captcha]
      except :
        time.sleep(0.5)
        continue
      value=sum(captcha)
      driver.execute_script('document.getElementById("cap_answer").value='+str(value))
      driver.execute_script('confirmSubmission();')
      for s in range(60) :
       try :
        menu=driver.find_element(By.ID, "ikea_home_menu_search")
        break
       except :
           time.sleep(1)
      break
    menu.send_keys('bill printing')
    time.sleep(0.5)
    driver.execute_script('document.querySelector("#search_menu_item_container > div:nth-child(1)").click();')
    intial = os.listdir(path)
    times=0
    time.sleep(5)
    if types==2 :
     for i in bills :
       intials=os.listdir(path)
       waituntil('document.querySelector("#bp_billFrom").value="'+i[0]+'";')
       waituntil('document.querySelector("#bp_billTo").value="'+i[1]+'";')
       waituntil('document.querySelector("#rsu-popup-bill_printing > div.rsu-popup-action-bar > div > div > div > a.rsu-btn.rsu-btn-small.rsu-popup-action-btn.rsu-popup-action-print.horizontal").click()')
       while True :
          if len(os.listdir(path))==len(intials)+1 :
              break
          else :
              time.sleep(0.5)
       waituntil('document.querySelector("#rsu-popup-bill_printing > div.rsu-popup-action-bar > div > div > div > a.rsu-btn.rsu-btn-small.rsu-popup-action-btn.rsu-popup-action-preview.horizontal").click();')
       waituntil('document.querySelector("body > div.rsu-popup-ghost-back.rsu-popup-ghost-back-sub-popup.rsu-popup-print-dialog-ghost-back > div > a.preview-btn.preview-popup-download").click();')
       waituntil('document.querySelector("body > div.rsu-popup-ghost-back.rsu-popup-ghost-back-sub-popup.rsu-popup-print-dialog-ghost-back > div > a.rsu-print-dialog-close-btn.print-preview-class").click();')
       while True :
          if len(os.listdir(path))==len(intials)+2 :
              break
          else :
              time.sleep(0.5)
       time.sleep(1)
     time.sleep(5)
     if (len(bills)*2)+len(intial) != len(os.listdir(path)) :
         time.sleep(10)
    else :
     for i in bills :
       intials=os.listdir(path)
       if times==0 :
        time.sleep(5)
       driver.execute_script('document.getElementById("bp_billFrom").value="'+i[0]+'";')
       driver.execute_script('document.getElementById("bp_billTo").value="'+i[1]+'";')
       driver.find_element(By.LINK_TEXT, "Print").click()
       for s in range(15):
        if len(list((set(os.listdir(path))^set(intials))&set(os.listdir(path))))==1  :
          if 'tmp' not in list((set(os.listdir(path))^set(intials))&set(os.listdir(path)))[0] and 'crd' not in list((set(os.listdir(path))^set(intials))&set(os.listdir(path)))[0] :
              break
        else :
            time.sleep(1)
       times+=1
    time.sleep(2)
    driver.quit()
    bills= list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))
    x=''
    for i in bills :
      try :
        if '.txt' in i :
         f=open(path+i)
         x=x+f.read()
         f.close()
      except :
          continue
    f=open('recentmanual.txt','w')
    f.write(x)
    f.close()
    secondarybills.main('recentmanual.txt','recentmanual.docx')
    win32api.ShellExecute (0,'print','recentmanual.docx',None, '.', 0 )
    if types==2 :
     for i in bills :
        if 'PDF' in i :
          win32api.ShellExecute (0,'print',path+i,None, '.', 0 )

    return 0 
