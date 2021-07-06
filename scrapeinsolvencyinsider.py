from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import urllib3
import re
import time
import pandas as pd


def scrape(chromedriver="C:/Users/Robpr/OneDrive/Documents/chromedriver.exe"):
        
    # Create driver object. Opens browser
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # Goes to insolvency insider.
    driver.get("https://insolvencyinsider.ca/filing/")

    # Creates "load more" button object.
    loadMore = driver.find_element_by_xpath(xpath="/html/body/div[2]/div/main/div/div/div/button")

    # Gets web page source code as str
    url = "https://insolvencyinsider.ca/filing/"
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    text = str(r.data)

    # Creates Match objects 
    totalPagesObj = re.search(pattern='"total_pages":\d+', string=text)

    # The matched pattern
    totalPagesStr = totalPagesObj.group(0)

    # Finds the digits of the matched pattern and converts them to int
    totalPages = int((re.search(pattern="\d+", string=totalPagesStr)).group(0))

    # Clicks the Load more button (total pages - 1) times with a three second delay.
    for i in range(totalPages-1):
        loadMore.click()
        time.sleep(3)

    # Creates a list of filing name elements and a list of filing date elements.
    filingNamesElements = driver.find_elements_by_class_name("filing-name")
    filingDateElements = driver.find_elements_by_class_name("filing-date")
    filingHrefElements = driver.find_elements_by_xpath("//*[@id='content']/div[2]/div/div[1]/h3/a")

    # For each filing name, gets the meta data associated with filing and puts it in a list.
    filingMetas = []
    for i in range(len(filingNamesElements) + 1):
        filingMetai = driver.find_elements_by_xpath(("//*[@id='content']/div[2]/div[%d]/div[2]/div[1]" %(i)))
        for element in filingMetai:
            filingMetaTexti = element.text
            filingMetas.append(filingMetaTexti)

    # For each filing, appends meta data to dict.
    metaDict = {"Filing Type": [], "Industry": [], "Province": []}
    for filing in filingMetas:
        filingSplit = filing.split("\n")
            
        for item in filingSplit:
            itemSplit = item.split(": ")
                
            if itemSplit[0] == "Filing Type":
                metaDict["Filing Type"].append(itemSplit[1])
            elif itemSplit[0] == "Industry":
                metaDict["Industry"].append(itemSplit[1])
            elif itemSplit[0] == "Province":
                metaDict["Province"].append(itemSplit[1])

        # Appends "NA" if filing does not contain filing type, industry, or province.       
        if "Filing Type" not in filing:
            metaDict["Filing Type"].append("NA")
        elif "Industry" not in filing:
            metaDict["Industry"].append("NA")
        elif "Province" not in filing:
            metaDict["Province"].append("NA")

    # Initiates a list for filing names and a list for filing dates.
    filingName = []
    filingDate = []
    filingLink = []

    # for each element in filing name elements list, appends the element's text to the filing names list.
    for element in filingNamesElements:
        filingName.append(element.text)

    # for each element in filing date elements list, appends the element's text to the filing dates list.
    for element in filingDateElements:
        filingDate.append(element.text)
    
    # For each element in filing href elements list, appends the element's href to filing links list.
    for link in filingHrefElements:
        if link.get_attribute("href"):
            filingLink.append(link.get_attribute("href"))

    # Creates a final dictionary with filing names and dates.
    fullDict = {
        "Filing Name": filingName,
        "Filing Date": filingDate, 
        "Filing Type": metaDict["Filing Type"],
        "Industry": metaDict["Industry"],
        "Province": metaDict["Province"],
        "Link": filingLink
    }

    # Creates a data frame.
    df = pd.DataFrame(fullDict, columns=["Filing Name", "Filing Date", "Filing Type", "Industry", "Province", "Link"])
    # df["Filing Date"] = pd.to_datetime(df["Filing Date"], infer_datetime_format=True)

    return df
