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
# AKT = 'JO5BZ-T4QKF-KKQJ2-JGUAY-YMY6O-KPBGB'
# AKT = 'ATRBZ-3YEWF-JV5JS-NXJ2A-AHX7J-MTFS3'
# AKT = 'FAFBZ-JIXKG-5M3QI-I7FG4-TKC4E-S4BE2'
AKT = 'VWWBZ-5HPWX-CNX4F-7QDLC-XSIQE-LUFQV'
AK = 'UBGFvk0LoUCduDmZyMfKvRoGxHLXkuUk'

county_NAME = '城市信息错误201806061329'
import_dir = '城市信息错误201806061329.xlsx'

URL = 'http://map.baidu.com/'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
connection = mysql_helper.mysql_login()
data_time = time.strftime('%Y%m%d', time.localtime(time.time()))
data_time1 = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
requests.adapters.DEFAULT_RETRIES = 5

def write_in(data,data_dir):
    with codecs.open(data_dir, 'a+', 'utf-8') as file_obj:
            file_obj.write(data)
    file_obj.close()
def write_in_dataframe(data, data_dir):
    data.to_excel(data_dir, sheet_name='result', index=False, header=True)
def changePoi4to3(x ,y):
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
def tencent_to_baidu(x,y):
    url = 'http://api.gpsspg.com/convert/coord/'
    parameters = {
        'oid': '8354',
        'key': 'FE846B1130854920AF8C7B092EEACED3',
        'from': 3,
        'to': 2,
        'latlng' : str(y) + ',' + str(x),
        'output':'json'
    }
    response = get_request(url, parameters)
    html = response.text
    try:
        decodejson = json.loads(html).get('result')[0]
        coor = []
        coor.append(decodejson.get('lng'))
        coor.append(decodejson.get('lat'))
    except:
        print('续订坐标转换')
        sys.exit()
    return coor
def cal_samper(x,y):
    total = 0
    count = 0
    for item in x:
        total = total +1
        for itemy in y:
            if(item == itemy):
                count = count + 1
                break
    return count/total
def get_request(url, parameters, headers = headers, num_retries=MAXTRY):
    html = ''
    r = requests.session()
    try:
        html = r.get(url, params=parameters, headers=headers)
        sleep(1)
        if (html.text.find('配额超限')>-1):
            print('bank 天配额超限，限制访问')
            sys.exit()
    except Exception as e:
        sleep(2)
        # recursively retry 5xx HTTP errors 判断返回的异常的代码，是否在500到600之间
        return get_request(url, num_retries - 1)
    return html
def insert_searchword(row):
    searchWords = []
    if ((re.findall(r'\d+', str(row['address'])) != [])or(str(row['address'])[-1] == '乡'or str(row['address'])[-1] == '镇' or
                                                                 str(row['address'])[-1] == '村' or str(row['address'])[-1] == '坪')):
        searchWords.append(row['address'])
    else:
        if(str(row['address']).find('乡政府')>-1):
            searchWords.append(row['address'][:row['address'].find('乡')+1])
        else:
            searchWords.append('')
    if ((re.findall(r'\d+', str(row['v_mph'])) != []) & (row['v_mph'] != 0)):
        searchWords.append(str(row['v_sfmc']) + str(row['v_dsmc']) + str(row['v_xsmc']) + str(row['v_jdmc']) + str(row['v_mph']) + '号')
    else:
        searchWords.append(str(row['v_sfmc']) + str(row['v_dsmc']) + str(row['v_xsmc']) + str(row['v_jdmc']) + str(row['v_mph']))
    if (pd.notnull(row['inst_name'])):
        if (row['inst_name'].find('中国邮政集团公司') > -1):
            searchWords.append(row['inst_name'][8:])
        else:
            searchWords.append(row['inst_name'])
    else:
        searchWords.append('')
    return searchWords
def get_list_baidu(searchWords,CITY_CODE):
    point_list = [[] for i in range(3)]
    index = 0
    for searchWord in searchWords:
        point = {}
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
        html = get_request(URL, parameters);
        html = html.text.encode('latin-1').decode('unicode_escape')
        pattern = r'"acc_flag":(.+?)"ty"'
        html = re.findall(pattern, html)
        for htm in html:
            try:
                pattern = r'},"name":"(.+?)","'
                pattern1 = r'geo":"1\|(.+?);'
                pattern3 = r'"addr":"(.+?)","'
                pattern4 = r',"di_tag":"(.+?)","'
                point["name"] = re.findall(pattern, htm)[0]
                point["addr"] = re.findall(pattern3, htm)[0]
                point["di_tag"] = re.findall(pattern4, htm)[0]
                point["coor"] = re.findall(pattern1, htm)[0]
                point_copy = point.copy()
                point_list[index].append(point_copy)
            except Exception as ex:
                print(ex)
        index = index + 1
    return  point_list
def get_list_tencent(searchWords,CITY_NAME):
    index = 0
    point_list = [[] for i in range(3)]
    for searchWord in searchWords:
        point = {}
        if (searchWord != ''):
            parameters = {
                'output': json,
                'keyword': searchWord,
                'region': CITY_NAME,
                'region_fix': 1,
                'key': AKT,
                'policy': 1
            }
            html = get_request('http://apis.map.qq.com/ws/place/v1/suggestion', parameters);
            html = json.loads(html.text).get('data')
            # sleep(10)
            for htm in html:
                try:
                    point["name"] = htm.get('title')
                    point["addr"] = htm.get('address')
                    point["di_tag"] = htm.get('category')
                    coor = htm.get('location')
                    point["coor"] = str(coor.get('lng')) + ',' + str(coor.get('lat'))
                    point_copy = point.copy()
                    point_list[index].append(point_copy)
                except Exception as ex:
                    print(ex)
        index = index + 1
    return point_list
def certain_poi(point_list,searchWords):
    # 0:address
    # 1:合成得地址
    # 2：机构名称
    index = 0
    # 按是否为邮局判断
    for point in point_list:
        # print(searchWords[index])
        index = index + 1
        for point_item in point:
            if (point_item):
                try:
                    pattern1 = r'\((.+?)\)'
                    if ((point_item['di_tag'].find('邮局') > -1) & (
                                cal_samper(searchWords[2], point_item["name"]) == 1)):
                        print(point_item["name"] + '----------' + searchWords[2] + ':' + str(
                            cal_samper(point_item["name"], searchWords[2])))
                        return point_item['coor']
                    if (re.findall(pattern1, point_item["name"]) != []):
                        if ((point_item['di_tag'].find('邮局') > -1) &
                                (cal_samper(re.findall(pattern1, point_item["name"])[0], searchWords[2]) > 0.86)):
                            print(
                                re.findall(pattern1, point_item["name"])[0] + '----------' + searchWords[2] + ':' + str(
                                    cal_samper(re.findall(pattern1, point_item["name"])[0], searchWords[2])))
                            return point_item['coor']
                    if (re.findall(pattern1, point_item["name"]) == []):
                        if ((point_item['di_tag'].find('邮局') > -1)
                                & (cal_samper(point_item["name"], searchWords[2]) > 0.86)
                                & (point_item["name"] != '中国邮政')):
                            print(point_item["name"] + '----------' + searchWords[2] + ':' + str(
                                cal_samper(point_item["name"], searchWords[2])))
                            return point_item['coor']
                    if ((point_item['di_tag'].find('邮局') > -1) & (
                                cal_samper(point_item["addr"], searchWords[0]) > 0.9)):
                        print(point_item["addr"] + '----------' + searchWords[0] + ':' + str(
                            cal_samper(point_item["addr"], searchWords[0])))
                        return point_item['coor']
                    if ((point_item['di_tag'].find('邮局') > -1) & (
                                cal_samper(point_item["addr"], searchWords[1]) > 0.9)):
                        print(point_item["addr"] + '----------' + searchWords[1] + ':' + str(
                            cal_samper(point_item["addr"], searchWords[1])))
                        return point_item['coor']
                    pattern2 = r'\((.+?)邮政'
                    pattern3 = r'县(.+?)邮政'
                    pattern4 = r'省(.+?)邮政'
                    pattern5 = r'市(.+?)邮政'
                    try:
                        if (re.findall(pattern2, point_item["name"]) != []):
                            if ((point_item['di_tag'].find('邮局') > -1) &
                                    ((re.findall(pattern2, point_item["name"])[-1] == re.findall(pattern3, searchWords[2])[-1]
                            ) or (re.findall(pattern2, point_item["name"])[-1] == re.findall(pattern4, searchWords[2])[-1]
                            )or (re.findall(pattern2, point_item["name"])[-1] == re.findall(pattern5, searchWords[2])[-1]
                            ))):
                                print(
                                    re.findall(pattern2, point_item["name"])[0] + '----------' + searchWords[2] + ':' + str(
                                        cal_samper(re.findall(pattern2, point_item["name"])[-1], searchWords[2])))
                                return point_item['coor']
                    except Exception as ex:
                        print(ex)
                    a = cal_samper(searchWords[2], point_item["addr"])
                    if ((point_item['di_tag'].find('邮局') > -1) &
                            (cal_samper(searchWords[2], point_item["addr"])> 0.9)):
                        print(
                            point_item["addr"] + '----------' + searchWords[2] + ':' + str(
                                cal_samper(searchWords[2], point_item["addr"])))
                        return point_item['coor']
                except Exception as ex:
                    print(ex)
    # 按地址判断
    if ((searchWords[0] == '')or(searchWords[0][-1] != '乡') & (searchWords[0][-1] != '镇') &
            (searchWords[0][-1] != '村') & (searchWords[0][-1] != '坪')& (searchWords[0].find('乡政府') == -1)):
        try:
                for point_item in point_list[0]:
                    if((point_item["addr"][-1]!='市')&(point_item["addr"][-1]!='区')&(point_item["addr"][-1]!='县')):
                        if((cal_samper(point_item["addr"], searchWords[0]) > 0.96)):
                            print(point_item["addr"] + '----------' + searchWords[0] + ':' + str(
                                cal_samper(point_item["addr"], searchWords[0])))
                            return point_item['coor']
                for point_item in point_list[1]:
                    if((point_item["addr"][-1]!='市')&(point_item["addr"][-1]!='区')&(point_item["addr"][-1]!='县')):
                        if ((cal_samper(point_item["addr"], searchWords[1]) > 0.96)):
                            print(point_item["addr"] + '----------' + searchWords[1] + ':' + str(
                                cal_samper(point_item["addr"], searchWords[1])))
                            return point_item['coor']
        except Exception as ex:
            print(ex)
    else:
        if ((len(point_list[1]) > 0) & (point_list[1] != '')):
            for point_item in point_list[1]:
                if (cal_samper(searchWords[0], point_item['addr']) == 1):
                    print(point_item['addr'] + '----------' + searchWords[0] + ':' + str(cal_samper(searchWords[0], point_item['addr'])))
                    return point_item['coor']
                if ((cal_samper(point_item['addr'], searchWords[0]) > 0.9) & (searchWords[0][-1] == point_item['addr'][-1])):
                    print(point_item['addr'] + '----------' + searchWords[0] + ':' + str(cal_samper(point_item['addr'], searchWords[0])))
                    return point_item['coor']
                try:
                    if ((cal_samper(point_item['name'], searchWords[0]) > 0.9) &(searchWords[0].find('乡政府') > -1)
                            & (point_item['di_tag'].find('政府') > -1)):
                        print(searchWords[0] + '----------' +point_item['addr'] + ':' + str(
                            cal_samper(point_item['name'], searchWords[0])))
                        return point_item['coor']
                except Exception as e:
                    print('why dont have tag')
            try:
                if ((point_item['di_tag'].find('行政地名') > -1) & (
                        len(searchWords[0]) - searchWords[0].find(point_item['name'][:-1]) == len(point_item['name']))):
                    print(searchWords[0] + '----------' + point_item['name'] )
                    return point_item['coor']
            except Exception as e:
                print('why dont have tag')
        if ((len(point_list[0]) > 0) & (point_list[0] != '')):
            for point_item in point_list[0]:
                if (cal_samper(searchWords[0], point_item['addr']) == 1):
                    print(point_item['addr'] + '----------' + searchWords[0] + ':' + str(cal_samper(searchWords[0], point_item['addr'])))
                    return point_item['coor']
                if ((cal_samper(point_item['addr'], searchWords[0]) > 0.9) & (searchWords[0][-1] == point_item['addr'][-1])):
                    print(point_item['addr'] + '----------' + searchWords[0] + ':' + str(
                        cal_samper(point_item['addr'], searchWords[0])))
                    return point_item['coor']
                if ((cal_samper(point_item['name'], searchWords[0]) > 0.9) &(searchWords[0].find('乡政府') > -1)
                        & (searchWords[0].find('乡政府') > -1)
                        & (point_item['di_tag'].find('政府') > -1)
                    ):
                    print(searchWords[0] + '----------' +point_item['addr'] + ':' + str(
                        cal_samper(point_item['name'], searchWords[0])))
                    return point_item['coor']
                if((point_item['di_tag'].find('行政地名') > -1)&(len(searchWords[0])-searchWords[0].find(point_item['name'][:-1]) == len(point_item['name']))):
                    print(searchWords[0] + '----------' + point_item['name'] )
                    return point_item['coor']

    return 0

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
    wrong_city = []
    # baidu_point = []
    # tencent_point = []
    mark = ''
    try:
        for index, row in data.iterrows():
            coor = 0
            searchWords = insert_searchword(row)
            CITY_NAME = row['v_dsmc']
            CITY_CODE = search_citycode(CITY_NAME)
            if (CITY_CODE == None):
                if (isinstance(wrong_city, list)):
                    wrong_city = pd.DataFrame([row])
                else:
                    wrong_city = wrong_city.append([row], ignore_index=True)
                continue
            point_list_baidu = get_list_baidu(searchWords, CITY_CODE)
            coor = certain_poi(point_list_baidu, searchWords)
            mark = 'baidu'
            if ((coor == 0) or (coor == '')):
                point_list_tencent = get_list_tencent(searchWords, CITY_NAME)
                coor = certain_poi(point_list_tencent, searchWords)
                mark = 'tencent'
            if(coor!= 0):
                print('the coor is :' + str(coor))
                if (mark == 'baidu'):
                    coor = changePoi4to3(coor.split(",")[0],coor.split(",")[1])
                    row['lng'] = str(coor[0])
                    row['lat'] = str(coor[1])
                    if (isinstance(has_point, list)):
                        has_point = pd.DataFrame([row])
                    else:
                        has_point = has_point.append([row], ignore_index=True)
                if (mark == 'tencent'):
                    coor = tencent_to_baidu(coor.split(",")[0], coor.split(",")[1])
                    row['lng'] = str(coor[0])
                    row['lat'] = str(coor[1])
                    if (isinstance(has_point, list)):
                        has_point = pd.DataFrame([row])
                    else:
                        has_point = has_point.append([row], ignore_index=True)
            else:
                if (isinstance(no_point, list)):
                    no_point = pd.DataFrame([row])
                else:
                    no_point = no_point.append([row], ignore_index=True)
    except:
        print('balabala')
    if (isinstance(has_point, list)):
        has_point = pd.DataFrame([])
    if (isinstance(no_point, list)):
        no_point = pd.DataFrame([])
    if (isinstance(wrong_city, list)):
        wrong_city = pd.DataFrame([])
    write_in_dataframe(no_point,  county_NAME + '未添补坐标' + str(data_time1) + '.xlsx')
    write_in_dataframe(has_point, county_NAME + '已修正信息' + str(data_time1) + '.xlsx')
    write_in_dataframe(wrong_city, '城市信息错误' + str(data_time1) + '.xlsx')
    easygui.msgbox("经纬度获取第一个程序完成！")
    # write_in_dataframe(tencent_point, CITY_NAME + '已修正信息' + str(data_time1) + 'tencent.xlsx')

