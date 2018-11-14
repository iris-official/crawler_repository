# -*- coding: utf-8 -*-

import urllib.request
import json
import time
import urllib
import codecs
from bs4 import BeautifulSoup
import sys
import re
import requests
import json
import random
import logging

# 目录名
CATALOG = "兴趣爱好"
# 路径
FOLDER_PATH = r"D:\program\amazon_JP\Data\\商家信息"
FOLDER_MAIN = r"D:\program\amazon_JP\Data\\"
LOG_PATH = r"D:\program\amazon_JP\logs\\"

STEN_STR = "\n"
STRQ_STR = "||"

WAITTIME = 10

#
FILETMEP_STR = (
    LOG_PATH
    + "_JP_"
    + time.strftime("%Y-%m-%d", time.localtime(time.time()))
    + "_"
    + str(time.time())
)
infil = FOLDER_MAIN + "inJP32" + ".txt"
outfil = FOLDER_PATH + CATALOG + "outJP32" + ".txt"
logfil = FILETMEP_STR + CATALOG + ".txt"

infil_object = codecs.open(infil, "rb", "UTF-8")
infil_lines = infil_object.readlines()

DP_ID = []
MAXTRY = 5
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Connection": "keep-alive",
    "Host": "www.amazon.co.jp",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
}
for infil_line in infil_lines:
    item = infil_line.replace("\r", "").replace("\n", "").strip()
    DP_ID.append(item.encode("utf-8").decode("utf-8-sig"))

infil_object.close()


def write_in(data, path):
    with codecs.open(path, "a", "utf-8") as file_obj:
        file_obj.write(data)
    file_obj.close()


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


for i in range(len(DP_ID)):

    rt = random.random()
    time.sleep(0.5 + rt)
    outfil_str = ""
    logfil_str = ""
    pho_no = "null"
    nbs = [0, 0, 0, 0]

    URLhead = (
        "https://www.amazon.co.jp/sp?_encoding=UTF8&asin=&isAmazonFulfilled=1&isCBA=&marketplaceID=A1VC38T7YXB528&orderID=&seller="
    )
    URL = URLhead + DP_ID[i] + "&language=zh_CN"
    print(URL)

    # --------主体工程--------
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [
            (
                "User-agent",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
            )
        ]
        response = download_request(URL)
        soup = BeautifulSoup(response, "html.parser")
        html_doc = soup.find("div", attrs={"id": "seller-profile-container"})

        # 提取
        DP_nam = html_doc.find("h1", attrs={"id": "sellerName"}).text
        if str(html_doc).find("""客户服务电话号码：: """):
            pho_no = html_doc.find("span", attrs={"id": "seller-contact-phone"}).text

        if str(html_doc).find("""<th class="a-text-right">整个期间</th></tr>"""):
            s_part = str(
                re.findall(
                    r"""</td></tr><tr><td class="a-nowrap" style="width:1px;">数量</td>(.+?)</tr></table></div></div></div></div></div>""",
                    str(html_doc),
                    re.S,
                )[0].strip()
            )
            soup = BeautifulSoup(s_part, "html.parser")
            nbs = soup.find_all(text=True)

        if str(html_doc).find("""详尽的卖家信息""") != -1:
            html_doc2 = html_doc.find(
                "ul", attrs={"class": "a-unordered-list a-nostyle a-vertical"}
            )
            DP_busi = str(
                re.findall(
                    r"""Business Name:</span>(.+?)</span></li><li><span class="a-list-item">""",
                    str(html_doc2),
                    re.S,
                )[0].strip()
            )
            DP_addr = ""
            addr_part = str(
                re.findall(
                    r"""地址:</span><ul class="a-unordered-list a-nostyle a-vertical">(.+?)</span></li></ul></span></li><li>""",
                    str(html_doc2),
                    re.S,
                )[0].strip()
            )
            soup = BeautifulSoup(addr_part, "html.parser")
            addr_s = soup.find_all(text=True)
            for addr in addr_s:
                DP_addr = DP_addr + addr + ";"

        outfil_str = (
            DP_nam
            + STRQ_STR
            + DP_ID[i]
            + STRQ_STR
            + str(nbs[0])
            + STRQ_STR
            + str(nbs[1])
            + STRQ_STR
            + str(nbs[2])
            + STRQ_STR
            + str(nbs[3])
            + STRQ_STR
            + pho_no
            + STRQ_STR
            + DP_busi
            + STRQ_STR
            + DP_addr
            + STEN_STR
        )

        print(outfil_str)

        write_in(outfil_str, outfil)
    except:
        print(logfil)
        logfil_str = DP_ID[i] + STEN_STR
        print("ERR:" + logfil_str)
        write_in(str(logfil_str.encode("UTF-8", "ignore")), logfil)
