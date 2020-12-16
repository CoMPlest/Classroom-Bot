from selenium import webdriver
from selenium.webdriver.common.by import By
from threading import Timer
from datetime import datetime
from os import path
import time
import pickle
import re
from selenium.common.exceptions import NoSuchElementException

def Init():
    if (path.exists("./cookies_tmp.pickle")):
        Main()
    else:
        Login()

def Login():
    print("To use the app you need to log in to google.")
    print("A browser window will open in 5 seconds, please log in...")
    print("Please do not close the window after you logged in. It will close automatically")

    time.sleep(3)
    browser = webdriver.Chrome()
    browser.get("https://classroom.google.com/u/0/h")

    input("Please press enter if you logged in...")
    with open("./cookies_tmp.pickle", 'wb') as filehandler:
        pickle.dump(browser.get_cookies(), filehandler)
    browser.close()
    input("Start the program again to continue...")

def Main():    
    #scheduled_classes = [['Kuki', 20, 12, 35], ['Kuki', 20, 13, 45]]
    scheduled_classes = askUserForClasses()

    print("")
    print("Waiting for the right time to join...")
    for meet in scheduled_classes:
        Timer(meet[4], openGoogleMeets, meet[0:2]).start()

    

def openGoogleMeets(classroom_title, class_length):

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.default_content_setting_values.media_stream_mic" : 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.notifications": 1 
    }
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://classroom.google.com/u/0/h")

    cookies = pickle.load(open("./cookies_tmp.pickle", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.get("https://classroom.google.com/u/0/h")
    time.sleep(5)
    driver.find_element(By.XPATH, '//div[text()="'+classroom_title+'"]').click()
    time.sleep(2)

    try:
        link = re.search(r"(https:\/\/meet\.google\.com\/lookup\/.*\?authuser)", driver.page_source).group(0)
    except Exception:
        print("Could not find the classroom link")
        return
    if link == "":
        print("Could not find the classroom link")
        return
         
    driver.get(link)
    
    try:
        driver.find_element(By.XPATH, "//*[@data-tooltip='Turn off microphone (ctrl + d)']").click()
    except NoSuchElementException:
        try:
            driver.find_element(By.XPATH, "//*[@data-tooltip='Mikrofon kikapcsolása (ctrl + d)']").click()
        except NoSuchElementException:
            print("Could not find the microphone button")       

    try:
        driver.find_element(By.XPATH, "//*[@data-tooltip='Turn off camera (ctrl + e)']").click()
    except NoSuchElementException:
        try:
            driver.find_element(By.XPATH, "//*[@data-tooltip='Kamera kikapcsolása (ctrl + e)']").click()
        except NoSuchElementException:
            print("Could not find the camera button")

    time.sleep(1)

    try:
        driver.find_element(By.XPATH, '//*[text()="Join now"]').click()
    except NoSuchElementException:
        try:
            driver.find_element(By.XPATH, '//*[text()="Belépés"]').click()
        except NoSuchElementException:
            print("Could not find the join button")
    time.sleep(class_length)
    driver.close()

def askUserForClasses():
    while True:
        try:
            number_of_classes = int(input("Please specify how many classes do you want to enter(max 10): "))
            break
        except ValueError:
            print("[ERROR] Thats not a valid number of classes!")
    

    scheduled_classes = [[]] * number_of_classes
    for i in range(number_of_classes):
        print("")
        classroom_title = input(f"Please specify a classroom title for your {i+1}-th/st/nd lesson: ")
        while True:
            try:
                classroom_interval = int(input(f"Please enter the ammount of time(in seconds) you want the bot to stay in {classroom_title}: "))
                break
            except ValueError:
                print("[ERROR] Thats not a valid interval")
        while True:
            try:
                start_hour = int(input(f"Please enter the start hour of {classroom_title}: "))
                start_minute = int(input(f"Please enter the start minute of {classroom_title}: "))
            except ValueError:
                print("[ERROR] Thats not a valid time")
            if (start_hour > 24):
                print("[ERROR] Thats not a valid time")
                continue
            if (start_minute > 59):
                print("[ERROR] Thats not a valid time")
                continue
            break
        scheduled_classes[i] = [classroom_title, classroom_interval, start_hour, start_minute]

    now = datetime.today()
    for i, meet in enumerate(scheduled_classes):
        delta_time = (now.replace(day=now.day, hour=meet[2], minute=meet[3], second=0, microsecond=0) - now).seconds+1
        scheduled_classes[i].append(delta_time)
    return scheduled_classes

if __name__ == "__main__":
    Init()


