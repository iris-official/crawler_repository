from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import logging
import re
import os, codecs
import time
import random
import urllib.request
import requests

HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
    # 'Cookie': 'aliyungf_tc=AQAAAM+QwFPOQQAAIMz9PL3a1rHSRRiT; acw_tc=AQAAAPZd1muYQgAAIMz9PFXuKPiDuWvJ',\
    "Host": "www.amazon.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
}
tproxy = "101.89.63.182:1080"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=socks5://%s" % tproxy)
BROWSER = webdriver.Chrome(chrome_options=chrome_options)
MAXTRY = 5
url_list = []
WAITTIME = 5


def download(url, num_retries=MAXTRY):
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
            return download(url, num_retries - 1)
    return html


def get_link(url):
    print("get_link...")
    total_links = []
    bro_link1 = []
    bro_link2 = []
    bro_link3 = []
    bro_link4 = []
    bro_link5 = []
    html = download(url)
    html = BeautifulSoup(html)
    try:
        root = html.find("span", {"class": "zg_selected"})
        pattern = re.compile(r'<a href="(.*?)">')
        pattern1 = re.compile(r"<ul>")
        try:
            bro = root.find_parent().find_next_siblings()
            ul = pattern1.findall(str(bro))
            if ul:
                url_list.append(url)
                try:
                    bro_link = root.find_parent().find_next_siblings()
                    bro_link = pattern.findall(str(bro_link))
                    for link in bro_link:
                        bro_link1.append(link)
                except:
                    logging.warning("can't find hrefs")
        except:
            print("the last page")
    except:
        print("can't find browseRoot")
    if bro_link1:

        for url in bro_link1:
            html = download(url)
            html = BeautifulSoup(html)
            try:
                root = html.find("span", {"class": "zg_selected"})
                pattern = re.compile(r'<a href="(.*?)">')
                pattern1 = re.compile(r"<ul>")
                try:
                    bro = root.find_parent().find_next_siblings()
                    ul = pattern1.findall(str(bro))
                    if ul:
                        url_list.append(url)
                        try:
                            bro_link = root.find_parent().find_next_siblings()
                            bro_link = pattern.findall(str(bro_link))
                            for link in bro_link:
                                bro_link2.append(link)
                        except:
                            logging.warning("can't find hrefs")
                except:
                    print("the last page")
                    return None
            except:
                print("can't find browseRoot")
                return None
    # if bro_link2:
    #     for url in bro_link2:
    #         html = download(url)
    #         html = BeautifulSoup(html)
    #         try:
    #             root = html.find("span", {"class": "zg_selected"})
    #             pattern = re.compile(r'<a href="(.*?)">')
    #             pattern1 = re.compile(r'<ul>')
    #             try:
    #                 bro = root.find_parent().find_next_siblings()
    #                 ul = pattern1.findall(str(bro))
    #                 if ul:
    #                     url_list.append(url)
    #                     try:
    #                         bro_link = root.find_parent().find_next_siblings()
    #                         bro_link = pattern.findall(str(bro_link))
    #                         for link in bro_link:
    #                             bro_link3.append(link)
    #                     except:
    #                         logging.warning("can't find hrefs")
    #             except:
    #                 print("the last page")
    #                 return None
    #         except:
    #             print("can't find browseRoot")
    #             return None
    # if bro_link3:
    #     for url in bro_link3:
    #         html = download(url)
    #         html = BeautifulSoup(html)
    #         try:
    #             root = html.find("span", {"class": "zg_selected"})
    #             pattern = re.compile(r'<a href="(.*?)">')
    #             pattern1 = re.compile(r'<ul>')
    #             try:
    #                 bro = root.find_parent().find_next_siblings()
    #                 ul = pattern1.findall(str(bro))
    #                 if ul:
    #                     url_list.append(url)
    #                     try:
    #                         bro_link = root.find_parent().find_next_siblings()
    #                         bro_link = pattern.findall(str(bro_link))
    #                         for link in bro_link:
    #                             bro_link4.append(link)
    #                     except:
    #                         logging.warning("can't find hrefs")
    #             except:
    #                 print("the last page")
    #                 return None
    #         except:
    #             print("can't find browseRoot")
    #             return None
    # if bro_link4:
    #     for url in bro_link4:
    #         html = download(url)
    #         html = BeautifulSoup(html)
    #         try:
    #             root = html.find("span", {"class": "zg_selected"})
    #             pattern = re.compile(r'<a href="(.*?)">')
    #             pattern1 = re.compile(r'<ul>')
    #             try:
    #                 bro = root.find_parent().find_next_siblings()
    #                 ul = pattern1.findall(str(bro))
    #                 if ul:
    #                     url_list.append(url)
    #                     try:
    #                         bro_link = root.find_parent().find_next_siblings()
    #                         bro_link = pattern.findall(str(bro_link))
    #                         for link in bro_link:
    #                             bro_link5.append(link)
    #                     except:
    #                         logging.warning("can't find hrefs")
    #             except:
    #                 print("the last page")
    #                 return None
    #         except:
    #             print("can't find browseRoot")
    #             return None
    # for link in url_list:
    #     if link not in total_links:
    #         total_links.append(link)
    # for link in bro_link1:
    #     if link not in total_links:
    #         total_links.append(link)
    for link in bro_link2:
        if link not in total_links:
            total_links.append(link)
    # for link in bro_link3:
    #     if link not in total_links:
    #         total_links.append(link)
    # for link in bro_link4:
    #     if link not in total_links:
    #         total_links.append(link)
    # for link in bro_link5:
    #     if link not in total_links:
    #         total_links.append(link)
    # print(bro_link2)
    print(total_links)


get_link("https://www.amazon.com/gp/bestsellers/toys-and-games/")

BROWSER.close()
