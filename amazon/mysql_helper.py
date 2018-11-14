# -*- coding: utf-8 -*-

import pymysql.cursors


def mysql_login():
    config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "tian1314",
        "db": "amazon",
        "charset": "utf8",
        "cursorclass": pymysql.cursors.DictCursor,
    }
    # Connect to the database
    connection = pymysql.connect(**config)
    return connection


def mail_format_dic2list(tracks_dict):
    tracks_list = []
    valid = "1"
    for every_yj in tracks_dict:
        for every_line in every_yj:
            line = []
            line.append(every_line["crawler_time"])
            line.append(every_line["yjhm"])
            line.append(every_line["status"])
            line.append(every_line["description"])
            line.append(every_line["do_city"])
            line.append(every_line["do_time"])
            line.append(valid)
            tracks_list.append(line)
    return tracks_list


def miss_mail_format_dic2list(miss_tracks_dict):
    miss_tracks_list = []
    retry = "0"
    for every_yj in miss_tracks_dict:
        line = []
        line.append(every_yj["crawler_time"])
        line.append(every_yj["yjhm"])
        line.append(every_yj["status"])
        line.append(retry)
        miss_tracks_list.append(line)
    return miss_tracks_list


def miss_mail_sql_generater(tracks_list):
    ori_sql = "INSERT INTO missing_mail (crawler_time, yjhm, status, retry) VALUES "
    line_sql = ""
    for line in tracks_list:
        line_sql = line_sql + "('" + ("', '").join(line) + "'),"
    sql = ori_sql + line_sql[:-1] + ";"
    return sql


def mail_sql_generater(tracks_list):
    ori_sql = (
        "INSERT INTO wuliu (crawler_time, yjhm, status, description, do_city, do_time, valid) VALUES "
    )
    line_sql = ""
    for line in tracks_list:
        line_sql = line_sql + "('" + ("', '").join(line) + "'),"
    sql = ori_sql + line_sql[:-1] + ";"
    return sql


def miss_mail_sql_insert(tracks_dict, connection):
    tracks_list = miss_mail_format_dic2list(tracks_dict)
    sql = miss_mail_sql_generater(tracks_list)
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


def mail_sql_insert(tracks_dict, connection):
    tracks_list = mail_format_dic2list(tracks_dict)
    sql = mail_sql_generater(tracks_list)
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


def select_id(connection):
    select_sql1 = "SELECT store_id FROM kitchen;"
    try:
        with connection.cursor() as cursor:
            cursor.execute(select_sql1)
            result1_list = [item["store_id"] for item in cursor.fetchall()]  # 所有商家ID
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception as ex:
        print(ex)

    return result1_list


def connection_close(connection):
    connection.close()
