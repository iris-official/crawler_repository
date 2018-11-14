import requests
import re
import codecs
import time
import math
URL = 'http://map.baidu.com/';
# 北京
cityCode = '131'

searchWords = {'五福家园','文科龙苑','新城东里','富燕新村四区'}
data_time = time.strftime('%Y%m%d', time.localtime(time.time()))
data_dir = 'result'+str(data_time)+'经纬度.txt'

def write_in(data):
    with codecs.open(data_dir, 'a+', 'utf-8') as file_obj:
            file_obj.write(data)
    file_obj.close()

for searchWord in searchWords:
    print('searchWord:' + searchWord)
    parameters = {
        'qt': 's',
        'c': cityCode,
        'wd': searchWord,
        'rn': '10',
        'ie': 'utf-8',
        'oue': '1',
        'fromproduct': 'jsapi',
        'res': 'api',
        'callback': 'BMap._rd._cbk58851',
        'ak': 'E4805d16520de693a3fe707cdc962045'
    }
    htm = requests.get(URL, params=parameters);
    htm = htm.text.encode('latin-1').decode('unicode_escape')

    pattern = r'(?<=\b"\},"name":").+?(?=")'
    names = re.findall(pattern, htm)

    x = 0
    y = 0
    for name in names:
        if(name.find(searchWord) > -1):
            # html = etree.HTML(htm)
            pattern1 = name+r'(.+?),{"acc_flag"'
            html_name = re.findall(pattern1, htm)
            patternx = r'"x":(.+?),'
            patterny = r'"y":(.+?)},'
            x = re.findall(patternx, str(html_name))[0]
            y = re.findall(patterny, str(html_name))[0]

            bd_x = x - 0.0065;

            bd_y = y - 0.006;

            z = math.sqrt(bd_x * bd_x + bd_y * bd_y) - 0.00002 * math.sin(bd_y * x);

            # double theta = atan2(bd_y, bd_x) - 0.000003 * cos(bd_x * x_pi);
            break;
    write_in(searchWord+','+x+','+y+'\n')
