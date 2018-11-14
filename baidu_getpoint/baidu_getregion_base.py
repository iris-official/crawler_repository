from time import sleep
import pandas as pd
import python.baidu_getpoint.baidu_getregion_bank as FindBank
import python.baidu_getpoint.baidu_getregion_bus as FindBus
import python.baidu_getpoint.baidu_getregion_school as FindSchool
import json
import requests
import time
import codecs
import python.baidu_getpoint.mysql_helper as mysql_helper
import easygui
import os
connection = mysql_helper.mysql_login()
AK = 'UBGFvk0LoUCduDmZyMfKvRoGxHLXkuUk'
URL = 'http://map.baidu.com/'
import_dir = '江苏已修正信息201805060914.xlsx'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
data_time1 = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
requests.adapters.DEFAULT_RETRIES = 1000
dir = '城市代码错误' + str(data_time1) + '.txt'
def write_in_dataframe(data, data_dir):
    data.to_excel(data_dir, sheet_name='result', index=False, header=True)
def deleteChar(data1):
    result = ''
    for x in data1:
        if x in '0123456789.':
            result += x
    return result
def changePoi(x ,y):
    url = 'http://api.map.baidu.com/geoconv/v1/'
    parameters = {
        'coords': deleteChar(str(x)) + ',' + deleteChar(str(y)),
        'ak': AK,
        'from': 3,
        'to': 4
    }
    response = requests.get(url=url, params=parameters, headers=headers)
    html = response.text
    decodejson = json.loads(html).get('result')[0]
    coor  = []
    coor.append(decodejson.get('x'))
    coor.append(decodejson.get('y'))
    return coor
def write_in(data,data_dir):
    with codecs.open(data_dir, 'a+', 'utf-8') as file_obj:
            file_obj.write(data)
    file_obj.close()
import chardet
def search_citycode(import_city):
    code_dir = 'BaiduMap_cityCode_1102.txt'
    f = open(code_dir, 'rb')
    lines = f.read()
    type = chardet.detect(lines)
    lines = lines.decode(type["encoding"])
    lines = str(lines).split('\r\n')
    for line in lines:
        city = line.split(',')[1]
        if(city.find(import_city)>-1 ):
            return line.split(',')[0]
if __name__ == '__main__':
    print('第一个程序')
    try:
        data = pd.read_excel(import_dir)
        FindBank = FindBank.SearchBank('', '','',connection)
        FindBus = FindBus.SearchBus('', '','',connection)
        FindSchool = FindSchool.SerchSchool('', '','',connection)
        jgid = mysql_helper.find_the_last(connection)
        flag = 0
        for index, row in data.iterrows():
            if ((flag == 1)):
                mysql_helper.delete_the_record(row['v_jgid'],connection)
                CITY_CODE = 0
                print('-----------------' + str(row['inst_name']) + '   ' + str(row['address']) + '-----------------')
                PROVINCE_NAME = str(row['v_sfmc']).strip()
                CITY_NAME = str(row['v_dsmc']).strip()
                if (CITY_NAME != 'nan'):
                    CITY_CODE = str(search_citycode(CITY_NAME)).strip()
                    FindBank.change_basedir(CITY_NAME)
                    FindBus.change_basedir(CITY_NAME)
                    FindSchool.change_basedir(CITY_NAME)
                    FindBank.change_value(CITY_CODE, CITY_NAME, PROVINCE_NAME)
                    FindBus.change_value(CITY_CODE, CITY_NAME, PROVINCE_NAME)
                    FindSchool.change_value(CITY_CODE, CITY_NAME, PROVINCE_NAME)
                    coor = changePoi(row['lng'], row['lat'])
                    coor = str(coor[0]) + ',' + str(coor[1])
                    tryTime = 5
                    print('----------------- FindBank fun1-----------------')
                    bank1 = FindBank.fun1(coor, row['v_jgid'])
                    print('----------------- FindBank fun2-----------------')
                    bank2 = FindBank.fun2(coor,row['v_jgid'])
                    if((len(bank2) - len(bank1)>5)&(len(bank1) == 0)):
                        print("try****************************************bank2")
                        # os.system('D:\program\python\\baidu_getpoint\\baidu_getregion_base.py')
                    print('----------------- FindBus fun1-----------------')
                    bus1 = FindBus.fun1(coor, row['v_jgid'])
                    print('----------------- FindBus fun2-----------------')
                    bus2 = FindBus.fun2(coor, row['v_jgid'])
                    if ((len(bus1) - len(bus2) > 5)&(len(bus1) == 0)):
                        print("try****************************************bus1")
                        # os.system('D:\program\python\\baidu_getpoint\\baidu_getregion_base.py')
                    print('----------------- FindSchool fun2-----------------')
                    list = FindSchool.fun2(coor, row['v_jgid'])
                    print('----------------- FindSchool fun1-----------------')
                    FindSchool.fun1(coor, row['v_jgid'], list)
                else:
                    write_in(str(row['v_jgid']) + '$' + str(row['v_sfmc']) + '$' + str(row['v_dsmc']) + '$'
                             + str(row['v_xsmc']) + '$' + str(row['v_jdmc']) + '$' + str(row['v_mph']) +
                             '$' + str(row['c_jyfs']) + '$' + str(row['v_jd']) + '$' + str(row['v_wd'])
                             + '$' + str(row['v_jgmc']) + '$' + str(row['v_jgbh']) + '$' + str(row['inst_name'])+ '$' +
                             str(row['address']) + '$' + str(row['lng']) + '$' + str(row['lat']) + '\r\n', dir)
            if ((str(row['v_jgid']) == jgid)):
                flag = 1
    except:
        connection.close()
        os.system('D:\program\python\\baidu_getpoint\\baidu_getregion_base.py')
    easygui.msgbox("获取周边信息第1个程序完成！")




