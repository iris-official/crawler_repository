# -*- coding: utf-8 -*-
import python.shunfeng0518.PRO as tu
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import random
import time
#time.sleep(2)
import urllib.request
import os
from PIL import Image
from PIL import ImageChops
import numpy
import python.shunfeng0518.mysql_helper as mysql_helper
import python.shunfeng0518.html_parser as html_parser
import python.shunfeng0518.huawei_ip_change as huawei_ip_change

BASE_DIR = os.path.dirname(__file__)
slide_path = os.path.join(BASE_DIR, 'Data\\slide')
total_path = os.path.join(BASE_DIR, 'Data\\total')
slide_data_path = os.path.join(BASE_DIR, 'Data\\slide_data')

OUT_TIME = 60
#Y = 539 # 验证码滑块中心黑点的位置
MAX_TRY = 10 # 换IP前请求的次数
EMPTY_TRY = 2 # 全部无物流情况后重新请求的次数
GROUP_NUM = 20 # 多少个一组

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

# 根据class_name 寻找输入框并填写信息
def input_by_class(text='', element_class=''):
    input_el = driver.find_element_by_class_name(element_class)  # 通过 class name 查找网页元素
    input_el.send_keys(text)  # 输入字符串
    time.sleep(0.5)


# 滑块位置检测
def get_offset_value(data):
    for j in range(680):
        jj = 679 - j
        num = 0
        for i in range(390):
            if data[i, jj] > 100:
                num += 1
                if num > 40:
                    length = 291 - round((690-jj)/2)
                    length=length+6+random.randint(-8,8)
                    print(length)
                    return length
    # for col_num in range(data.shape[1]):
    #     count = 0
    #     for item in data[:, col_num]:
    #         if item[0] > 100:
    #             count += 1
    #     if count > 30:
    #         return col_num
    # return 0

# 计算图片位移
def cal_picture(src_slide, crawler_time):
    url_src = urllib.request
    #print(url_src)
    try:
        img_slide = url_src.urlopen(src_slide, timeout=OUT_TIME).read()
        #print(img_slide)
        url_src.urlopen(src_slide).close()
        #img_total = url_src.urlopen(src_total, timeout=OUT_TIME).read()
        #print(img_total)
        #url_src.urlopen(src_total).close()
    except Exception as ex:
        print('Open picture error!!!', ex)
        return None

    slide_file = os.path.join(slide_path, crawler_time + '.jpg')
    with open(slide_file, 'wb') as f:
        f.write(img_slide)
    total_file = os.path.join(total_path, crawler_time + '.jpg')
    #with open(total_file, 'wb') as f:
        #f.write(img_total)
    tu.imgPRO(slide_file, total_file)
    #PRO.imgPRo(slide_file, total_file)
    #slide_file = os.path.join(slide_path, crawler_time + '.jpg')
    #total_file = os.path.join(total_path, crawler_time + '.jpg')
    try:
        slide = Image.open(slide_file)
        total = Image.open(total_file)
        diff = ImageChops.difference(slide, total)
        diff = diff.convert('L')
        data = numpy.matrix(diff.getdata())
    except Exception as ex:
        print('offset calculate ERROR!!!', ex)
        return None

    try:
        data = numpy.reshape(data, (390, 680))
        length = get_offset_value(data)
        #length = round(length / 2) - 10
    except Exception as ex:
        print(ex)
        return None
    try:
        x = numpy.random.normal(3, 0.6, 1000)
        c, cc = numpy.histogram(x, bins=40, range=None, normed=False, weights=None)
        time.sleep(0.5)
        track_list = list(map(lambda i: i / sum(c) * length, c))
    except Exception as ex:
        print(ex)
        return None



    '''
    track_list = []
    # 每次移动轨迹的距离
    offset = 0 # 记录位移累加值
    count = 0 # 记录步数
    while offset < length-7:
        count += 1
        if count < 6:
            x = random.randint(1, 2)
            offset += x
        else:
            x = random.randint(2, 4)
            offset += x
        track_list.append(x)

    for i in range(length - offset):
        offset += 1
        track_list.append(1)

    for i in range(5):
        x = random.randint(1, 2)
        offset += x
        track_list.append(x)
    if offset > length:
        for i in range(offset-length):
            track_list.append(-1)
    else:
        for i in range(length-offset):
            track_list.append(1)
    '''
    return track_list

# 返回根据class_name定位的元素是否存在
def is_class_name_element_exist(driver, class_name):
    try:
        driver.find_element_by_class_name(class_name)
        return True
    except:
        return False

# 返回根据tag_name定位的元素是否存在
def is_tag_name_element_exist(driver, tag_name):
    try:
        driver.find_element_by_tag_name(tag_name)
        return True
    except:
        return False

def crack_code(driver, crawler_time):
    src_slide = driver.find_element_by_xpath("//img[@id='slideBkg']").get_attribute('src')
    track_list = cal_picture(src_slide, crawler_time)
    # 没计算出来
    if track_list is None:
        return None, crawler_time
    try:
        button = driver.find_element_by_id('tcaptcha_drag_thumb')
        ActionChains(driver).click_and_hold(on_element=button).perform()
        time.sleep(1)
        for track in track_list:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()
            time.sleep(random.randint(1, 5)/200)
        time.sleep(0.1)
        ActionChains(driver).release(on_element=button).perform()
        time.sleep(1)
    except Exception as ex:
        print('NO slide_bar!!!', ex)
    time.sleep(2.5)#10

# 下载物流页面信息
def download_wuliu_info(driver, danhao):
    crawler_time = time.strftime('%Y-%m-%d %H%M%S', time.localtime(time.time()))
    # 输入单号，点击查询，并切换到验证码frame
    max_try = MAX_TRY
    while max_try > 0:
        try:
            if (not is_class_name_element_exist(driver, 'token-input')) \
                    or (is_tag_name_element_exist(driver, 'iframe')): # 被卡在验证码页面或者查询框找不到时
                driver.get('http://www.sf-express.com/cn/sc/dynamic_function/waybill/')
            else:
                driver.find_element_by_class_name('input-group-addon').click()
            input_by_class(danhao, 'token-input')
            driver.find_element_by_tag_name('button').click()
            time.sleep(1)
            iframe = driver.find_element_by_tag_name('iframe')
            #print(iframe)
            driver.switch_to.frame(iframe)
            max_try -= 1
            break
        except Exception as ex: # 从点查询到出现滑块验证码之间的异常，包含验证码出不来、单号错位等
            print('Input or vertify ERROR!!!', ex)
            return None
        #     time.sleep(10)
        #     max_try -= 1
    try:
        if max_try <= 0:
            return 'error', crawler_time
        time.sleep(2)
        crack_code(driver, crawler_time)
        for i in range(3):
            if is_tag_name_element_exist(driver, 'iframe'):
                driver.find_element_by_id('reload').click()
                time.sleep(1)
                crack_code(driver, crawler_time)
            else:
                break
        if is_tag_name_element_exist(driver, 'iframe'):
            return None, crawler_time
        driver.switch_to.default_content()  # 转换 webdriver 工作环境至默认
    except Exception as ex:
        # 没查询出结果来或卡在了验证码页面
        print('no deliveries!!!058888888888888888888888', ex)
        return None
    try:
        WebDriverWait(driver, OUT_TIME).until(lambda the_driver: the_driver.find_element_by_class_name("deliveries"))
        page = driver.page_source
        return page, crawler_time
    except Exception as ex:
        # 没查询出结果来或卡在了验证码页面
        print('no deliveries!!!', ex)
        return None, crawler_time

#切换IP,重启浏览器
def change_ip(driver):
    print('切换IP,重启浏览器')
    huawei_ip_change.reboot_service(driver)  # 操作华为网卡，其他的需修改程序
    driver.quit()
    driver = browser_sets()
    time.sleep(60)
    return driver

if __name__ == '__main__':
    connection = mysql_helper.mysql_login()
    danhao_list = mysql_helper.select_danhao(connection)
    driver = browser_sets()
    print(len(danhao_list))
    max_try = MAX_TRY
    empty_try = EMPTY_TRY
    index = GROUP_NUM - 1  # 每GROUP_NUM个一组
    while index < len(danhao_list):
        if ((index + 1) % GROUP_NUM == 0) or (index == len(danhao_list) - 1):
            mail_no = ','.join(danhao_list[index-GROUP_NUM+1:index + 1])
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), 'Start', index+1)
            #print(index)
            #print(index+1)
            print(mail_no)
            try:
                page, crawler_time = download_wuliu_info(driver, mail_no)
                #print(page)
                if page == 'error': # 出现了验证码图片出不来、有alert框等情况
                    driver = change_ip(driver)
                    continue
                elif page is None:
                    max_try -= 1
                    if max_try < 0:
                        driver = change_ip(driver)
                        max_try = MAX_TRY
                    time.sleep(5)
                    continue
                else:
                    wuliu_info_list, no_record_list, danhao_info_list, terminal_list = html_parser.parse_page(page, crawler_time)
                    # 全部返回为无信息的情况，重复爬EMPTY_TRY次，还没有就将单号写入表
                    if len(no_record_list) == GROUP_NUM:
                        empty_try -= 1
                        if empty_try < 0:
                            #driver = change_ip(driver)
                            empty_try = EMPTY_TRY
                            mysql_helper.no_record_mail_insert2(no_record_list, connection)
                            index += GROUP_NUM
                        time.sleep(5)
                        continue
                    # 出错或无任何信息，重新爬
                    if len(no_record_list) + len(danhao_info_list) + len(wuliu_info_list) == 0:
                        time.sleep(1)
                        continue
                    # 正常情况
                    if len(no_record_list) > 0:
                        mysql_helper.no_record_mail_insert(no_record_list, connection)
                    if len(danhao_info_list) > 0:
                        mysql_helper.mail_info_insert(danhao_info_list, connection)
                    if len(wuliu_info_list) > 0:
                        mysql_helper.mail_wuliu_insert(wuliu_info_list, connection)
                    if len(terminal_list) > 0:
                        mysql_helper.terminal_insert(terminal_list, connection)
                    print(index+1, 'OK')
                    max_try = MAX_TRY
                    empty_try = EMPTY_TRY
                    time.sleep(1)
                    index += GROUP_NUM
            except Exception as ex:
                # 没查询出结果来或卡在了验证码页面
                print('no deliveries!!!17777777777', ex)


    driver.quit()
    mysql_helper.connection_close(connection)