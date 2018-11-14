# -*- coding: utf-8 -*-

import random

# print(random.randint(0, 15))
proxy_list = ["178.62.171.190:43407", "117.135.132.107:3000"]


class Proxy:

    def getProxy(self):
        LOCAL_PROXY = "39.155.160.162"

        longth = len(proxy_list)
        if proxy_list == []:
            return LOCAL_PROXY
        rnum = random.randint(0, longth - 1)
        tproxy = proxy_list[rnum]
        del proxy_list[rnum]
        print(tproxy)
        return tproxy
