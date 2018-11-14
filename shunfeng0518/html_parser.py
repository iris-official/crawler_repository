# -*- coding: utf-8 -*-

# @Usage: 解析顺丰官网跟踪查询信息

import os
import re
import codecs
import time
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(__file__)
htmldoc_dir = os.path.join(BASE_DIR, 'Data\\htmldoc')

# 清晰字符串里的标签内容
def clear_str(str):
    if '<' in str:
        clear_re = re.compile('<.*?>')
        str = clear_re.sub('', str)
    return str.replace(' ', '')

def process_empty_str(re_result_list):
    if len(re_result_list) == 0:
        return ''
    else:
        return re_result_list[0]

# 更换时间格式
def change_time(crawler_time):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(crawler_time, "%Y-%m-%d %H%M%S"))

# 解析物流信息
def parse_page(text, crawler_time):
    danhao_info_list = []
    wuliu_info_list = []
    no_record_list = []
    terminal_list = []
    text = text.replace('open', '')
    soup = BeautifulSoup(text, 'html.parser')
    deliveries = soup.find_all('div', attrs={"class": "main-content-row delivery"})
    htmldoc_path = os.path.join(htmldoc_dir, crawler_time+'.txt')
    with codecs.open(htmldoc_path, 'wb', 'utf-8') as f:
        f.write('\n\n\n\n\n'.join([str(a) for a in deliveries]))
    crawler_time = change_time(crawler_time)
    for each_delivery in deliveries:
        if each_delivery.find('div', attrs={"class": "delivery-brief not-found"}):
            no_record_list.append([re.findall('未查到此运单(.*?)信息', str(each_delivery))[0], crawler_time])
        else:
            locations = process_empty_str(re.findall('class="locations">(.*?)<span class', str(each_delivery)))
            locations_arrow = process_empty_str(re.findall('location-arrow"></span>(.*?)</div>', str(each_delivery)))
            number = re.findall('class="number">(.*?)</span>', str(each_delivery).replace('\r', '').replace('\n',''))[0]
            product = re.findall('product-name">(.*?)</span>', str(each_delivery).replace('\r', '').replace('\n',''))[0]
            last_update_time = re.findall('class="last-update"><span class="time">(.*?)</span>', str(each_delivery).replace('\r', '').replace('\n',''))[0]
            status = clear_str(re.findall('<span class="status">(.*?)</span>', str(each_delivery).replace('\r', '').replace('\n',''))[0])
            danhao_info_list.append([number, locations, locations_arrow, product, last_update_time, status, crawler_time])

            day_soups = each_delivery.find_all('div', attrs={"class": "status-update-box "})
            for each_day_soup in day_soups:
                day = re.findall('div class="status-update-tab">(.*?)星期', str(each_day_soup).replace('\r', '').replace('\n',''))[0]
                time = re.findall('<td class="time">(.*?)</td>', str(each_day_soup).replace('\r', '').replace('\n',''))
                statuses = re.findall('class="update">(.*?)</td>', str(each_day_soup).replace('\r', '').replace('\n',''))
                for index in range(len(time)):
                    try:
                        wuliu_info_list.append([number, day+time[index], clear_str(statuses[index]), crawler_time])
                        if 'terminal-code' in statuses[index]:
                            terminal_codes = re.findall('terminal-code="(.*?)"', statuses[index])
                            #link_type = re.findall('link-type="(.*?)"', statuses[index])
                            types = re.findall('terminal-type="(.*?)"', statuses[index])
                            #names = re.findall('【(.*?)】', statuses[index])
                            for t_index in range(len(terminal_codes)):
                                terminal_list.append([terminal_codes[t_index], types[t_index]])
                    except Exception as ex:
                        print(ex)
    print('无物流个数：', len(no_record_list), ','.join([a[0] for a in no_record_list]))
    return wuliu_info_list, no_record_list, danhao_info_list, terminal_list






