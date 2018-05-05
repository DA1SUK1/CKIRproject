#!/usr/bin/python3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.alert import Alert
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime, date
import re
import sys
import pdb

def pnu_library_login(driver, id_string, pw_string):
    driver.get("https://lib.pusan.ac.kr/login/")  # here needs wait
    sleep(10)
    driver.find_element_by_id("id").send_keys(id_string)
    driver.find_element_by_id("pw").send_keys(pw_string)
    sleep(3)
    driver.find_element_by_class_name("btn_login").click()
    sleep(3)
    
def get_burrowed_books(driver):
    burrowed_books = []
    driver.get("https://pulip.pusan.ac.kr/mylibrary/Circulation.ax") #here needs wait
    sleep(10)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for book in soup.findAll("tr", {"class":re.compile("tbRecord*")}):
        try:  # to avoid index error by overdue days
            renewal_date = date(*(int(x) for x in book.findAll("td")[4].get_text().strip().split('/')))
            book_code = book.findAll("td")[1].get_text().strip()
            is_renewaled = True if book.findAll("td")[5].get_text().strip()[0] == '1' else False
            burrowed_books.append({"book_code":book_code, "renewal_date":renewal_date, "is_renewaled":is_renewaled})
        except IndexError:
            pass
    return sorted(burrowed_books, key = lambda k : k["is_renewaled"], reverse = True) #renewaled books come first
        
def is_renewal_day(book, today):
    #pdb.set_trace()
    if not hasattr(is_renewal_day, "renewal_to_reduce_fee"):   #for static variable in this function
        is_renewal_day.renewal_to_reduce_fee = False
      
    #pdb.set_trace()
    if today.date() == book["renewal_date"] and book["is_renewaled"] and not is_renewal_day.renewal_to_reduce_fee:
        is_renewal_day.renewal_to_reduce_fee = True
        return False
    elif book["is_renewaled"]:
        return False
    elif today.date() == book["renewal_date"] or is_renewal_day.renewal_to_reduce_fee:
        return True
    else:
        return False

def renewal(driver, book):
    driver.get("https://pulip.pusan.ac.kr/mylibrary/Circulation.ax")  #here needs wait
    sleep(10)
    driver.find_element_by_id(book[0]).click() #here needs wait
    sleep(10)
    Alert(driver).accept() #here needs wait
    sleep(10)
    Alert(driver).accept() #here needs wait
    sleep(10)
    
if __name__=="__main__":
    geckodriver_path = "/home/gooninn/geckodriver"
    recordfile_path = "/home/gooninn/renewal_record2"
    
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
    except:
        f.write("problem occured in selenium.\n\n")
        sys.exit()
        
    try:
        pnu_library_login(driver, userid, userpw)
        
        for book in get_burrowed_books(driver):
            if is_renewal_day(book, today):
                renewal(driver, book)
                renewaled_book = renewaled_book + 1
            else:
                not_renewaled_book = not_renewaled_book + 1
        
        #driver.quit()
    except:
        f.write("error occured in script.\n")
    finally:
        f.write(str(today.year) + "/" + str(today.month) + "/" + str(today.day) +  " " + str(today.hour) + ":" + str(today.minute) + " " + str(renewaled_book) + " book renewal\n")
        f.write(str(today.year) + "/" + str(today.month) + "/" + str(today.day) + " " + str(today.hour) + ":" + str(today.minute) + " " + str(not_renewaled_book) + " book not renewal\n\n")
        f.close()
        driver.quit()
