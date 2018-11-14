# -*- coding: utf-8 -*-

# Author: Wu Yunxiang
# Date: 2017/07/12
# Contact Information:
#   WeChat: 18961517612
#   QQ: 530719677


from selenium import webdriver
import requests
import os
import json
import time
import python.shunfeng0518.mysql_helper_android as mysql_helper
import python.shunfeng0518.huawei_ip_change as huawei_ip_change

LYFLAG = 'KD100'
URL = 'http://p.kuaidi100.com/mobile/mobileapi.do'
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM801 Build/LMY47V)',
    'Host': 'p.kuaidi100.com',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
}

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

def form_request(yjhm):
    params = {
        'method': 'query',
        'userid': '0',
        'json': '{"num": "%s", "com": "shunfeng", "method": "query", "appid": "com.Kingdee.Express", "versionCode": 439, "os_version": "android5.1.1"}' % yjhm
    }
    response = requests.post(URL, params=params, headers=HEADERS)
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
            sql =  "INSERT INTO kd100_mail_info (yjhm,locations,locations_arrow,product_name,last_update_time,status,crawler_time,add_do,add_flag) VALUES " \
                   "('" + tyjhm + "','" + torg + "','" + tdes + "','-','" + record.get('time') + "','" + record.get('context') + "','" + str(crawler_time) + "','" +  record.get('status') + "','" + LYFLAG + "')"
            with connection.cursor() as cursor:
                cursor.execute(sql)
        connection.commit()
        # print(yjhm + ":【SUC】" + sql)
        print(yjhm + ":【SUC】")
    elif status == '500':
        print(yjhm + ":【" + status + "】")
        sql = "INSERT INTO no_mail (yjhm) VALUE" + ' ' + '(' + yjhm + ')'
        with connection.cursor() as cursor:
            cursor.execute(sql)
        print(yjhm + ":【NO】")
        time.sleep(0)
    else:
        # print(yjhm + ":【" + str(status) + "】") # 不插网卡使用
        print(yjhm + ":【" + status + "】")  # 插网卡使用
        time.sleep(60)
    # except Exception as e:
    #     print(e)
    #     print(yjhm + ":【ERR】")
    #     time.sleep(0)
    print("=====================================================")

#切换IP,重启浏览器
def change_ip(driver):
    print('切换IP,重启浏览器')
    huawei_ip_change.reboot_service(driver)  # 操作华为网卡，其他的需修改程序
    driver.quit()
    driver = browser_sets()
    time.sleep(30)
    return driver

if __name__ == '__main__':
    connection = mysql_helper.mysql_login()
    danhao_list = mysql_helper.select_danhao(connection)
    print(str(len(danhao_list)) + " danhao")
    COUNT = 0

    for yjhm in danhao_list:
        # print(yjhm)
        COUNT+=1
        print(COUNT)
        max_try = 5
        while max_try > 0:
            try:
                resp = form_request(yjhm)
                parse(yjhm, resp, connection)
                break
            except Exception as e:
                print(e)
                max_try-=1
                time.sleep(3)
                print(str(5-max_try) + 'st try')
                if(max_try==0):
                    driver = browser_sets()
                    driver = change_ip(driver)
                    driver.quit()
        time.sleep(0)
    mysql_helper.connection_close(connection)

