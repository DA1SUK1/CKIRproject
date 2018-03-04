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
        
def is_renewal_date(book, today):
    pdb.set_trace()
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
    
if __name__=="__main__":
    geckodriver_path = "/home/gooninn/geckodriver"
    recordfile_path = "/home/gooninn/renewal_record"
    
    today = datetime.today()
    renewaled_book = 0
    not_renewaled_book = 0
    
    userid = sys.argv[1]
    userpw = sys.argv[2]
    
    f = open(recordfile_path, "a")
    
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=options, executable_path=geckodriver_path)
    
        pnu_library_login(driver, userid, userpw)
    
        for book in get_burrowed_books(driver):
            if is_renewal_date(book, today):
                renewal(driver, book)
                renewaled_book = renewaled_book + 1
            else:
                not_renewaled_book = not_renewaled_book + 1
        
        driver.quit()
    except:
        f.write("crontab worked. but error occured in script.\n")
    finally:
        f.write(str(today.year) + "/" + str(today.month) + "/" + str(today.day) +  " " + str(today.hour) + ":" + str(today.minute) + " " + str(renewaled_book) + " book renewal\n")
        f.write(str(today.year) + "/" + str(today.month) + "/" + str(today.day) + " " + str(today.hour) + ":" + str(today.minute) + " " + str(not_renewaled_book) + " book not renewal\n")
        f.close()
