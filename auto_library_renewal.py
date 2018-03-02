#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.alert import Alert
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import re
import sys
import pdb

def pnu_library_login(driver, id_string, pw_string):
    driver.get("https://lib.pusan.ac.kr/login/")
    sleep(10)
    driver.find_element_by_id("id").send_keys(id_string)
    driver.find_element_by_id("pw").send_keys(pw_string)
    sleep(3)
    driver.find_element_by_class_name("btn_login").click()
    sleep(3)
    
def get_burrowed_books(driver):
    driver.get("https://pulip.pusan.ac.kr/mylibrary/Circulation.ax")
    sleep(10)
    #pdb.set_trace()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for book in soup.findAll("tr", {"class":re.compile("tbRecord*")}):
        renewal_date = tuple(book.findAll("td")[4].get_text().strip().split('/'))
        renewal_code = book.findAll("td")[1].get_text().strip()
        #pdb.set_trace()
        yield (renewal_code, renewal_date)
        
def is_renewal_date(book):
    today = datetime.today()
    #pdb.set_trace()
    if today.year == int(book[1][0]) and today.month == int(book[1][1]) and today.day == int(book[1][2]):
        return True
    else:
        return False

def renewal(driver, book):
    driver.get("https://pulip.pusan.ac.kr/mylibrary/Circulation.ax")
    sleep(10)
    driver.find_element_by_id(book[0]).click()
    sleep(10)
    Alert(driver).accept()
    sleep(10)
    Alert(driver).accept()
    sleep(10)
    
def write_log(f, isRenewaled):
    today = datetime.today()
    if isRenewaled:
        f.write(str(today.year) + "/" + str(today.month) + "/" + str(today.day) + " 1 book renewal\n")
    else:
        f.write(str(today.year) + "/" + str(today.month) + "/" + str(today.day) + " " + str(today.hour) + ":" + str(today.minute) + " " + " 1 book not renewal\n")
    
if __name__=="__main__":
    geckodriver_path = "/home/gooninn/geckodriver"
    recordfile_path = "/home/gooninn/renewal_record"
    userid = sys.argv[1]
    userpw = sys.argv[2]
    
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options, executable_path=geckodriver_path)
    
    f = open(recordfile_path, "a")
    
    pnu_library_login(driver, userid, userpw)
    
    for book in get_burrowed_books(driver):
        if is_renewal_date(book):
            renewal(driver, book)
            write_log(f, True)
        else:
            #print("here\n")
            write_log(f, False)
        
    f.close()
    driver.quit()
