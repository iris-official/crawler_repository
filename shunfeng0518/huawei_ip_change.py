# -*- coding: utf-8 -*-1

# @Usage: 重启华为无线网卡，其他网卡应修改程序
# 电脑对此网卡的设置为自动连接，对其他无线网均为不自动连接

import time

def reboot_service(driver):
    try:
        driver.get('http://192.168.0.1')
        driver.find_element_by_id('menu_settings').click()
        driver.find_element_by_id('username').send_keys('admin')
        driver.find_element_by_id('password').send_keys('admin')
        driver.find_element_by_id('pop_login').click()
        time.sleep(0.1)
        driver.find_element_by_id('label_system').click()
        driver.find_element_by_id('label_reboot').click()
        driver.find_element_by_id('undefined').click()
        driver.find_element_by_id('pop_confirm').click()
        print('HUAWEI Reboot OK!!!')
        time.sleep(30)
        return True
    except Exception as ex:
        print('Reboot ERROR!!!', ex)

