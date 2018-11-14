import requests
import re
import codecs
import time
import json
import pandas as pd
from time import sleep
import sys
import python.baidu_getpoint.mysql_helper as mysql_helper

AK = 'ngaqgQjdlmRooq7eYTWVebXyxe9257VY'
RANGE_LIMIT = '1000'
requests.adapters.DEFAULT_RETRIES = 1000
MAXTRY = 1000
URL = 'http://map.baidu.com/'
# import_dir = 'wrong.xlsx'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
'Cookie': 'BIDUPSID:9BEFC566E24C9532B0CCE037B9C57D22; PSTM=1503301988; BDUSS=kwTk1BYm1zQUlvc1hKVGp2OFhqQX42dmp6VHhHWWM5OXRoNzRMeENRR2tBdkJaSVFBQUFBJCQAAAAAAAAAAAEAAAAyT-UMc3VuZmxvd2VyXzM2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKR1yFmkdchZZm; routeiconclicked=1; __cfduid=d021255f3fa6dca8743781f2847061b031508722454; BAIDUID=E31E01582D222B36512ABE4C2BB67157:FG=1; routetype=bus; H_PS_PSSID=1422_21090_26309; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; MCITY=-131%3A; validate=67639; PSINO=7; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; M_LG_UID=216354610; M_LG_SALT=0739867'

    }

KEY_WORD = '公交站'
# connection = mysql_helper.mysql_login()
data_time = time.strftime('%Y%m%d', time.localtime(time.time()))

class SearchBus(object):

    def __init__(self, CITY_CODE , CITY_NAME,PROVINCE_NAME,connection):
        self.PROVINCE_NAME = PROVINCE_NAME
        self.CITY_CODE = CITY_CODE
        self.CITY_NAME = CITY_NAME
        self.BASE_DIR = 'result\\'  + '公交站' + str(CITY_NAME)
        self.connection = connection
    def change_basedir(self, CITY_NAME):
        self.BASE_DIR = 'result\\' +  '公交站' + str(CITY_NAME)
    def change_value(self, CITY_CODE , CITY_NAME, PROVINCE_NAME):
        self.CITY_CODE = CITY_CODE
        self.CITY_NAME = CITY_NAME
        self.PROVINCE_NAME = PROVINCE_NAME
    def get_request(self,url, parameters, headers, num_retries=MAXTRY):
        html = ''
        r = requests.session()
        try:
            html = r.get(url, params=parameters,headers=headers)
            if(html.text.find('"status":302')>-1):
                print('bus 天配额超限，限制访问"')
                sys.exit()
        except Exception as e:
            sleep(2)
            # recursively retry 5xx HTTP errors 判断返回的异常的代码，是否在500到600之间
            return self.get_request(url, num_retries - 1)
        return html
    def write_in(self,data,data_dir):
        with codecs.open(data_dir, 'a+', 'utf-8') as file_obj:
                file_obj.write(data)
        file_obj.close()

    def changePoi(self,x ,y):
        url = 'http://api.map.baidu.com/geoconv/v1/'
        parameters = {
            'coords': str(x) + ',' + str(y),
            'ak': AK,
            'from': 4,
            'to': 3
        }
        response = self.get_request(url, parameters, headers)
        try:
            html = response.text
            decodejson = json.loads(html).get('result')[0]
            coor  = []
            coor.append(decodejson.get('x'))
            coor.append(decodejson.get('y'))
        except:
            print('changePoi wrong')
        return coor

    def search(self,x, y, id):
        list = []
        # for key_word in find_list:
        flag = 0
        for page in range(0,3):
            parameters = {
                'newmap': '1',
                'reqflag': 'pcmap',
                'biz': '1',
                'from': 'webmap',
                'da_par': 'baidu',
                'pcevaname': 'pc4.1',
                'qt': 'nb',
                'c': self.CITY_CODE,
                # 'wd': key_word['name'],
                'wd': '公交站',
                'da_src': 'pcmappg.poi.page',
                'on_gel': '1',
                'l': '19',
                'gr': '1',
                'nb_x': x,
                'nb_y': y,
                'gr_radius': RANGE_LIMIT,
                'tn': 'B_NORMAL_MAP',
                'nn': page * 10,
                'u_loc': '12953877,4824666',
                'ie': 'utf-8',
                't': '1525254112870',
                'pn': page,
                'b': '(' + str(float(x) - 10000) + ',' + str(float(y) - 1000) + ';' + str(float(x) + 10000) + ',' + str(float(y) + 1000)
            }
            htm = self.get_request(URL, parameters,headers);
            htm = htm.text.encode('utf-8').decode('unicode_escape')
            mysql_helper.fun1_sql_insert(id, htm, self.CITY_NAME, KEY_WORD,self.connection)
            pattern = r',"content":(.+?),"current_city"'
            if(re.findall(pattern, htm)):
                data = {}
                htm = re.findall(pattern, htm)
                pattern = r'"acc_flag":(.+?)"ty"'
                htm = re.findall(pattern, htm[0])
                for item in htm:
                    pattern = r'(?<="name":").+?(?=")'
                    if(re.findall(pattern, item)):
                        try:
                            name = re.findall(pattern, item)[-1]
                            pattern1 = r'geo":"1\|(.+?);'
                            pattern2 = r'"dis":(.+?),"'
                            pattern3 = r'"addr":"(.+?)","'
                            pattern4 = r'"cla":(.+?)],'
                            coor = re.findall(pattern1, item)
                            distance = re.findall(pattern2, item)[0]
                            addr = re.findall(pattern3, item)[0]
                            di_tag = re.findall(pattern4, item)[0]
                            pattern5 = r',"di_tag":"(.+?)","'
                            di_tag2 = re.findall(pattern5, item)[0]
                            # & (name == key_word['name'])
                            if((int(distance) != -1) & (int(distance) < 1000)&((di_tag2.find('公交车站') > -1) or(di_tag.find('22') > -1))):
                                lat = coor[0].split(",")[0]
                                lon = coor[0].split(",")[1]
                                data["name"] = name
                                data["coor"] = self.changePoi(lat,lon)
                                data["dis"] = distance
                                data["addr"] = addr
                                # data["di_tag"] = di_tag
                                data_copy = data.copy()
                                list.append(data_copy)
                        except Exception as ex:
                            print(ex)
            # else:
                # print("can't find the name")
        return list
    def search_api(self,x,y, id):
        list = []
        poi = self.changePoi(x,y)
        url = 'http://api.map.baidu.com/place/v2/search'
        for page in range(0, 15):
            parameters = {
                'query': KEY_WORD,
                'location': str(poi[1])+','+str(poi[0]),
                'radius': RANGE_LIMIT,
                'output': 'xml',
                'ak': AK,
                'output': 'json',
                'page_size': 20,
                'page_num': page,
                'city_limit': 'true'

            }
            response = self.get_request(url, parameters, headers)
            html = response.text
            # sleep(3)
            mysql_helper.fun2_sql_insert(id, html, self.CITY_NAME, KEY_WORD,self.connection)
            if(json.loads(html).get('total') == 0):
                return list
            decodejson = json.loads(html).get('results')
            if (decodejson):
                for item in decodejson:
                    name = item.get('name')
                    loc = item.get('location')
                    addr = item.get('address')
                    lat = loc.get('lat')
                    lng = loc.get('lng')
                    data = {}
                    data["name"] = name
                    data["addr"] = addr
                    data["lng"] = lng
                    data["lat"] = lat
                    data_copy = data.copy()
                    # data = [name,loc,addr,lat,lng]
                    list.append(data_copy)
            else:
                break
        return list

    def fun1(self,coor,id):
        poi = self.changePoi(coor.split(",")[0], coor.split(",")[1])
        banklist1 = self.search(coor.split(",")[0], coor.split(",")[1],id)
        if(banklist1 == []):
            mysql_helper.bus1_info_sql_insert(self.CITY_NAME,self.PROVINCE_NAME,str(id),str(poi[0])+','+str(poi[1]),'','','',''
                    ,self.connection)
        else:
            for info in banklist1:
                mysql_helper.bus1_info_sql_insert(self.CITY_NAME,self.PROVINCE_NAME,str(id),str(poi[0])+','+str(poi[1]),str(info['name']) ,
                         str(info['coor'][0]) + ',' + str(info['coor'][1]),str(info['dis']), str(info['addr']), self.connection)
        print(banklist1)
        return banklist1

    def fun2(self,coor,id):
        poi = self.changePoi(coor.split(",")[0],coor.split(",")[1])
        banklist2 = self.search_api(coor.split(",")[0], coor.split(",")[1],id)
        # data_dir2 = self.BASE_DIR + str(data_time) + '接口方法.txt'
        if (banklist2 == []):
            mysql_helper.bus2_info_sql_insert(self.CITY_NAME,self.PROVINCE_NAME,str(id),str(poi[0]) + ',' + str(poi[1]),'','',''
                    , self.connection)
        else:
            for info in banklist2:
                mysql_helper.bus2_info_sql_insert(self.CITY_NAME,self.PROVINCE_NAME,str(id),str(poi[0])+','+str(poi[1]),str(info['name']),str(info['lng']) + ',' + str(info['lat']),str(info['addr']), self.connection)
        print(banklist2)
        return(banklist2)
