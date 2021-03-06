# -*- coding: utf-8 -*-

# Author: Wu Yunxiang
# Date: 2017/07/12
# Contact Information:
#   WeChat: 18961517612
#   QQ: 530719677


from selenium import webdriver
from random import choice
import requests
import os, codecs
import json
import time
import mysql_helper

LYFLAG = 'KD100'
URL = 'http://p.kuaidi100.com/mobile/mobileapi.do'
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM801 Build/LMY47V)',
    'Host': 'p.kuaidi100.com',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
}

# 导入代理
BASE_DIR = os.path.dirname(__file__)
proxies_file = os.path.join(BASE_DIR, 'Data\\proxies\\代理IP_gy_2018_05_25.txt')
all_proxies = []
backup_proxies = []
with codecs.open(proxies_file, 'r', 'utf-8') as file_obj:
    data = file_obj.readlines()
    for line in data:
        all_proxies.append(line.replace('\r', '').replace('\n', ''))
        backup_proxies.append(line.replace('\r', '').replace('\n', ''))

proxy = {'http': choice(all_proxies)}

def browser_sets():
    # Chromedriver.exe放在chrome的安装文件夹下，Application里
    chromedriver = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'
    os.environ["webdriver.chrome.driver"] = chromedriver
    options = webdriver.ChromeOptions()
    options.add_argument('--window-position=0,0')  # chrome 启动初始位置
    options.add_argument('--window-size=1080,800')  # chrome 启动初始大小,修改或删除需对应地改变y值
    options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    setted_browser = webdriver.Chrome(chromedriver, chrome_options=options)
    return setted_browser

def form_request(r, yjhm, proxy):
    params = {
        'method': 'query',
        'userid': '0',
        'json': '{"num": "%s", "com": "shunfeng", "method": "query", "appid": "com.Kingdee.Express", "versionCode": 439, "os_version": "android5.1.1"}' % yjhm
    }
    response = r.post(URL, params=params, headers=HEADERS, proxies=proxy, timeout=10)
    return response
    # callback(response)


def parse(yjhm,resp,connection):
    # try:
    crawler_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    json_data = json.loads(resp.text)
    status = json_data.get('status')
    print("-----------------------------------------------------")
    if status == '200':
        tlastResult = json_data.get('lastResult')
        # print(tlastResult.get('routeInfo'))
        tyjhm = tlastResult.get('nu')
        torg = tlastResult.get('routeInfo').get('from').get('name')
        tdes = tlastResult.get('routeInfo').get('to').get('name')
        # print(torg,tdes)
        for record in tlastResult.get('data'):
            sql =  "INSERT INTO kd100_mail_info_1 (yjhm,locations,locations_arrow,product_name,last_update_time,status,crawler_time,add_do,add_flag) VALUES " \
                   "('" + tyjhm + "','" + torg + "','" + tdes + "','-','" + record.get('time') + "','" + record.get('context') + "','" + str(crawler_time) + "','" +  record.get('status') + "','" + LYFLAG + "')"
            with connection.cursor() as cursor:
                cursor.execute(sql)
        connection.commit()
        # print(yjhm + ":【SUC】" + sql)
        print(yjhm + ":【SUC】 " + crawler_time)
    elif status == '500':
        print(yjhm + ":【" + status + "】")
        sql = "INSERT INTO no_mail (yjhm) VALUE" + ' ' + '(' + yjhm + ')'
        with connection.cursor() as cursor:
            cursor.execute(sql)
        print(yjhm + ":【NO】")
        time.sleep(0)
    else:
        # print(yjhm+ ":【" + str(status) + "】") # 不插网卡使用
        print(yjhm + ":【" + status + "】")  # 插网卡使用
        time.sleep(5)
    # except Exception as e:
    #     print(e)
    #     print(yjhm + ":【ERR】")
    #     time.sleep(0)
    print("=====================================================")


if __name__ == '__main__':
    connection = mysql_helper.mysql_login()
    danhao_list = mysql_helper.select_danhao_a(connection)
    print(str(len(danhao_list)) + " danhao")
    COUNT = 0
    r = requests.session()
    print('proxy is: ' + proxy['http'])
    for yjhm in danhao_list:
        # print(yjhm)
        COUNT+=1
        print(COUNT)
        max_try = 5
        while max_try > 0:
            try:
                resp = form_request(r, yjhm, proxy)
                parse(yjhm, resp, connection)
                time.sleep(1)
                break
            except Exception as e:
                max_try-=1
                time.sleep(3)
                print(str(5-max_try) + 'st try ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                print(e)
                if(max_try==0):
                    time.sleep(10)
                    if proxy['http'] in all_proxies:
                        all_proxies.remove(proxy['http'])
                    if len(all_proxies) <= 0:
                        for proxy in backup_proxies:
                            all_proxies.append(proxy)
                    if len(all_proxies) > 0:
                        proxy['http'] = choice(all_proxies)
                        print('\nproxy change to: ' + proxy['http'])
                        print('  %d proxies remain\n' % len(all_proxies))
        time.sleep(0)
    mysql_helper.connection_close(connection)

