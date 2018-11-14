import requests
import re
import codecs
import time
import json
import pandas as pd
import python.baidu_getpoint.mysql_helper as mysql_helper
from time import  sleep
import chardet
import sys
import easygui

MAXTRY = 100

county_NAME = 'D:\program\python\\baidu_getpoint\未找到地址\河南未添补坐标201806060918'
import_dir = 'D:\program\python\\baidu_getpoint\河南未添补坐标201806060918.xlsx'

URL = 'http://map.baidu.com/'
data_time = time.strftime('%Y%m%d', time.localtime(time.time()))
data_time1 = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))

def write_in(data,data_dir):
    with codecs.open(data_dir, 'a+', 'utf-8') as file_obj:
            file_obj.write(data)
    file_obj.close()
def write_in_dataframe(data, data_dir):
    data.to_excel(data_dir, sheet_name='result', index=False, header=True)

def search_citycode(import_city):
    code_dir = 'BaiduMap_cityCode_1102.txt'
    f = open(code_dir, 'rb')
    lines = f.read()
    type = chardet.detect(lines)
    lines = lines.decode(type["encoding"])
    lines = str(lines).split('\r\n')
    for line in lines:
        city = line.split(',')[1]
        if(city.find(str(import_city))>-1 ):
            return line.split(',')[0]
if __name__ == '__main__':
    data = pd.read_excel(import_dir)
    no_point = []
    has_point = []
    mark = ''

    for index, row in data.iterrows():
        # print(str(row['v_jd']))
        # print(str(row['v_wd']))
        # print((str(row['v_jd'])).find('E'))
        # print((str(row['v_jd'])).find('°'))
        # print((str(row['v_wd'])).find('E'))
        # print((str(row['v_wd'])).find('°'))
        # print(len(str(row['v_jd'])))
        # print((str(row['v_jd'])).find('.'))
        # print(len(str(row['v_wd'])))
        # print((str(row['v_wd'])).find('.'))
        # print(len(str(row['v_jd']).split('.')[0]))
        # print(len(str(row['v_wd']).split('.')[0]))
        if(((str(row['v_jd'])).find('E')== -1)&((str(row['v_wd'])).find('E')== -1)
               &((str(row['v_jd'])).find('°')== -1)&((str(row['v_wd'])).find('°')== -1)
               & ((str(row['v_jd'])).find('度') == -1) & ((str(row['v_wd'])).find('度') == -1)
               & ((str(row['v_jd'])).find('-') == -1) & ((str(row['v_wd'])).find('-') == -1)
               & ((str(row['v_jd'])).find('`') == -1) & ((str(row['v_wd'])).find('`') == -1)
               & ((str(row['v_jd'])).find('：') == -1) & ((str(row['v_wd'])).find('：') == -1)
               & ((str(row['v_jd'])).find('*') == -1) & ((str(row['v_wd'])).find('*') == -1)
               & ((str(row['v_jd'])).find('’') == -1) & ((str(row['v_wd'])).find('’') == -1)
               & ((str(row['v_jd'])).count('.') == 1) & ((str(row['v_wd'])).count('.') == 1)
               & ((str(row['v_jd'])).find('“') == -1) & ((str(row['v_wd'])).find('“') == -1)
               & ((str(row['v_jd'])).find(',') == -1) & ((str(row['v_wd'])).find(',') == -1)
               &(row['v_wd'] != None )&(row['v_jd'] != None )
               &((len(str(row['v_jd']))>6) &((str(row['v_jd'])).find('.')> -1)) & ((len(str(row['v_wd']))>6) &((str(row['v_wd'])).find('.')>-1))):
            jd = row['v_jd'].replace(' ', '')
            wd = row['v_wd'].replace(' ', '')
            if((int(str(jd).split('.')[0]) > 70)&(int(str(wd).split('.')[0]) < 50)&
                (len(str(jd).split('.')[1]) > 3) & (len(str(wd).split('.')[1]) > 3)):
                row['lng'] = str(jd)
                row['lat'] = str(row['v_wd'])
            elif((int(str(jd).split('.')[0]) < 50) & (int(str(wd).split('.')[0]) > 70)&
                (len(str(jd).split('.')[1]) > 3) & (len(str(wd).split('.')[1]) > 3)):
                row['lat'] = str(jd)
                row['lng'] = str(wd)
            else:
                if (isinstance(no_point, list)):
                    no_point = pd.DataFrame([row])
                else:
                    no_point = no_point.append([row], ignore_index=True)
                continue
            if (isinstance(has_point, list)):
                has_point = pd.DataFrame([row])
            else:
                has_point = has_point.append([row], ignore_index=True)
        else:
            if (isinstance(no_point, list)):
                no_point = pd.DataFrame([row])
            else:
                no_point = no_point.append([row], ignore_index=True)

    if (isinstance(has_point, list)):
        has_point = pd.DataFrame([])
    if (isinstance(no_point, list)):
        no_point = pd.DataFrame([])
    write_in_dataframe(no_point,  county_NAME + '未添补坐标' + str(data_time1) + '.xlsx')
    write_in_dataframe(has_point, county_NAME + '已修正信息' + str(data_time1) + '.xlsx')
    easygui.msgbox("split_excel完成！！")
    # write_in_dataframe(tencent_point, CITY_NAME + '已修正信息' + str(data_time1) + 'tencent.xlsx')

