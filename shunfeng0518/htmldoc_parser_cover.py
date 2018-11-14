# -*- coding: utf-8 -*-

import os,codecs
import html_parser2
import mysql_helper_for_parser

BASE_DIR = os.path.dirname(__file__)
data_dir = os.path.join(BASE_DIR, 'Data\\htmldoc1')

connection = mysql_helper_for_parser.mysql_login()
files = os.listdir(data_dir)
for index in range(len(files)):
    file_path = os.path.join(data_dir, files[index])
    with codecs.open(file_path, 'r', 'utf-8') as f:
        htmldoc = f.read()
        if htmldoc == '':
            continue
        time = files[index].split('.')[0]
        wuliu_info_list, no_record_list, danhao_info_list, terminal_list = html_parser2.parse_page(htmldoc, time)
        if len(wuliu_info_list) > 0:
            mysql_helper_for_parser.mail_wuliu_insert(wuliu_info_list, connection)
        if len(terminal_list) > 0:
            mysql_helper_for_parser.terminal_insert(terminal_list, connection)
    print(str(index) + ' OK')

mysql_helper_for_parser.connection_close(connection)