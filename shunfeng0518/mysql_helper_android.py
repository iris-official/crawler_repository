# -*- coding: utf-8 -*-

import pymysql.cursors


def mysql_login():
    config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "tian1314",
        "db": "shunfeng_android",
        "charset": "utf8",
        "cursorclass": pymysql.cursors.DictCursor,
    }
    # Connect to the database
    connection = pymysql.connect(**config)
    return connection


def connection_close(connection):
    connection.close()

def select_danhao(connection):
    select_sql1 = 'select DISTINCT(yjhm) from all_mail;'
    select_sql2 = 'select DISTINCT(yjhm) from no_mail;'
    select_sql3 = 'select distinct(yjhm) from kd100_mail_info;'
    select_sql4 = 'select distinct(yjhm) from kd100_mail_info_1;'
    result = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_sql1)
            result1_list = [item['yjhm'] for item in cursor.fetchall()] #生成的所有单号
            cursor.execute(select_sql2)
            result2_list = [item['yjhm'] for item in cursor.fetchall()] #已抓过的无记录单号
            cursor.execute(select_sql3)
            result3_list = [item['yjhm'] for item in cursor.fetchall()] #已抓过的有记录单号
            cursor.execute(select_sql4)
            result4_list = [item['yjhm'] for item in cursor.fetchall()]  # 已抓过的有记录单号

            result_tmp1 = list(set(result1_list).difference(set(result2_list))) #相减后的单号(没有记录的单号)
            result_tmp2 = list(set(result_tmp1).difference(set(result3_list))) #相减后的单号(已经获取的单号)
            result = list(set(result_tmp2).difference(set(result4_list)))
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
    result = [str(item) for item in result]
    #return sorted(result)
    return result

def select_danhao_a(connection):
    select_sql1 = 'select DISTINCT(yjhm) from all_mail_a;'
    select_sql2 = 'select DISTINCT(yjhm) from no_mail;'
    select_sql3 = 'select distinct(yjhm) from kd100_mail_info;'
    select_sql4 = 'select distinct(yjhm) from kd100_mail_info_1;'
    result = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_sql1)
            result1_list = [item['yjhm'] for item in cursor.fetchall()] #生成的所有单号
            cursor.execute(select_sql2)
            result2_list = [item['yjhm'] for item in cursor.fetchall()] #已抓过的无记录单号
            cursor.execute(select_sql3)
            result3_list = [item['yjhm'] for item in cursor.fetchall()] #已抓过的有记录单号
            cursor.execute(select_sql4)
            result4_list = [item['yjhm'] for item in cursor.fetchall()]  # 已抓过的有记录单号

            result_tmp1 = list(set(result1_list).difference(set(result2_list))) #相减后的单号(没有记录的单号)
            result_tmp2 = list(set(result_tmp1).difference(set(result3_list))) #相减后的单号(已经获取的单号)
            result = list(set(result_tmp2).difference(set(result4_list)))
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
    result = [str(item) for item in result]
    #return sorted(result)
    return result

def select_danhao_b(connection):
    select_sql1 = 'select DISTINCT(yjhm) from all_mail_b;'
    select_sql2 = 'select DISTINCT(yjhm) from no_mail;'
    select_sql3 = 'select distinct(yjhm) from kd100_mail_info;'
    select_sql4 = 'select distinct(yjhm) from kd100_mail_info_1;'
    result = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_sql1)
            result1_list = [item['yjhm'] for item in cursor.fetchall()] #生成的所有单号
            cursor.execute(select_sql2)
            result2_list = [item['yjhm'] for item in cursor.fetchall()] #已抓过的无记录单号
            cursor.execute(select_sql3)
            result3_list = [item['yjhm'] for item in cursor.fetchall()] #已抓过的有记录单号
            cursor.execute(select_sql4)
            result4_list = [item['yjhm'] for item in cursor.fetchall()]  # 已抓过的有记录单号

            result_tmp1 = list(set(result1_list).difference(set(result2_list))) #相减后的单号(没有记录的单号)
            result_tmp2 = list(set(result_tmp1).difference(set(result3_list))) #相减后的单号(已经获取的单号)
            result = list(set(result_tmp2).difference(set(result4_list)))  # 相减后的单号(已经获取的单号)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
    result = [str(item) for item in result]
    #return sorted(result)
    return result

