#core libraries
import time
import json
import sys
import platform
#selenium libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from selenium.common.exceptions import TimeoutException


# ################################## ADD HERE REQUIRED XPATHS ##########################################
# we are using the k and i values for figuring out the appropriate sections
# USAGE LEGEND: each tuple () is allowed to have only 4 values that are respectively
# ( 'what name to be saved', 'type', 'element whose value we want', 'xpath expression' )

def relative_xpaths(k,i):
    return [
    ('tld',
     'value',
     'text',
     "//table[contains(@class, 'gb-table')]/tbody/tr[%s]/td[%s]/div/a" % (str(k+1), str(1))
     ),
	 ('irrelevant',
     'value',
     'text',
     "//table[contains(@class, 'gb-table')]/tbody/tr[%s]/td[%s]/svg" % (str(k+1), str(2))
     ),
	 ('normal_price',
     'value',
     'text',
     "//table[contains(@class, 'gb-table')]/tbody/tr[%s]/td[%s]/span" % (str(k+1), str(3))
     ),
	 ('renew_price',
     'value',
     'text',
     "//table[contains(@class, 'gb-table')]/tbody/tr[%s]/td[%s]/div/span" % (str(k+1), str(3))
     )
	 ]


def core(drv):
    drv.execute_script("window.scrollTo(0, 1080);")
    time.sleep(0.5)
    pres4 = element_presence(drv, "//a[contains(@class, 'gb-btn gb-btn--lg gb-btn--primary')]", 5)
    if(pres4):
        pres3 = element_presence(drv, "//h2[contains(@class, 'gb-headline__title')]", 5)
        if(pres3):
            pres2 = element_presence(drv, "//table[contains(@class, 'gb-table')]", 1)
            if(pres2):
                dat = []
                showmore = element_clicable(drv, "//button[contains(@class, 'gb-btn gb-mb-6 gb-btn-show-more')]", 1)
                if(showmore):
                    showmorec = element_click(drv, "//button[contains(@class, 'gb-btn gb-mb-6 gb-btn-show-more')]")
                    pres1 = element_presence(drv, "//table[contains(@class, 'gb-table')]", 1)
                    tblrows = find_xpath_elements(drv, "//table[contains(@class, 'gb-table')]/tbody/tr")
                    for k, row in enumerate(tblrows):
                        out = {}
                        out = extract_each_row(drv, k)
                        if out and "tld" in out:
                            dat.append(out)
                newlist = sorted(dat, key=lambda k: k['renew_price'])
                return newlist


def extract_each_row(drv, k):
    out = {}
    #in this case the i is not being used! set it to some number we dont care
    i = 1
    xpaths = relative_xpaths(k,i)
    for (name, typ, attrib, xpath) in xpaths:
        if(name == "irrelevant"):
            continue
        tmp = find_xpath_element(drv, xpath)
        if(tmp):
            if(typ == "attribute"):
                out[name] = tmp.get_attribute(attrib)
                if name in out:
                    if name != "tld":
                        out[name] = (out[name][1:]).replace(',','')
                        if(out[name]):
                            out[name] = float(out[name])
            elif(typ == "value"):
                out[name] = eval("tmp.%s" % attrib)
                if name in out:
                    if name != "tld":
                        out[name] = (out[name][1:]).replace(',','')
                        if(out[name]):
                            out[name] = float(out[name])
    if "tld" in out:
        return out


def element_presence(driver, xp, tim):
    try:
        seeallo = WebDriverWait(driver, tim).until( EC.presence_of_element_located((By.XPATH, xp)) )
    except TimeoutException as ex:
        seeallo = False
        #driver.quit()
    return seeallo


def element_clicable(driver, xp, tim):
    try:
        se = WebDriverWait(driver, tim).until( EC.element_to_be_clickable((By.XPATH, xp)) )
    except TimeoutException as ex:
        se = False
        #driver.quit()
    return se


def element_click(driver, xp):
    try:
        se = WebDriverWait(driver, 1).until( EC.element_to_be_clickable((By.XPATH, xp)) ).click()
    except TimeoutException as ex:
        se = False
        #driver.quit()
    return se


def element_scroll(driver, element):
    return js_script(driver, "arguments[0].scrollIntoView();", element)


def find_xpath_element(driver, xp):
    try:
        a = driver.find_element_by_xpath(xp)
    except Exception as ex:
        #print(ex)
        a = False
        #driver.quit()
    return a


def find_xpath_elements(driver, xp):
    try:
        a = driver.find_elements_by_xpath(xp)
    except Exception as ex:
        print(ex)
        a = False
        #driver.quit()
    return a


def js_script(driver, script, argz):
    driver.execute_script(script, argz)
    return True


def driver_options():
    options = Options()
    #change headless to false if we want window of chrome to be seen!
    options.headless = False
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--incognito')
    options.add_argument('--log-level=3')
    options.add_argument('--start-maximized')
    options.add_argument('--maximized')
    options.add_argument('--whitelisted-ips')
    options.add_argument('--disable-notifications')
    return options


def get_driver():
    which = platform.system()
    if(which == 'Windows'):
        chrdriver = r"chromedriver.exe"
    else:
        chrdriver = r"/usr/lib/chromium/chromedriver"
    driver = webdriver.Chrome( chrdriver, options=driver_options() )
    return driver


# ############################################### MAIN FLOW #############################################
start_time = time.time()
url = "https://www.namecheap.com/domains/new-tlds/explore/"
drv = get_driver()
drv.get( url )
dat = core(drv)
with open('data_namecheap.json', 'w', encoding='utf-8') as f:
    json.dump(dat, f, ensure_ascii=False, indent=4)
drv.quit()
print("--- took: %s seconds ---" % (time.time() - start_time))
# ############################################## END OF MAIN FLOW #######################################
