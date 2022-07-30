import gspread
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json

print("Program started!")
gc = gspread.service_account(filename="ADDYOUROWN.json")  # Add your own JSON, generated from Google.
sheet = gc.open('').sheet1  # Put your own sheet here
sheet2 = gc.open('').get_worksheet(1)  # Put your own sheet here
options = Options()
options.headless = True
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(options=options)  # Remember to download and use your own webdriver.

print("Starting data collection...")

browser.get("https://tiktok.com/")
count = 0

IDs = set({})
hashtags = dict({})
while count < 10000:
    try:
        browser.refresh()
        html = browser.execute_script("return document.documentElement.outerHTML;")
        soup = BeautifulSoup(html, "html.parser")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        data = soup.find("script", {"id": "SIGI_STATE", "type": "application/json"})
        if data.text is not None:
            data = json.loads(data.text)
        for i in data["ItemModule"]:
            if i in IDs:
                print("duplicate")
                continue
            else:
                IDs.add(i)
            if count == 10000:
                break
            if count % 50 == 0 and count >= 50:
                time.sleep(60)
            count += 1
            print("Currently on Tiktok #" + str(count))
            duet = False

            # Using strings as bools
            # to stay consistent with
            # formatting

            if data["ItemModule"][i]["duetInfo"]["duetFromId"] != "0":
                duet = True
            stuff = {"Author": data["ItemModule"][i]["author"],
                     "Link": "https://tiktok.com/@" + data["ItemModule"][i]["author"] + "/video/" + i,
                     "Duration": data["ItemModule"][i]["video"]["duration"],
                     "Original Music": data["ItemModule"][i]["music"]["original"],
                     "Description": data["ItemModule"][i]["desc"],
                     "Desc. Length": len(data["ItemModule"][i]["desc"]),
                     "Likes": data["ItemModule"][i]["stats"]["diggCount"],
                     "Shares": data["ItemModule"][i]["stats"]["shareCount"],
                     "Comments": data["ItemModule"][i]["stats"]["commentCount"],
                     "Plays": data["ItemModule"][i]["stats"]["playCount"],
                     "Duet": duet,
                     "Verified": data["UserModule"]["users"][data["ItemModule"][i]["author"]]["verified"],
                     "Hashtag #": len(data["ItemModule"][i]["challenges"]),
                     }
            sheet.append_row([stuff["Author"], stuff["Link"], stuff["Duration"], stuff["Original Music"],
                              stuff["Description"], int(stuff["Desc. Length"]), int(stuff["Likes"]), int(stuff["Shares"]),
                              int(stuff["Comments"]), int(stuff["Plays"]), stuff["Duet"], stuff["Verified"],
                              stuff["Hashtag #"]])

            for j in range(0, len(data["ItemModule"][i]["challenges"])):
                if data["ItemModule"][i]["challenges"][j]["title"] in hashtags:
                    hashtags[data["ItemModule"][i]["challenges"][j]["title"]] += 1
                else:
                    hashtags[data["ItemModule"][i]["challenges"][j]["title"]] = 1

    except:
        print("Something went wrong. In most cases, the program should resume normally.")
        time.sleep(5)
hashtags = reversed(sorted(hashtags.items(), key=lambda x: x[1]))
count = 0
for i in hashtags:
    if i[1] < 5:
        break
    count += 1
    print("Currently on hashtag #" + str(count))
    sheet2.append_row([i[0], int(i[1])])
    time.sleep(2)

print("Program has finished.")
