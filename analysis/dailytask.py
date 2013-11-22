#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import datetime

from HiveInterface import HiveInterface
from HbaseInterface import HbaseInterface


HOST = "hadoopmaster"
ONE_DAY = datetime.timedelta(days=1)

hiveinterface = HiveInterface(HOST)
hiveinterface.execute("select count(distinct sn), device from daily_logs where d <= 20131121 group by device");
class DailyTask:
    def __init__(self, day):
        self.day = day
        self.day_str = day.strftime("%Y%m%d")
    
    # 累计用户数
    def _a(self):
        sql = """select count(distinct sn), device from daily_logs where d <= %s group by device""" % self.day_str
        print sql
        res = hiveinterface.execute(sql)

        print res

    # 新增用户数
    def _b(self):
        print "_b"
    
    # 活跃用户数
    def _c(self):
        print "_c"

    # VOD用户数
    def _d(self):
        pass

    # VOD播放次数
    def _e(self):
        pass

    # VOD户均时长
    def _f(self):
        pass

    # VOD激活率
    def _g(self):
        pass

    # 开机率
    def _h(self):
        pass

    # 应用激活率
    def _i(self):
        pass

    # 智能激活率
    def _j(self):
        pass

    def execute(self):
        self._a()
        self._b()
        self._c()
        self._d()
        self._e()
        self._f()
        self._g()
        self._h()
        self._i()
        self._j()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        daylist = [datetime.datetime.now() - datetime.timedelta(days=1)]
    elif len(sys.argv) == 2:
        daylist = [datetime.datetime.strptime(sys.argv[1], "%Y%m%d")]
    else:
        startday = datetime.datetime.strptime(sys.argv[1], "%Y%m%d")
        endday = datetime.datetime.strptime(sys.argv[2], "%Y%m%d")
        daylist = []
        while startday <= endday:
            daylist.append(startday)
            startday = startday + ONE_DAY
    
    for day in daylist:
        task = DailyTask(day)
        task.execute()
                                           
