import requests
import re
import codecs
import time
import json
import pandas as pd
import python.baidu_getpoint.mysql_helper as mysql_helper

# AK = 'o3gPPvOqcPL5dx57zT8LnGbOf5UKeF29'
AK = '3mYbhFK4biPKu5XUEnWMMtzNmjHVa6mp'
# AK = 'UBGFvk0LoUCduDmZyMfKvRoGxHLXkuUk'

URL = 'http://map.baidu.com/'
# import_dir = 'wrong.xlsx'
import_dir = '兰州地理信息.xlsx'
# import_dir = '空缺20180420.xlsx'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
CITY_CODE = '36'
KEY_WORD = '银行'
RANGE_LIMIT = '1000'
connection = mysql_helper.mysql_login()
data_time = time.strftime('%Y%m%d', time.localtime(time.time()))


def write_in(data,data_dir):
    with codecs.open(data_dir, 'a+', 'utf-8') as file_obj:
            file_obj.write(data)
    file_obj.close()
def write_in_dataframe(data, data_dir):
    data.to_excel(data_dir, sheet_name="123", index=False, header=True)

def changePoi(x ,y):
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

def changePoi3to4(x ,y):
    url = 'http://api.map.baidu.com/geoconv/v1/'
    parameters = {
        'coords': str(x) + ',' + str(y),
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

def getpoint(searchWords):
    for searchWord in searchWords:
        print('searchWord:' + searchWord)
        parameters = {
            'qt': 's',
            'c': CITY_CODE,
            'wd': searchWord,
            'rn': '10',
            'ie': 'utf-8',
            'oue': '1',
            'fromproduct': 'jsapi',
            'res': 'api',
            'callback': 'BMap._rd._cbk58851',
            'ak': 'E4805d16520de693a3fe707cdc962045',
        }
        html = requests.get(URL, params=parameters);
        html = html.text.encode('latin-1').decode('unicode_escape')
        pattern = r'"acc_flag":(.+?)"ty"'
        html = re.findall(pattern, html)
        coor = []
        for htm in html:
            try:
                pattern = r'},"name":"(.+?)","'
                name = re.findall(pattern, htm)
                if(name[0].find("邮政") > -1):
                    pattern1 = r'geo":"1\|(.+?);'
                    coor = re.findall(pattern1, htm)
                    x = coor[0].split(",")[0]
                    y = coor[0].split(",")[1]
                    break
            except Exception as ex:
                print(ex)
        if(coor):
            return coor[0];
        else:
            continue
    print('the coor is' + str(coor))
    return 0

def search(x, y, id):
    list = []
    for page in range(0, 30):
        parameters = {
            'newmap':'1',
            'reqflag':'pcmap',
            'biz':'1',
            'from':'webmap',
            'da_par':'baidu',
            'pcevaname':'pc4.1',
            'qt':'nb',
            'c': CITY_CODE,
            'wd':KEY_WORD,
            'da_src':'pcmappg.poi.page',
            'on_gel':'1',
            'l':'16',
            'gr':'1',
            'nb_x':x,
            'nb_y':y,
            'gr_radius':RANGE_LIMIT,
            'tn':'B_NORMAL_MAP',
            # 'nn':'0',
            'u_loc':'12953894,4824746',
            'ie':'utf-8',
            't':'1524037255504',
            'pn': page
        }
        htm = requests.get(URL, params=parameters);
        htm = htm.text.encode('utf-8').decode('unicode_escape')
        mysql_helper.fun1_sql_insert(id, htm, CITY_CODE, KEY_WORD,connection)
        pattern = r',"content":(.+?),"current_city"'
        if(re.findall(pattern, htm)):
            data = {}
            htm = re.findall(pattern, htm)
            pattern = r'"acc_flag":(.+?)"ty"'
            htm = re.findall(pattern, htm[0])
            for item in htm[:-1]:
                pattern = r'},"name":"(.+?)","'
                if(re.findall(pattern, item)):
                    name = re.findall(pattern, item)
                    pattern1 = r'geo":"1\|(.+?);'
                    pattern2 = r'"dis":(.+?),"'
                    pattern3 = r'"addr":"(.+?)","'
                    pattern4 = r',"di_tag":"(.+?)","'
                    coor = re.findall(pattern1, item)
                    distance = re.findall(pattern2, item)[0]
                    addr = re.findall(pattern3, item)[0]
                    di_tag = re.findall(pattern4, item)[0]
                    # 电话：
                    pattern5 = r'(?<="phone":").+?(?=")'
                    phone = re.findall(pattern5, item)
                    if not phone:
                        phone = ''
                    elif phone[0] == r'",':
                        phone = ''
                    else:
                        phone = phone[0]
                    # 营业时间：
                    pattern6= r'(?<="shop_hours":").+?(?=")'
                    shop_hours = re.findall(pattern6, item)
                    if len(shop_hours) < 2:
                        shop_hours = ''
                    else:
                        shop_hours = shop_hours[0]
                    if(int(distance) < RANGE_LIMIT):
                        lat = coor[0].split(",")[0]
                        lon = coor[0].split(",")[1]
                        data["name"] = name[0]
                        data["coor"] = changePoi(lat,lon)
                        data["dis"] = distance
                        data["addr"] = addr
                        data["di_tag"] = di_tag
                        data["phone"] = phone
                        data["shop_hours"] = shop_hours
                        data_copy = data.copy()
                        list.append(data_copy)
                    else:
                        return list
                else:
                    print("can't find the name")
                    break;
        else:
            break
    return list
def search_api(x,y, id):
    list = []
    poi = changePoi(x,y)
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
        mysql_helper.fun2_sql_insert(id, html, CITY_CODE, KEY_WORD,connection)
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

def fun1(coor,id):
    poi = changePoi(coor.split(",")[0], coor.split(",")[1])
    banklist1 = search(coor.split(",")[0], coor.split(",")[1], id)
    data_dir1 = 'result' + str(data_time) + '方法1.txt'
    if(banklist1 == []):
        write_in(str(id) + ';' + str(poi[0])+','+str(poi[1]) + ';' + ';' + ';' + ';' + ';' + ';'
                 + ';' + '\r\n', data_dir1)
    else:
        for info in banklist1:
            write_in(str(id) + ';' + str(poi[0])+','+str(poi[1]) + ';' +str(info['name']) + ';'
                     + str(info['coor'][0]) + ',' + str(info['coor'][1]) + ';' + str(info['dis']) +
                     ';' + str(info['addr']) + ';' + str(info['di_tag']) + ';' + str(info['phone'])
                     + ';' + str(info['shop_hours']) +'\r\n', data_dir1)
    print(banklist1)

def fun2(coor,id):
    poi = changePoi(coor.split(",")[0],coor.split(",")[1])
    banklist2 = search_api(coor.split(",")[0], coor.split(",")[1],id)
    data_dir2 = 'result' + str(data_time) + '接口方法.txt'
    if (banklist2 == []):
        write_in(str(id) + ';' + str(poi[0]) + ',' + str(poi[1]) + ';' + ';' + ';' + ';' + ';' + ';'
                 + ';' + '\r\n', data_dir2)
    else:
        for info in banklist2:
            write_in(str(id) + ';' + str(poi[0])+','+str(poi[1]) + ';' + str(info['name']) + ';' + str(info['lng']) + ',' + str(info['lat']) + ';' + str(info['addr']) + '\r\n', data_dir2)
    print(banklist2)

if __name__ == '__main__':
    data = pd.read_excel(import_dir)
    no_data = []
    for index, row in data.iterrows():
        searchWords = []
        coor = 0
        if(pd.notnull(row['address'])):
            searchWords.append(row['address'])
        if (pd.notnull(row['inst_name'])):
            if(row['inst_name'].find('中国邮政集团公司')>-1):
                searchWords.append(row['inst_name'][8:])
            else:
                searchWords.append(row['inst_name'])
        if (pd.isnull(row['inst_name'])&pd.isnull(row['address'])):
            print('no searchWord')
            if(isinstance(no_data,list)):
                no_data = pd.DataFrame([row])
            else:
                no_data = no_data.append([row], ignore_index=True)
            continue
        # 找坐标
        coor = getpoint(searchWords)
        # if (coor == 0):
        #     if ((len(str(row['v_jd'])) > 8) & (len(str(row['v_wd'])) > 8)):
        #         coor = str(row['v_jd']) + ',' + str(row['v_wd'])
        #         coor = changePoi3to4(coor.split(",")[0], coor.split(",")[1])
        #         coor = str(coor[0]) + ',' + str(coor[1])
        if(coor!= 0):
            print('-----------------fun1-----------------')
            fun1(coor, row['v_jgid+A1:C9513'])
            print('-----------------fun2-----------------')
            fun2(coor,row['v_jgid+A1:C9513'])
        else:
            if (isinstance(no_data, list)):
                no_data = pd.DataFrame([row])
            else:
                no_data = no_data.append([row], ignore_index=True)
    write_in_dataframe(no_data, '空缺' + str(data_time) + '.xlsx')
    mysql_helper.connection_close(connection)
