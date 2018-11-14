import python.baidu_getpoint.mysql_helper as mysql_helper
connection = mysql_helper.mysql_login()
mysql_helper.delete_the_record(210000222703,connection)
connection.close()
# import easygui
# easygui.msgbox("获取周边信息第1个程序完成！")