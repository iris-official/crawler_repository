# -*- coding: utf-8 -*-

import pymysql.cursors

def mysql_login():
    config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "tian1314",
        'db': 'shunfeng2',
        'charset': 'utf8',
        'cursorclass': pymysql.cursors.DictCursor,
    }
    # Connect to the database
    connection = pymysql.connect(**config)
    return connection

# 将sql处理成可一次性插入多条的语句
def process_sql_str(ori_sql, data_list):
    line_sql = ''
    for line in data_list:
        line_sql = line_sql + '(\'' + ('\', \'').join(line) + '\'),'
    sql = ori_sql + line_sql[:-1] + ';'
    return sql


def mail_wuliu_insert(wuliu_info_list, connection):
    ori_sql = 'INSERT INTO mail_wuliu (yjhm, time, status, crawler_time) VALUES '
    sql = process_sql_str(ori_sql, wuliu_info_list)
    #print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)

def mail_info_insert(danhao_info_list, connection):
    ori_sql = 'INSERT INTO mail_info (yjhm, locations, locations_arrow, product_name, last_update_time, status, crawler_time) VALUES '
    sql = process_sql_str(ori_sql, danhao_info_list)
    #print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)

def no_record_mail_insert(no_record_list, connection):
    ori_sql = 'INSERT INTO no_record_mail (yjhm, crawler_time) VALUES '
    sql = process_sql_str(ori_sql, no_record_list)
    #print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)

def no_record_mail_insert2(no_record_list, connection):
    ori_sql = 'INSERT INTO no_record_mail2 (yjhm, crawler_time) VALUES '
    sql = process_sql_str(ori_sql, no_record_list)
    #print(sql)
    # 执行sql语句
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)

def terminal_insert(terminal_list, connection):
    ori_sql = 'INSERT ignore INTO ori_terminal (terminal_code, terminal_type) VALUES (%s,%s)'
    #sql = process_sql_str(ori_sql, terminal_list)
    # print(sql)
    # 执行sql语句
    for each_row in terminal_list:
        try:
            with connection.cursor() as cursor:
                # 执行sql语句，插入记录
                cursor.execute(ori_sql, each_row)
            # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
            connection.commit()
        except Exception as ex:
            print(ex)

def select_danhao(connection):
    select_sql1 = 'select yjhm from generate_mail_no_1;'
    select_sql2 = 'select yjhm from no_record_mail;'
    select_sql3 = 'select distinct(yjhm) from mail_info;'
    select_sql4 = 'select distinct(yjhm) from mail_info_1;'
    select_sql5 = 'select distinct(yjhm) from mail_info_2;'
    select_sql6 = 'select distinct(yjhm) from mail_info_3;'
    select_sql7 = 'select distinct(yjhm) from mail_info_4;'
    select_sql8 = 'SELECT DISTINCT(yjhm) from no_record_mail2'
    select_sql9 = 'select distinct(yjhm) from mail_info_5;'
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
            cursor.execute(select_sql5)
            result5_list = [item['yjhm'] for item in cursor.fetchall()]  # 已抓过的有记录单号
            cursor.execute(select_sql6)
            result6_list = [item['yjhm'] for item in cursor.fetchall()]  # 已抓过的有记录单号
            cursor.execute(select_sql7)
            result7_list = [item['yjhm'] for item in cursor.fetchall()]  # 已抓过的有记录单号
            cursor.execute(select_sql8)
            result8_list = [item['yjhm'] for item in cursor.fetchall()]  # 已抓过的有记录单号
            cursor.execute(select_sql9)
            result9_list = [item['yjhm'] for item in cursor.fetchall()]  # 已抓过的有记录单号

            result_tmp1 = list(set(result1_list).difference(set(result2_list)))
            result_tmp2 = list(set(result_tmp1).difference(set(result3_list))) #相减后的单号
            result_tmp3 = list(set(result_tmp2).difference(set(result4_list)))
            result_tmp4 = list(set(result_tmp3).difference(set(result5_list)))
            result_tmp5 = list(set(result_tmp4).difference(set(result6_list)))
            result_tmp6 = list(set(result_tmp5).difference(set(result7_list)))
            result_tmp7 = list(set(result_tmp6).difference(set(result8_list)))
            result = list(set(result_tmp7).difference(set(result9_list)))
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)
    result = [str(item) for item in result]
    return sorted(result)
    #return result


def connection_close(connection):
    connection.close()