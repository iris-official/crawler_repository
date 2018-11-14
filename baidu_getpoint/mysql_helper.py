# -*- coding: utf-8 -*-

import pymysql.cursors

def mysql_login():
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'tian1314',
        'db': 'wangdian',
        'charset': 'utf8',
        'cursorclass': pymysql.cursors.DictCursor,
    }
    # Connect to the database
    connection = pymysql.connect(**config)
    return connection

def mail_format_dic2list(tracks_dict):
    tracks_list = []
    valid = '1'
    for every_yj in tracks_dict:
        for every_line in every_yj:
            line = []
            line.append(every_line['crawler_time'])
            line.append(every_line['yjhm'])
            line.append(every_line['status'])
            line.append(every_line['description'])
            line.append(every_line['do_city'])
            line.append(every_line['do_time'])
            line.append(valid)
            tracks_list.append(line)
    return tracks_list
def fun1_sql_generater(id, html_con, CITY_CODE, KEY_WORD):
    ori_sql = ('INSERT INTO gansu1 (jgid, html,city,keyword) VALUES (\''
    + str(id) + '\',\'' + str(html_con) + '\',\'' + str(CITY_CODE) + '\',\'' + str(KEY_WORD)+'\');')
    return ori_sql
def fun2_sql_generater(id, html_con, CITY_CODE, KEY_WORD):
    ori_sql = ('INSERT INTO gansu2 (jgid, html,city,keyword) VALUES (\''
    + str(id) + '\',\'' + str(html_con) + '\',\'' + str(CITY_CODE) + '\',\'' + str(KEY_WORD)+ '\');')
    return ori_sql
def fun1_sql_insert(id, html_con, CITY_CODE, KEY_WORD, connection):
    sql = fun1_sql_generater(id, html_con, CITY_CODE, KEY_WORD)
    # print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()
def fun2_sql_insert(id, html_con, CITY_CODE, KEY_WORD, connection):
    sql = fun2_sql_generater(id, html_con, CITY_CODE, KEY_WORD)
    # print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()

def bank1_info_sql_generater(city, province, jgid, geo1, name, geo2, dis,addr, tag, phone, bussiness_time):
    ori_sql = ('INSERT INTO bank1 (city, province, jgid, geo1, name, geo2, dis,addr, tag, phone, bussiness_time) VALUES (\''
               + str(city) + '\',\'' + str(province) + '\',\''+ str(jgid) + '\',\'' + str(geo1) + '\',\'' + str(name) + '\',\'' + str(geo2)
               + '\',\'' + str(dis) + '\',\'' + str(addr)+ '\',\'' + str(tag)+ '\',\'' + str(phone)+ '\',\'' + str(bussiness_time)+ '\');')
    return ori_sql
def bank1_info_sql_insert(city, province, jgid, geo1, name, geo2, dis,addr, tag, phone, bussiness_time, connection):
    sql = bank1_info_sql_generater(city, province, jgid, geo1, name, geo2, dis,addr, tag, phone, bussiness_time)
    # print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()(id, html_con, CITY_CODE, KEY_WORD)
def bank2_info_sql_generater(city, province, jgid, geo1, name, geo2, addr):
    ori_sql = ('INSERT INTO bank2 (city, province, jgid, geo1, name, geo2, addr) VALUES (\''
               + str(city) + '\',\'' + str(province)+ '\',\'' + str(jgid) + '\',\'' + str(geo1) + '\',\'' + str(name) + '\',\'' + str(geo2)
               + '\',\'' + str(addr) + '\');')
    return ori_sql
def bank2_info_sql_insert(city, province, jgid, geo1, name, geo2, addr, connection):
    sql = bank2_info_sql_generater(city, province, jgid, geo1, name, geo2, addr)
    # print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()(id, html_con, CITY_CODE, KEY_WORD)

def bus1_info_sql_generater(city, province, jgid, geo1, name, geo2, dis, addr):
    ori_sql = ('INSERT INTO bus1 (city, province, jgid, geo1, name, geo2, dis, addr) VALUES (\''
               + str(city) + '\',\'' + str(province)+ '\',\'' + str(jgid) + '\',\'' + str(geo1) + '\',\'' + str(name) + '\',\'' + str(geo2)
               + '\',\'' + str(dis) + '\',\'' + str(addr) + '\');')
    return ori_sql
def bus1_info_sql_insert(city, province, jgid, geo1, name, geo2, dis, addr, connection):
    sql = bus1_info_sql_generater(city, province, jgid, geo1, name, geo2, dis, addr)
    # print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()(id, html_con, CITY_CODE, KEY_WORD)
def bus2_info_sql_generater(city, province, jgid, geo1, name, geo2, addr):
    ori_sql = ('INSERT INTO bus2 (city, province, jgid, geo1, name, geo2, addr) VALUES (\''
               + str(city) + '\',\'' + str(province)+ '\',\'' + str(jgid) + '\',\'' + str(geo1) + '\',\'' + str(name) + '\',\'' + str(geo2)
               + '\',\'' + str(addr) + '\');')
    return ori_sql
def bus2_info_sql_insert(city, province, jgid, geo1, name, geo2, addr, connection):
    sql = bus2_info_sql_generater(city, province, jgid, geo1, name, geo2, addr)
    # print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()(id, html_con, CITY_CODE, KEY_WORD)


def school1_info_sql_generater(city, province, jgid, geo1, name, geo2, dis, addr, tag):
    ori_sql = ('INSERT INTO school1 (city, province, jgid, geo1, name, geo2, dis, addr, tag) VALUES (\''
               + str(city) + '\',\'' + str(province)+ '\',\'' + str(jgid) + '\',\'' + str(geo1) + '\',\'' + str(name) + '\',\'' + str(geo2)
               + '\',\'' + str(dis) + '\',\'' + str(addr) + '\',\'' + str(tag) + '\');')
    return ori_sql
def school1_info_sql_insert(city, province, jgid, geo1, name, geo2, dis, addr, tag, connection):
    sql = school1_info_sql_generater(city, province, jgid, geo1, name, geo2, dis, addr, tag)
    # print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()(id, html_con, CITY_CODE, KEY_WORD)
def school2_info_sql_generater(city, province, jgid, geo1, name, geo2, addr):
    ori_sql = ('INSERT INTO school2 (city, province, jgid, geo1, name, geo2, addr) VALUES (\''
               + str(city) + '\',\'' + str(province) + '\',\'' + str(jgid) + '\',\'' + str(geo1) + '\',\'' + str(name) + '\',\'' + str(geo2)
               + '\',\'' + str(addr) + '\');')
    return ori_sql
def school2_info_sql_insert(city, province, jgid, geo1, name, geo2, addr, connection):
    sql = school2_info_sql_generater(city, province, jgid, geo1, name, geo2, addr)
    # print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()(id, html_con, CITY_CODE, KEY_WORD)

def find_the_last(connection):
    sql = 'SELECT jgid FROM school1 ORDER BY id DESC LIMIT 1 '
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
            result = cursor.fetchall()[0]['jgid']
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
        return result
    except Exception as ex:
        print(ex)
        # connection.close()(id, html_con, CITY_CODE, KEY_WORD)
def delete_the_record(jgid,connection):
    sql1 = 'DELETE from bank1 where id >=(SELECT MIN(a.id) from (select id from bank1 where jgid = '+str(jgid) +')a)'
    sql2 = 'DELETE from bank2 where id >=(SELECT MIN(a.id) from (select id from bank2 where jgid = '+str(jgid) +')a)'
    sql3 = 'DELETE from bus1 where id >=(SELECT MIN(a.id) from (select id from bus1 where jgid = ' + str(jgid) + ')a)'
    sql4 = 'DELETE from bus2 where id >=(SELECT MIN(a.id) from (select id from bus2 where jgid = ' + str(jgid) + ')a)'
    sql5 = 'DELETE from school1 where id >=(SELECT MIN(a.id) from (select id from school1 where jgid = ' + str(jgid) + ')a)'
    sql6 = 'DELETE from school2 where id >=(SELECT MIN(a.id) from (select id from school2 where jgid = ' + str(jgid) + ')a)'
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql1)
            cursor.execute(sql2)
            cursor.execute(sql3)
            cursor.execute(sql4)
            cursor.execute(sql5)
            cursor.execute(sql6)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
        # connection.close()(id, html_con, CITY_CODE, KEY_WORD)
def connection_close(connection):
    connection.close()