from selenium import webdriver
import os 
def main(bills,path) :
    driver.maximize_window()
    driver.get('https://leveredge102.hulcd.com/rsunify/')
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
      menu=driver.find_element(By.ID, "ikea_home_menu_search")
      break
    
    driver.click()
    driver.send_keys('bill printing')
    driver.find_element(By.CSS_SELECTOR, ".menu-active > .menu-text").click()
    initial = os.listdir(paths)
    for i in bills :
     driver.find_element(By.ID, "bp_billFrom").send_keys(i[0])
     driver.find_element(By.ID, "bp_billTo").send_keys(i[1])
     driver.find_element(By.LINK_TEXT, "Print").click()
    time.sleep(5)
    driver.quit()
    return list((set(os.listdir(path))^set(intial))&set(os.listdir(path)))
