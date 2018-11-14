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
WAITTIME = 10
data_dir = "Data\\ppppp"
tproxy = ""
MAXTRY = 5
# BROWSER = webdriver.Chrome()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=socks5://%s" % tproxy)
BROWSER = webdriver.Chrome(chrome_options=chrome_options)


def download_selenium(url, num_retries=MAXTRY):
    if num_retries < 0:
        return None
    try:
        logging.info("downloading:" + url)
        i_url = str(re.findall(r"""(.+?)ref=""", str(url), re.S)[0].strip())
        BROWSER.get(i_url)
        html = BROWSER.execute_script("return document.body.innerHTML;")
        time.sleep(3)
        if BROWSER.title == "Robot Check":
            logging.info("------------robot check------------")
            WebDriverWait(BROWSER, 2000000000).until(EC.title_contains(u"Amazon"))
        return BROWSER.page_source
    except Exception as e:
        logging.warning("Download error", e.reason)
        BROWSER.page_source = None
        if hasattr(e, "code") and 500 <= e.code < 600:
            # recursively retry 5xx HTTP errors 判断返回的异常的代码，是否在500到600之间
            return download_selenium(url, num_retries - 1)
    return html


def download_request(url, num_retries=MAXTRY):
    if num_retries < 0:
        return None
    try:
        i_URL = str(re.findall(r"""(.+?)ref=""", str(url), re.S)[0].strip())
        opener2 = urllib.request.build_opener()
        opener2.addheaders = [
            (
                "User-agent",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
            )
        ]
        response2 = opener2.open(i_URL, timeout=WAITTIME)
        html = response2.read()
    except Exception as e:
        logging.warning("Download error", e.reason)
        BROWSER.page_source = None
        if hasattr(e, "code") and 500 <= e.code < 600:
            # recursively retry 5xx HTTP errors 判断返回的异常的代码，是否在500到600之间
            return download_selenium(url, num_retries - 1)
    return html


def write(data, data_dir):
    with codecs.open(data_dir, "w", "utf-8") as file_obj:
        file_obj.write(data)
    file_obj.close()


def get_products(url):
    logging.info(".......................商品列表页是.......................:")
    logging.info(url)
    html = download_selenium(url)
    html = BeautifulSoup(html, "html.parser", from_encoding="utf_8")
    category = html.find_all("span", {"class": {"category"}})

    # 找到分类
    # regexstr = re.compile('<[^>]+>')
    # category = regexstr.sub("", str(category))
    # regexstr = re.compile(r'\s&amp;\s')
    # category = regexstr.sub("&", str(category))
    # data_dir ="Data\\"+category
    # print(data_dir)
    # if not (os.path.exists(data_dir + "1.txt") and os.path.exists(data_dir + "2.txt")):
    #     # 建立新的类目文件
    #     write(category+'\n', data_dir + "1.txt")
    #     write(category+'\n', data_dir + "2.txt")

    # 找到产品列表
    products_list = []
    products = html.find_all("div", {"class": {"zg_itemWrapper"}})
    for item in products:
        hastitle = item.find_all("a", class_="a-link-normal")
        for some in hastitle:
            if not some.has_attr("title") and "a-size-small" not in some["class"]:
                products_url = some.get("href")
                products_list.append("https://www.amazon.com" + products_url + "")
    return products_list


def get_sellers(url):
    # print("get_sellers", url)
    # print("get_sellers")
    print(url)
    i_URL = str(re.findall(r"""(.+?)ref=""", str(url), re.S)[0].strip() + "?th=1&psc=1")
    try:
        opener2 = urllib.request.build_opener()
        opener2.addheaders = [
            (
                "User-agent",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
            )
        ]
        response2 = opener2.open(i_URL, timeout=WAITTIME)
        html_doc2 = response2.read()
        html = BeautifulSoup(html_doc2, "html.parser", from_encoding="utf_8")
        try:
            merchant_info = html.find_all("div", {"id": {"merchant-info"}})
            if merchant_info == [] or merchant_info == None:
                merchant_info = html.find("span", {"id": {"merchant-info"}})
                if merchant_info == None or merchant_info == []:
                    merchant_info = html.find(
                        "div", {"id": {"pantry-availability-brief"}}
                    )
                    if merchant_info == None or merchant_info == []:
                        merchant_info = html.find("div", {"id": {"availability-brief"}})
                        if merchant_info == None or merchant_info == []:
                            merchant_info = html.find(
                                "div", {"id": {"sns-availability"}}
                            )
            # print(merchant_info)
        except Exception as e:
            logging.warning("can't find merchant_info:", e)
            return None

        flag = 1

        try:
            merchant_info = str(merchant_info).replace("&amp", '">')
            pattern1 = re.compile(r'seller=(.*?)">')
            # pattern2 = re.compile(r'seller=(.*?)&amp')
            pattern3 = re.compile(r"sold by Amazon.com")
            pattern4 = re.compile(r"(ships|shiping) from China")
            china_ex = pattern4.findall(str(merchant_info))
            # print(china_ex)
            if china_ex:
                flag = 3
            seller_id = pattern1.findall(str(merchant_info))
            if seller_id:
                seller_id = str(seller_id[0])
                # print(seller_id)
                return seller_id, flag
                # file_obj1.write(seller_id + '\n')
            # elif pattern1.findall(str(merchant_info)):
            #     seller_id = pattern1.findall(str(merchant_info))
            #     seller_id = str(seller_id[0])
            #     return seller_id, flag
            #     # file_obj1.write(seller_id+'\n')
            else:
                if not pattern3.findall(str(merchant_info)):
                    logging.info("not sold by Amazon")
                    return seller_id, 2
                    # file_obj2.write(seller_id+'\n')
                elif pattern3.findall(str(merchant_info)):
                    logging.info("sold by Amazon")
        except Exception as ex:
            logging.warning("can't find seller_info:", ex)
        return None
    except:
        logfil_object = open("wrong_url", "a")
        logfil_str = i_URL + "\n"
        print("ERR:" + logfil_str)
        logfil_object.write(logfil_str.encode("UTF-8", "ignore"))
        logfil_object.close()


def best_100(url):

    for i in range(1, 6):
        logging.info(".......................page.......................")
        # 获取当页产品
        products = get_products(url + "#" + str(i))
        products = list(products)

        # 打开文件
        file_obj1 = codecs.open(data_dir + "1.txt", "a", "utf-8")
        file_obj2 = codecs.open(data_dir + "2.txt", "a", "utf-8")
        file_obj3 = codecs.open("Data\\china.txt", "a", "utf-8")

        # 写入商家信息
        for item in products:
            sellers = get_sellers(item)
            if not sellers == None:
                sellers = list(sellers)
                logging.info(sellers[0])
                logging.info(sellers[1])
                if sellers[1] == 1:
                    file_obj1.write(sellers[0] + "\n")
                elif sellers[1] == 2:
                    file_obj2.write(item + "\n")
                elif sellers[1] == 3:
                    file_obj3.write(item + "\n")

        file_obj1.close()
        file_obj2.close()
        file_obj3.close()


def get_link(url):
    html = download(url)
    html = BeautifulSoup(html)
    pattern = re.compile(r'<a href="(.*?)">')

    # print(html.find("ul", {"id": "zg_browseRoot"}))
    # print("------------------------------")

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


def crawl_all(url):
    urls_list = get_link(url)
    for item in urls_list:
        best_100(item)


if __name__ == "__main__":
    print(
        download_request(
            "https://www.amazon.com/Mothers-05212-California-Chrome-Polish/dp/B006VU37AS/ref=zg_bs_15718321_1?_encoding=UTF8&psc=1&refRID=AND8E0R1G12ZR1QAWGPG"
        )
    )
    # get_sellers("https://www.amazon.com/Reversible-Chalkboard-Classroom-Blackboard-Labels-Dry/dp/B01M00UNE4/ref=zg_bs_12896691_77?_encoding=UTF8&psc=1&refRID=D6W5Q63GMJSBEK0E07ZX&th=1&psc=1","123")
    BROWSER.close()
