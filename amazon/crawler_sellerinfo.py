# -*- coding: utf-8 -*-

# @Author: Tian jingyi
# @Date: 2017/09/04
# @Contact Information:
#   WeChat: 312571106
#   QQ: 312571106
# @Usage: 亚马逊官网抓取店铺信息


from selenium import webdriver
import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql_helper
from bs4 import BeautifulSoup
import re
import codecs


logger = logging.getLogger(__name__)
data_dir = "Data\\iris_info.txt"
tproxy = "94.23.92.30:1997"


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=socks5://%s" % tproxy)
BROWSER = webdriver.Chrome(chrome_options=chrome_options)


def download(url):
    try:
        print("downloading:" + url)
        BROWSER.get(url)
        time.sleep(1)
        if BROWSER.title == "Robot Check":
            print("------------robot check------------")
            WebDriverWait(BROWSER, 2000000000).until(EC.title_contains(u"Amazon"))
        return BROWSER.page_source
    except:
        print("Download error")


def get_id(connection):
    return mysql_helper.select_id(connection)


def write_in(name, id, t_days, n_days, t_months, life_time, phone):

    file_obj1 = codecs.open(data_dir, "a", "utf-8")
    file_obj1.write(
        name
        + "||"
        + id
        + "||"
        + t_days
        + "||"
        + n_days
        + "||"
        + t_months
        + "||"
        + life_time
        + "||"
        + phone
        + "\n"
    )
    file_obj1.close()


def get_info(id):

    html = download(
        "https://www.amazon.com/sp?_encoding=UTF8&asin=&isAmazonFulfilled=1&isCBA=&marketplaceID=ATVPDKIKX0DER&orderID=&seller="
        + id
        + "&tab=&vasStoreID="
    )
    html = BeautifulSoup(html)

    phone = html.find("div", {"id": "seller-phone-number"})
    try:
        phone = phone.find("span", {"id": "seller-contact-phone"})
        phone = phone.get_text()
    except:
        phone = "null"

    # 商家名字
    name = html.find("h1", {"id": "sellerName"})
    name = name.get_text()

    # 找评价
    table = html.find("table", {"id": "feedback-summary-table"})
    tr = table.find_all("tr")
    pattern1 = re.compile('">([0-9]+)<')
    feedback = pattern1.findall(str(list(tr)[-1]))
    if feedback == None:
        write_in(name, id, "null", "null", "null", "null", phone)
        print(name, id, "null", "null", "null", "null", phone)
    else:
        print(name, id, feedback[0], feedback[1], feedback[2], feedback[3], phone)
        write_in(name, id, feedback[0], feedback[1], feedback[2], feedback[3], phone)

    return


if __name__ == "__main__":
    connection = mysql_helper.mysql_login()
    id_list = get_id(connection)
    for id in id_list:
        get_info(id)
    BROWSER.close()
