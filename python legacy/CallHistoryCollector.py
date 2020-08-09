import glob
from openpyxl import Workbook
from openpyxl import load_workbook
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from Utilities import formatNumber
from Utilities import indexOfLastDigit
import time
from tkinter import filedialog
from datetime import datetime
from Utilities import parseDateTime


class NotImplementedException(Exception):
    def __init__(self, message):
        self.message = message


def getCallType(fileName):
    if "Voicemail" in fileName:
        return "Voicemail"
    elif "Missed" in fileName:
        return "Missed"
    elif "Placed" in fileName:
        return "Placed"
    elif "Text" in fileName:
        return "MMS"
    elif "Received" in fileName:
        return "Answered"
    raise NotImplementedException(fileName + " Contains a call type that has not been implemented yet")


def isContact(fileName):
    try:
        return (True, fileName.index('+') + 2, fileName.index('-') - 1)
    except:
        return (False, fileName.rindex('/') + 1, fileName.index(' ') - 1)


def requestBoolean(question):
    while True:
        prompt = input(question)
        if prompt == "True":
            return True
        if prompt == "False":
            return False
        print("Enter response in the format: (True) or (False) *Without parenthesis")


def requestDateTime(question):
    while True:
        try:
            return datetime.fromisoformat(input(question))
        except:
            return requestDateTime("The date you specified is not in ISO format" + question)


def getDate(elem):
    sortValue = list(numberdict[elem])[0]
    if sortValue is not datetime:
        return datetime.combine(sortValue, datetime.min.time())
    return sortValue


# user input
print("Enter path to files")
filepath = filedialog.askdirectory() + "/*.html"
ignoreUnknownNumbers = requestBoolean("Ignore Restricted Numbers? True or False?")
checkDateRange = requestBoolean("Would you like to filter based on a specific date range? True or False?")
if checkDateRange:
    start_date = requestDateTime("Please enter the start date in ISO format YYYY-MM-DD")
    end_date = requestDateTime("Please enter the end date in ISO format YYYY-MM-DD")

# start data collecting
start_time = time.time()
numberdict = dict()
# start webdriver
driver = Chrome(executable_path="C:/WebDriver/bin/chromedriver.exe")

directoryList = glob.glob(filepath)
lastProgress = 0
for currentFileIndex, fileName in enumerate(directoryList):
    # counter
    if (currentFileIndex / len(directoryList)) - lastProgress >= .01:
        print("Current Progress: {}/{} {}".format(currentFileIndex, len(directoryList),
                                                  (currentFileIndex / len(directoryList)) * 100))
        lastProgress = currentFileIndex / len(directoryList)
    currentFileIndex += 1
    # collect date
    try:
        foundDateTime = parseDateTime(fileName)
    except:
        continue
    # date filter
    if checkDateRange:
        if foundDateTime is not datetime:
            if not start_date <= datetime.combine(foundDateTime, datetime.min.time()) <= end_date:
                continue
        else:
            if not start_date <= foundDateTime <= end_date:
                continue
    # get call type
    try:
        callType = getCallType(fileName)
    except NotImplementedException as err:
        print(err)
        continue
    # filter call types
    if callType == "MMS":
        continue

    driver.get(fileName)
    contactInfo = isContact(fileName)
    if contactInfo[0]:
        number = formatNumber(fileName[contactInfo[1]:contactInfo[2]])
    else:
        number = fileName[contactInfo[1]:contactInfo[2]]
        if ignoreUnknownNumbers:
            print(fileName + " Is unknown number")
            continue
    calldirection = None
    try:
        calldirection = driver.find_element_by_xpath("/html/body/div/div[1]").text
        if "from" in calldirection:
            calldirection = "from"
        elif "to" in calldirection:
            calldirection = "to"
    except Exception as err:
        print(str(err) + " @ " + fileName)
    callDuration = None
    if "Missed" != callType:
        try:
            callDuration = driver.find_element_by_class_name("duration").text
        except Exception as err:
            print(str(err) + " @ " + fileName)
    if number in numberdict:
        numberdict[number][foundDateTime] = [callType, calldirection, callDuration]
    else:
        numberdict[number] = dict()
        numberdict[number][foundDateTime] = [callType, calldirection, callDuration]
    if "Voicemail" == callType:
        try:
            text = driver.find_element(By.XPATH, '/html/body/div/span[3]').text
            numberdict[number][foundDateTime].append(text)
        except:
            print("Transcription unavaliable: " + fileName)
            numberdict[number][foundDateTime].append("Transcription unavailiable")
# save data to worksheet
wb = Workbook()
sheet = wb.active
row = 1
for numberToAdd in sorted(numberdict.keys(), key=getDate, reverse=True):
    sheet["A" + str(row)].value = numberToAdd
    for date in sorted(numberdict[numberToAdd].keys(), reverse=True):
        callInfo = numberdict[numberToAdd][date]
        sheet["B" + str(row)].value = callInfo[0]
        sheet["C" + str(row)].value = callInfo[1]
        sheet["D" + str(row)].value = callInfo[2]
        sheet["E" + str(row)].value = date
        if len(callInfo) > 3:
            sheet["F" + str(row)].value = callInfo[3]
        print(str(row) + str(sheet["A" + str(row)].value) + " " + str(sheet["B" + str(row)].value) + " " + str(
            sheet["C" + str(row)].value) + " " + str(sheet["D" + str(row)].value) + " " + str(
            sheet["E" + str(row)].value))
        row += 1
    row += 1

while True:
    try:
        wb.save(filedialog.asksaveasfilename(defaultextension="*.xlsx", filetypes=[("Excel document", "*.xlsx")],
                                             title="Save As: "))
        break
    except PermissionError as err:
        print(err)
        input("Try closing E:/demo.xlsx then press enter")
driver.quit()
print(numberdict)
print("Runtime: {}".format(time.time() - start_time))
