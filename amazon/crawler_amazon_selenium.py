# -*- coding: utf-8 -*-

# @Author: Tian jingyi
# @Date: 2017/09/04
# @Contact Information:
#   WeChat: 312571106
#   QQ: 312571106
# @Usage: 亚马逊官网抓取店铺信息


from selenium import webdriver
from bs4 import BeautifulSoup
import logging
import re
import codecs
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
import requests

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s",
    datefmt="%a, %d %b %Y %H:%M:%S",
    filename="crawler_amazon.log",
    filemode="w",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
}

WAITTIME = 10
data_dir = "Data\\iris"
tproxy = ""
MAXTRY = 5

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=socks5://%s" % tproxy)
BROWSER = webdriver.Chrome(chrome_options=chrome_options)


# 用selenium下载网页
def download_selenium(url, num_retries=MAXTRY):
    if num_retries < 0:
        return None
    try:
        logging.info("downloading:" + url)
        BROWSER.get(url)
        # html = BROWSER.execute_script("return document.body.innerHTML;")
        html = BROWSER.page_source
        if BROWSER.title == "Robot Check":
            logging.info("------------robot check------------")
            WebDriverWait(BROWSER, 2000000000).until(EC.title_contains(u"Amazon"))
    except Exception as e:
        logging.warning("Download error", e.reason)
        html = None
        time.sleep(WAITTIME)
        if hasattr(e, "code") and 500 <= e.code < 600:
            # recursively retry 5xx HTTP errors 判断返回的异常的代码，是否在500到600之间
            return download_selenium(url, num_retries - 1)
    return html


def download_request(url, num_retries=MAXTRY):
    if num_retries < 0:
        return None
    try:
        logging.info("downloading:" + url)
        html = requests.get(url, headers=HEADERS, timeout=WAITTIME)
        html = html.text
    except Exception as e:
        logging.warning("Download error", e.reason)
        html = None
        if hasattr(e, "code") and 500 <= e.code < 600:
            return download_request(url, num_retries - 1)
    return html


def write_in(data, data_dir):
    with codecs.open(data_dir, "a", "utf-8") as file_obj:
        file_obj.write(data)
    file_obj.close()


def get_sellers(url):
    seller_list = ""
    none_list = ""
    china_list = ""
    for url_item in url:
        i_URL = str(
            re.findall(r"""(.+?)ref=""", str(url_item), re.S)[0].strip() + "?th=1&psc=1"
        )
        try:
            time.sleep(3)
            html = download_request(i_URL)
            html = BeautifulSoup(
                html.replace("\r", "").replace("\n", "").strip(), "html.parser"
            )
            time.sleep(3)
            try:
                html = str(html).replace("&", '">')
                pattern = re.compile(r'seller=(.+?)"')
                pattern1 = re.compile(r'merchantId : "(.+?)"')
                pattern2 = re.compile(r"sold by Amazon.com")
                pattern3 = re.compile(r"(ships|shiping) from China")
                china_ex = pattern3.findall(html)
                if china_ex:
                    china_list = china_list + seller_id
                elif pattern.findall(html):
                    seller_id = pattern.findall(html)
                elif pattern1.findall(html):
                    seller_id = pattern1.findall(html)
                if seller_id:
                    for id in seller_id:
                        logging.info(seller_id)
                        if id not in seller_list:
                            seller_list = seller_list + id + "\n"
                else:
                    if not pattern2.findall(html):
                        logging.info("not sold by Amazon")
                        none_list = none_list + url_item + "\n"
                    elif pattern2.findall(html):
                        logging.info("sold by Amazon")
            except Exception as ex:
                logging.warning("can't find seller_info:", ex)
        except:
            logfil_object = open("wrong_url", "wb+")
            logfil_str = i_URL + "\n"
            print("ERR:" + logfil_str)
            logfil_object.write(logfil_str.encode("UTF-8", "ignore"))
            logfil_object.close()
    print(seller_list)
    print(none_list)
    print(china_list)
    if seller_list:
        write_in(seller_list, data_dir + "1.txt")
    if none_list:
        write_in(none_list, data_dir + "2.txt")
    if china_list:
        write_in(china_list, "Data\\china.txt")


def get_link(url):

    html = download_selenium(url)
    html = BeautifulSoup(html)
    pattern = re.compile(r'<a href="(.*?)">')
    try:
        root = html.find("span", {"class": "zg_selected"})
        try:
            bro = root.find_parent().find_next_siblings()
            try:
                bro_link = pattern.findall(str(bro))
                return bro_link
            except:
                logging.warning("can't find hrefs")
        except:
            logging.warning("the last page")
            return None
    except:
        logging.warning("can't find browseRoot")
        return None


def get_100(url):
    products_list = []
    for i in range(1, 6):
        products = ""
        logging.info(".......................page.......................")
        pattern = re.compile(r"(.*bs)")

        page_url = pattern.findall(url)
        page_url = str(page_url[0]) + "_pg_1?_encoding=UTF8&pg=" + str(i) + "&ajax=1"

        html1 = download_selenium(page_url)
        time.sleep(5)
        html = BeautifulSoup(html1, "html.parser", from_encoding="utf_8")
        products = html.find_all("div", {"class": {"zg_itemWrapper"}})
        for item in products:
            hastitle = item.find_all("a", class_="a-link-normal")
            for some in hastitle:
                if not some.has_attr("title") and "a-size-small" not in some["class"]:
                    products_url = some.get("href")
                    if (
                        "https://www.amazon.com" + products_url + ""
                    ) not in products_list:
                        products_list.append(
                            "https://www.amazon.com" + products_url + ""
                        )
    # print(products_list)
    return products_list


def crawl_all(url):
    urls_list = get_link(url)
    logging.info("所有子分类为：")
    logging.info(urls_list)
    for item in urls_list:
        logging.info("当前子分类为：")
        logging.info(item)
        products_100 = get_100(item)
        logging.info("当前子分类的前一百商品为：")
        logging.info(products_100)
        get_sellers(products_100)


if __name__ == "__main__":
    links = [
        "https://www.amazon.co.jp/%E5%B1%B1%E5%B4%8E%E5%AE%9F%E6%A5%AD-%E8%BB%BD%E9%87%8F%E4%BA%BA%E4%BD%93%E5%9E%8B%E3%82%A2%E3%82%A4%E3%83%AD%E3%83%B3%E5%8F%B0-%E3%83%95%E3%83%83%E3%82%AF%E4%BB%98%E3%81%8D-%E3%83%AC%E3%82%A4%E3%83%B3%E3%83%9C%E3%83%BC-7804/dp/B00HWJZ854/ref=zg_bs_13945161_20?_encoding=UTF8&psc=1&refRID=06291WZEGPHENNM418XY",
        "https://www.amazon.co.jp/NICHIGA-%E3%83%8B%E3%83%81%E3%82%AC-%E9%85%B8%E7%B4%A0%E7%B3%BB%E6%BC%82%E7%99%BD%E5%89%A4-3%EF%BD%8B%EF%BD%87%EF%BC%88%E9%81%8E%E7%82%AD%E9%85%B8%E3%83%8A%E3%83%88%E3%83%AA%E3%82%A6%E3%83%A0%EF%BC%89%E6%BC%82%E7%99%BD-%E5%87%84%E3%81%84%E7%A0%B4%E5%A3%8A%E5%8A%9B%EF%BC%81%E6%B4%97%E6%BF%AF%E6%A7%BD%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%8A%E3%83%BCNICHIGA/dp/B002VDE0MS/ref=zg_bs_13945161_17?_encoding=UTF8&psc=1&refRID=06291WZEGPHENNM418XY",
    ]
    print(get_sellers(links))
    for link in links:
        logging.info(".......................新的一轮开始了.......................")
        logging.info(link)
        products_100 = get_100(link)
        logging.info("当前子分类的前一百商品为：")
        logging.info(products_100)
        get_sellers(products_100)
BROWSER.close()
