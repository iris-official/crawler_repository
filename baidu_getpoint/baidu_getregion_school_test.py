import requests
import re
import codecs
import time
import json
# import pandas as pd
import python.baidu_getpoint.mysql_helper as mysql_helper

# AK = 'ngaqgQjdlmRooq7eYTWVebXyxe9257VY'
AK = '3mYbhFK4biPKu5XUEnWMMtzNmjHVa6mp'
RANGE_LIMIT = '1000'
requests.adapters.DEFAULT_RETRIES = 5
URL = 'http://map.baidu.com/'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

KEY_WORD = '学校'
connection = mysql_helper.mysql_login()
data_time = time.strftime('%Y%m%d', time.localtime(time.time()))
class SerchSchool(object):

    def __init__(self, CITY_CODE , CITY_NAME):
        self.CITY_CODE = CITY_CODE
        self.CITY_NAME = CITY_NAME
        self.BASE_DIR = 'result\\' + CITY_NAME + '\\' + 'test_result学校'



    def write_in(data,data_dir):
        with codecs.open(data_dir, 'a+', 'utf-8') as file_obj:
                file_obj.write(data)
        file_obj.close()
    def write_in_dataframe(data, data_dir):
        data.to_excel(data_dir, sheet_name="123", index=False, header=True)

    def changePoi(self,x,y):
        url = 'http://api.map.baidu.com/geoconv/v1/'
        parameters = {
            'coords': str(x) + ',' + str(y),
            'ak': AK,
            'from': 4,
            'to': 3
        }
        response = requests.get(url=url, params=parameters, headers=headers)
        html = response.text
        decodejson = json.loads(html).get('result')[0]
        coor  = []
        coor.append(decodejson.get('x'))
        coor.append(decodejson.get('y'))
        return coor

    def search(self,x, y, id,find_list):
        list = []
        for key_word in find_list:
            flag = 0
            for page in range(0,15):
                parameters = {
                    'newmap':'1',
                    'reqflag':'pcmap',
                    'biz':'1',
                    'from':'webmap',
                    'da_par':'baidu',
                    'pcevaname':'pc4.1',
                    'qt':'nb',
                    'c': self.CITY_CODE,
                    'wd': key_word['name'],
                    'da_src':'pcmappg.poi.page',
                    'on_gel':'1',
                    'l':'16',
                    'gr':'1',
                    'nb_x':x,
                    'nb_y':y,
                    'gr_radius':RANGE_LIMIT,
                    'tn':'B_NORMAL_MAP',
                    # 'nn': page * 10,
                    'u_loc':'12953894,4824746',
                    'ie':'utf-8',
                    't':'1524037255504',
                    'pn': page
                }
                htm = requests.get(URL, params=parameters);
                htm = htm.text.encode('utf-8').decode('unicode_escape')
                # mysql_helper.fun1_sql_insert(id, htm, CITY_NAME, KEY_WORD,connection)
                pattern = r',"content":(.+?),"current_city"'
                if(re.findall(pattern, htm)):
                    data = {}
                    htm = re.findall(pattern, htm)
                    pattern = r'"acc_flag":(.+?)"ty"'
                    htm = re.findall(pattern, htm[0])
                    for item in htm:
                        pattern = r'(?<="name":").+?(?=")'
                        if(re.findall(pattern, item)):
                            name = re.findall(pattern, item)[-1]
                            pattern1 = r'geo":"1\|(.+?);'
                            pattern2 = r'"dis":(.+?),"'
                            pattern3 = r'"addr":"(.+?)","'
                            pattern4 = r',"di_tag":"(.+?)","'
                            coor = re.findall(pattern1, item)
                            distance = re.findall(pattern2, item)[0]
                            addr = re.findall(pattern3, item)[0]
                            di_tag = re.findall(pattern4, item)[0]
                            # & (name == key_word['name'])
                            if ((int(distance) < int(RANGE_LIMIT))& (di_tag.find('教育') >-1)):
                                lat = coor[0].split(",")[0]
                                lon = coor[0].split(",")[1]
                                data["name"] = name
                                data["coor"] = self.changePoi(lat, lon)
                                data["dis"] = distance
                                data["addr"] = addr
                                data["di_tag"] = di_tag
                                data_copy = data.copy()
                                list.append(data_copy)
                                flag = 1
                                break
                        else:
                            print("can't find the name")
                            break;
                if(flag == 1):
                    break
        return list
    def search_api(self,x,y, id):
        list = []
        poi = self.changePoi(x,y)
        url = 'http://api.map.baidu.com/place/v2/search'
        for page in range(0, 30):
            parameters = {
                'query': KEY_WORD,
                'location': str(poi[1])+','+str(poi[0]),
                'radius': RANGE_LIMIT,
                'output': 'xml',
                'ak': AK,
                'output': 'json',
                'page_size': 20,
                'page_num': page

            }
            response = requests.get(url=url, params=parameters, headers=headers)
            html = response.text
            # mysql_helper.fun2_sql_insert(id, html, CITY_NAME, KEY_WORD,connection)
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

    def fun1(self,coor,id,find_list):
        poi = self.changePoi(coor.split(",")[0], coor.split(",")[1])
        banklist1 = self.search(coor.split(",")[0], coor.split(",")[1], id, find_list)
        data_dir1 = self.BASE_DIR + str(data_time) + '方法1.txt'
        # if(banklist1 == []):
        #     write_in(str(id) + '$' + str(poi[0])+','+str(poi[1]) + '$' + '$' + '$' + '$' + '$' + '$'
        #              + '$' + '\r\n', data_dir1)
        # else:
        #     for info in banklist1:
        #         write_in(str(id) + '$' + str(poi[0])+','+str(poi[1]) + '$' +str(info['name']) + '$'
        #                  + str(info['coor'][0]) + ',' + str(info['coor'][1]) + '$' + str(info['dis']) +
        #                  '$' + str(info['addr']) + '$' + str(info['di_tag'])+'\r\n', data_dir1)
        print(banklist1)

    def fun2(self,coor,id):
        poi = self.changePoi(coor.split(",")[0],coor.split(",")[1])
        banklist2 = self.search_api(coor.split(",")[0], coor.split(",")[1],id)
        data_dir2 = self.BASE_DIR + str(data_time) + '接口方法.txt'
        # if (banklist2 == []):
            # write_in(str(id) + '$' + str(poi[0]) + ',' + str(poi[1]) + '$' + '$' + '$' + '$' + '$' + '$'
            #          + '$' + '\r\n', data_dir2)
        # else:
            # for info in banklist2:
                # write_in(str(id) + '$' + str(poi[0])+','+str(poi[1]) + '$' + str(info['name']) + '$' + str(info['lng']) + ',' + str(info['lat']) + '$' + str(info['addr']) + '\r\n', data_dir2)
        print(banklist2)
        return banklist2

