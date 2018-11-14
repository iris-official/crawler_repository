# -*- coding: utf-8 -*-
"""
@author: 冰蓝
@site: http://lanbing510.info
"""

import re
import urllib.request as urllib2
import requests
import sqlite3
import random
import threading
from bs4 import BeautifulSoup
import logging
import pymysql

import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

#登录，不登录不能爬取三个月之内的数据
import python.LianJiaSpidermaster.LianJiaLogIn as LianJiaLogIn


#Some User Agents
hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
    {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},\
    {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
    {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
    {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},\
    {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},\
    {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]
    

#北京区域列表
regions=[u"shijingshan",u"xicheng",u"chanyang",u"haidian",u"fengtai",u"dongcheng","tongzhou",u"changping",u"daxing",
         u"yizhuangkaifaqu",u"shunyi",u"fangshan",u"mentougou",u"pinggu",u"huairou",u"miyu",u"yanqing",
         u"yanjiao"]
MAXTRY = 5
WAITTIME = 5

def download_request(url, headers, num_retries=MAXTRY):
    if num_retries < 0:
        return None
    try:
        logging.info("downloading:" + url)
        html = requests.get(url, headers=headers, timeout=WAITTIME)
        html = html.text
    except Exception as e:
        logging.warning("Download error", e.reason)
        html = None
        if hasattr(e, "code") and 500 <= e.code < 600:
            return download_request(url, num_retries - 1)
    return html

lock = threading.Lock()


class SQLiteWraper(object):
    """
    数据库的一个小封装，更好的处理多线程写入
    """
    def __init__(self,path,command='',*args,**kwargs):  
        self.lock = threading.RLock() #锁  
        self.path = path #数据库连接参数  
        
        if command!='':
            conn=self.get_conn()
            cu=conn.cursor()
            cu.execute(command)
    
    def get_conn(self):
        config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'tian1314',
            'db': 'lianjia',
            'charset': 'utf8',
            'cursorclass': pymysql.cursors.DictCursor,
        }
        # Connect to the database
        connection = pymysql.connect(**config)
        return connection
      
    def conn_close(self,conn=None):  
        conn.close()  
    
    def conn_trans(func):  
        def connection(self,*args,**kwargs):  
            self.lock.acquire()  
            conn = self.get_conn()  
            kwargs['conn'] = conn  
            rs = func(self,*args,**kwargs)  
            self.conn_close(conn)  
            self.lock.release()  
            return rs  
        return connection  
    
    @conn_trans    
    def execute(self,command,method_flag=0,conn=None):  
        cu = conn.cursor()
        try:
            with conn.cursor() as cursor:
                # 执行sql语句，插入记录
                cursor.execute(command)
            # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
                conn.commit()
        except Exception as ex:
            print(ex)
    
    @conn_trans
    def fetchall(self,command="select name from xiaoqu WHERE  regionb like '%石景山%' or regionb like '%门头沟%'",conn=None):
        cu=conn.cursor()
        lists=[]
        try:
            cu.execute(command)
            lists=cu.fetchall()
        except  Exception as e:
            print(e)
            pass
        return lists


def gen_xiaoqu_insert_command(info_dict):
    """
    生成小区数据库插入命令
    """
    info_list=[u'小区名称',u'30天成交',u'大区域',u'小区域',u'小区户型',u'建造时间']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    command =('INSERT INTO xiaoqu VALUES (\''
     + t[0] + '\',\'' + str(t[1]) + '\',\'' + t[2] + '\',\'' + t[3] + '\',\'' + t[4] + '\',\'' + str(t[5]) + '\');')
    return command


def gen_chengjiao_insert_command(info_dict):
    """
    生成成交记录数据库插入命令
    """
    info_list=[u'链接',u'小区名称',u'户型',u'面积',u'朝向',u'楼层',u'建造时间',u'签约时间',u'签约单价',u'签约总价',u'房产类型',u'学区',u'地铁',u'装修程度',u'是否电梯',u'挂牌总价']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    command =('INSERT INTO chengjiao VALUES (\''
     + t[0] + '\',\'' + str(t[1]) + '\',\'' + t[2] + '\',\'' + t[3] + '\',\'' + t[4] + '\',\'' + str(t[5]) + '\',\''+ str(t[6])
              + '\',\''+ str(t[7]) + '\',\''+ str(t[8]) + '\',\''+ str(t[9]) + '\',\''+ str(t[10]) + '\',\''+ str(t[11])
              + '\',\'' + str(t[12]) + '\',\''+ str(t[13]) + '\',\''+ str(t[14]) + '\',\''+ str(t[15])
              + '\');')
    return command

def gen_zaishou_insert_command(info_dict):
    """
    生成在售记录数据库插入命令
    """
    info_list=[u'链接',u'小区域',u'小区名称',u'户型',u'面积',u'朝向',u'楼层',u'建造时间',u'房屋类型',u'单价',u'总价',u'房产类型',u'地铁',u'装修程度',u'是否电梯',u'关注人数',u'带看人数']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    command =('INSERT INTO zaishou VALUES (\''
     + t[0] + '\',\'' + str(t[1]) + '\',\'' + t[2] + '\',\'' + t[3] + '\',\'' + t[4] + '\',\'' + str(t[5]) + '\',\''+ str(t[6])
              + '\',\''+ str(t[7]) + '\',\''+ str(t[8]) + '\',\''+ str(t[9]) + '\',\''+ str(t[10]) + '\',\''+ str(t[11])
              + '\',\'' + str(t[12]) + '\',\''+ str(t[13]) + '\',\''+ str(t[14]) + '\',\''+ str(t[15])+ '\',\''+ str(t[16])
              + '\');')
    return command


def xiaoqu_spider(db_xq,url_page):
    """
    爬取页面链接中的小区信息
    """
    try:
        # req = urllib2.Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
        # source_code = urllib2.urlopen(req,timeout=10).read()
        source_code = download_request(url_page,headers=hds[random.randint(0,len(hds)-1)])
        # plain_text= unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code, from_encoding="utf_8")
    except (urllib2.HTTPError, urllib2.URLError) as e:
        print(e)
        exit(-1)
    except Exception as e:
        print(e)
        exit(-1)
    
    xiaoqu_list=soup.findAll('div',{'class':'info'})
    a = str(xiaoqu_list[0])
    for xq in xiaoqu_list:
        info_dict={}
        info_dict.update({u'小区名称':xq.find('a').text})
        content=xq.find('div',{'class':'houseInfo'})
        info = content.find('a').text
        if re.findall(r"30天成交(.+?)套",info):
            info_dict.update({u'30天成交': re.findall(r"30天成交(.+?)套",info)[0]})
        else:
            info_dict.update({u'30天成交': ''})
        content = xq.find('div', {'class': 'positionInfo'})
        info = content.findAll('a')
        if info:
            info_dict.update({u'大区域':info[0].text})
            info_dict.update({u'小区域':info[1].text})
        content = content.text.split("\n")
        info_dict.update({u'小区户型': content[4].strip()})
        if re.findall(r" / (.+?)年建成",content[5]):
            info_dict.update({u'建造时间':re.findall(r" / (.+?)年建成",content[5])[0]})
        else:
            info_dict.update({u'建造时间': ''})
        command=gen_xiaoqu_insert_command(info_dict)
        db_xq.execute(command,1)

    
def do_xiaoqu_spider(db_xq,region=u"昌平"):
    """
    爬取大区域中的所有小区信息
    """
    url_page=u"https://bj.lianjia.com/xiaoqu/"+region+"/"
    try:
        # req = urllib2.Request(url_page,headers=hds[random.randint(0,len(hds)-1)])
        # source_code = urllib2.urlopen(req,timeout=10).read()
        source_code = download_request(url_page, headers=hds[random.randint(0,len(hds)-1)])
        # plain_text=unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code, "html.parser")
    except (urllib2.HTTPError, urllib2.URLError) as e:
        print(e)
        return
    except Exception as e:
        print(e)
        return
    d="d="+soup.find('div',{'class':'page-box house-lst-page-box'}).get('page-data')
    exec(d)
    pattern = r'"totalPage":(.+?),"'
    total_pages = int(re.findall(pattern, d)[0])
    
    threads=[]
    for i in range(total_pages):
        url_page = u'https://bj.lianjia.com/xiaoqu/' +region +'/pg' + str(i+1) + '/'
        xiaoqu_spider(db_xq,url_page)
        t=threading.Thread(target=xiaoqu_spider,args=(db_xq,url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(u"爬下了 %s 区全部的小区信息" % region)


def chengjiao_spider(db_cj,url_page=u"http://bj.lianjia.com/chengjiao/pg1rs%E5%86%A0%E5%BA%AD%E5%9B%AD"):
    """
    爬取页面链接中的成交记录
    """
    try:
        source_code = download_request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        # plain_text=unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code)
    except (urllib2.HTTPError, urllib2.URLError) as e:
        print(e)
        exception_write('chengjiao_spider',url_page)
        return
    except Exception as e:
        print(e)
        exception_write('chengjiao_spider',url_page)
        return
    
    cj_list= soup.findAll('ul',{'class':'listContent'})[0].findAll('li')
    # cj_list = soup.findAll('li', {'class': 'listContent'})
    for cj in cj_list:
        info_dict={}
        href=cj.findAll('a')[0]
        if not href:
            continue
        info_dict.update({u'链接':href.attrs['href']})
        content = cj.findAll('a')
        content=content[1].text.split(' ')
        if content:
            info_dict.update({u'小区名称':content[0]})
            info_dict.update({u'户型':content[1]})
            info_dict.update({u'面积':content[2]})
        content = str(cj)
        content=cj.find('div',{'class':'houseInfo'})
        content=content.text.split('|')
        if content:
            info_dict.update({u'朝向':content[0].strip()})
            if (len(content) > 1):
                info_dict.update({u'装修程度':content[1].strip()})
            else:
                info_dict.update({u'装修程度': ''})
            if(len(content) > 2):
                info_dict.update({u'是否电梯': content[2].strip()})
            else:
                info_dict.update({u'是否电梯': ''})
        content=cj.findAll('div',{'class':'dealDate'})
        if content:
            info_dict.update({u'签约时间':content[0].text})
        content = cj.findAll('span', {'class': 'number'})
        if content:
            info_dict.update({u'签约总价': content[0].text})
            info_dict.update({u'签约单价': content[1].text})
        content = cj.findAll('div', {'class': 'positionInfo'})[0].text
        if content:
            info_dict.update({u'楼层': content.split(' ')[0]})
            if(re.findall('(.+?)年',content.split(' ')[1])):
                info_dict.update({u'建造时间': re.findall('(.+?)年',content.split(' ')[1])[0]})
        if(cj.findAll('div', {'class': 'dealHouseInfo'})):
            content = cj.findAll('div', {'class': 'dealHouseInfo'})[0].findAll('span')
            if str(content).find(u'满') != -1:
                info_dict.update({u'房产类型': re.findall('房屋满(.+?)</span>',str(content))[0]})
            else:
                info_dict.update({u'房产类型': ''})
            if(str(content).find(u'距') != -1):
                info_dict.update({u'地铁': re.findall('距(.+?)</span>',str(content))[0]})
            else:
                info_dict.update({u'地铁': ''})
            if (str(content).find(u'学') != -1):
                info_dict.update({u'学区': re.findall('学(.+?)</span>',str(content))[0]})
            else:
                info_dict.update({u'学区': ''})
        content = str(cj.findAll('span', {'class': 'dealCycleTxt'}))
        if re.findall('挂牌(.+?)万', content):
            info_dict.update({u'挂牌总价': re.findall('挂牌(.+?)万',str(content))[0]})
        else:
            info_dict.update({u'挂牌总价': ''})
        
        command=gen_chengjiao_insert_command(info_dict)
        db_cj.execute(command,1)


def xiaoqu_chengjiao_spider(db_cj,xq_name=u"冠庭园"):
    """
    爬取小区成交记录
    """
    url=u"http://bj.lianjia.com/chengjiao/rs"+xq_name+"/"
    try:
        # req = urllib2.Request(url,headers=hds[random.randint(0,len(hds)-1)])
        # source_code = urllib2.urlopen(req,timeout=10).read().encode(encoding='UTF8')
        source_code = download_request(url, headers=hds[random.randint(0, len(hds) - 1)])
        # plain_text=unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code)
    except (urllib2.HTTPError, urllib2.URLError) as e:
        print(e)
        exception_write('xiaoqu_chengjiao_spider',xq_name)
        return
    except Exception as e:
        print(e)
        exception_write('xiaoqu_chengjiao_spider',xq_name)
        return
    content=soup.find('div',{'class':'page-box house-lst-page-box'})
    total_pages=0
    if content:
        d="d="+content.get('page-data')
        pattern = r'"totalPage":(.+?),"'
        total_pages = int(re.findall(pattern, d)[0])
    
    threads=[]
    for i in range(total_pages):
        url_page=u"http://bj.lianjia.com/chengjiao/pg%drs%s/" % (i+1,xq_name)
        chengjiao_spider(db_cj,url_page)
        t=threading.Thread(target=chengjiao_spider,args=(db_cj,url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    
def do_xiaoqu_chengjiao_spider(db_xq,db_cj):
    """
    批量爬取小区成交记录
    """
    count=0
    xq_list=db_xq.fetchall()
    for xq in xq_list:
        xiaoqu_chengjiao_spider(db_cj,xq["name"])
        count+=1
        print('have spidered %d xiaoqu' % count)
    print('done')


def zaishou_spider(db_cj, url_page=u"http://bj.lianjia.com/chengjiao/pg1rs%E5%86%A0%E5%BA%AD%E5%9B%AD"):
    """
    爬取页面链接中的在售记录
    """
    try:
        source_code = download_request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        # plain_text=unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code)
    except (urllib2.HTTPError, urllib2.URLError) as e:
        print(e)
        exception_write('zaishou_spider', url_page)
        return
    except Exception as e:
        print(e)
        exception_write('zaishou_spider', url_page)
        return

    cj_list = soup.findAll('ul', {'class': 'sellListContent'})[0].findAll('li')
    for cj in cj_list:
        if (cj.find('div', {'class': 'houseInfo'})):
            info_dict = {}
            href = cj.findAll('a')[0]
            if not href:
                continue
            info_dict.update({u'链接': href.attrs['href']})
            content = cj.find('div', {'class': 'houseInfo'})
            content = content.text.strip().split('/')
            if content:
                info_dict.update({u'小区名称': content[0]})
                info_dict.update({u'户型': content[1]})
                info_dict.update({u'面积': content[2]})
                info_dict.update({u'朝向': content[3]})
                if len(content) == 5:
                    info_dict.update({u'装修程度': content[4]})
                if len(content) == 6:
                    info_dict.update({u'是否电梯': content[5]})
            content = cj.find('div', {'class': 'positionInfo'})
            content = content.text.strip().split('/')
            if content:
                info_dict.update({u'楼层': content[0]})
                if content[1].find(u'年') != -1:
                    info_dict.update({u'建造时间': re.findall('(.+?)年', content[1])[0]})
                if (content[1].find(u'塔楼') != -1):
                    info_dict.update({u'房屋类型': '塔楼'})
                if (content[1].find(u'板楼') != -1):
                    info_dict.update({u'房屋类型': '板楼'})
                if (content[1].find(u'塔板结合') != -1):
                    info_dict.update({u'房屋类型': '塔板结合'})
                info_dict.update({u'小区域': content[2]})
            content = cj.find('div', {'class': 'followInfo'}).text
            content = content.strip().split('/')
            if content:
                if content[0].find(u'关注') != -1:
                    info_dict.update({u'关注人数': re.findall('(.+?)人关注', content[0])[0]})
                if content[1].find(u'带看') != -1:
                    info_dict.update({u'带看人数': re.findall('(.+?)次带看', content[1])[0]})
            if content[0].find(u'满') != -1:
                info_dict.update({u'房产类型': re.findall('满(.+?)年', str(content))[0]})
            if (str(content).find(u'近') != -1):
                info_dict.update({u'地铁': '1'})
            if (str(content).find(u'万') != -1):
                info_dict.update({u'总价':re.findall('(\d+)',re.findall('(.+?)万', str(content))[0])[-1]})
            if (str(content).find(u'元') != -1):
                info_dict.update({u'单价': re.findall('价(.+?)元', str(content))[0]})

            command = gen_zaishou_insert_command(info_dict)
            db_cj.execute(command, 1)


def xiaoqu_zaishou_spider(db_cj, xq_name=u"冠庭园"):
    """
    爬取小区成交记录
    """
    url = u"http://bj.lianjia.com/ershoufang/rs" + xq_name + "/"
    try:
        # req = urllib2.Request(url,headers=hds[random.randint(0,len(hds)-1)])
        # source_code = urllib2.urlopen(req,timeout=10).read().encode(encoding='UTF8')
        source_code = download_request(url, headers=hds[random.randint(0, len(hds) - 1)])
        # plain_text=unicode(source_code)#,errors='ignore')
        soup = BeautifulSoup(source_code)
    except (urllib2.HTTPError, urllib2.URLError) as e:
        print(e)
        exception_write('xiaoqu_zaishou_spider', xq_name)
        return
    except Exception as e:
        print(e)
        exception_write('xiaoqu_zaishou_spider', xq_name)
        return
    content = soup.find('div', {'class': 'page-box house-lst-page-box'})
    total_pages = 0
    if content:
        d = "d=" + content.get('page-data')
        pattern = r'"totalPage":(.+?),"'
        total_pages = int(re.findall(pattern, d)[0])

    threads = []
    for i in range(total_pages):
        url_page = u"http://bj.lianjia.com/ershoufang/pg%drs%s/" % (i + 1, xq_name)
        t = threading.Thread(target=zaishou_spider, args=(db_cj, url_page))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def do_xiaoqu_zaishou_spider(db_xq, db_cj):
    """
    批量爬取小区在售记录
    """
    count = 0
    xq_list = db_xq.fetchall()
    for xq in xq_list:
        xiaoqu_zaishou_spider(db_cj, xq["name"])
        count += 1
        print('have spidered %d xiaoqu' % count)
    print('done')

def exception_write(fun_name,url):
    """
    写入异常信息到日志
    """
    lock.acquire()
    f = open('log.txt','a')
    line="%s %s\n" % (fun_name,url)
    f.write(line)
    f.close()
    lock.release()


def exception_read():
    """
    从日志中读取异常信息
    """
    lock.acquire()
    f=open('log.txt','r')
    lines=f.readlines()
    f.close()
    f=open('log.txt','w')
    f.truncate()
    f.close()
    lock.release()
    return lines


def exception_spider(db_cj):
    """
    重新爬取爬取异常的链接
    """
    count=0
    excep_list=exception_read()
    while excep_list:
        for excep in excep_list:
            excep=excep.strip()
            if excep=="":
                continue
            excep_name,url=excep.split(" ",1)
            if excep_name=="chengjiao_spider":
                chengjiao_spider(db_cj,url)
                count+=1
            elif excep_name=="xiaoqu_chengjiao_spider":
                xiaoqu_chengjiao_spider(db_cj,url)
                count+=1
            else:
                print("wrong format")
            print("have spidered %d exception url" % count)
        excep_list=exception_read()
    print('all done ^_^')
    


if __name__=="__main__":
    command="create table if not exists xiaoqu (Name varchar(18) primary key UNIQUE, chengjiaoliang TEXT, regionb TEXT, regions TEXT, style TEXT, year TEXT)"
    db_xq=SQLiteWraper('lianjia-xq.db',command)
    
    command="create table if not exists chengjiao (href varchar(100) primary key UNIQUE, name TEXT, style TEXT, area TEXT, orientation TEXT, floor TEXT, year TEXT, sign_time TEXT, unit_price TEXT, total_price TEXT,fangchan_class TEXT, school TEXT, subway TEXT, zhuangxiu TEXT, dianti TEXT, guapai TEXT)"
    db_cj=SQLiteWraper('lianjia-cj.db',command)

    command = "create table if not exists zaishou (href varchar(100) primary key UNIQUE,regions TEXT, name TEXT, style TEXT, area TEXT, orientation TEXT, floor TEXT, year TEXT, fangwuleixing TEXT, danjia TEXT, zongjia TEXT,fangchanleixing TEXT, ditie TEXT, zhangxiu TEXT, dianti TEXT, guanzhurenshu TEXT, daikanrenshu TEXT)"
    db_cj = SQLiteWraper('lianjia-cj.db', command)

    #爬下所有的小区信息
    # for region in regions:
    #     do_xiaoqu_spider(db_xq,region)
    
    #爬下所有小区里的成交信息
    do_xiaoqu_chengjiao_spider(db_xq,db_cj)

    # 爬下所有小区里的在售信息
    # do_xiaoqu_zaishou_spider(db_xq,db_cj)
    
    #重新爬取爬取异常的链接
    exception_spider(db_cj)

