#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import datetime

from decorators import timed
from HiveInterface import HiveInterface
from HbaseInterface import HbaseInterface

HIVEHOST = "hadoopsnn411"
HBASEHOST = "hadoopns410"
ONE_DAY = datetime.timedelta(days=1)

class MonthlyTask:
    hiveinterface = HiveInterface(HIVEHOST)    
    hbaseinterface = HbaseInterface(HBASEHOST, "9090","monthly_channel")

    # 自然月
    def __init__(self, day):
        self.day = day
        if self.day.day != 1:
            raise Exception("MonthlyTask must be executed at 1th of month...")
        self.endday = self.day - ONE_DAY
        self.startday = self.endday.replace(day=1)
        self.startday_str = self.startday.strftime("%Y%m%d")
        self.endday_str = self.endday.strftime("%Y%m%d")
        self.month_str = self.startday.strftime("%Y%m")

    # VOD用户数
    @timed
    def _a(self):
        sql = """select count(distinct sn), device, channel
                 from daily_logs where parsets >= "%s" and parsets <= "%s"
                 and event in ("video_start", "video_play_load", "video_play_start", "video_exit")
                 group by device, channel
              """ % (self.startday_str, self.endday_str)
        res = MonthlyTask.hiveinterface.execute(sql)
        for li in res:
            value, device, channel = li.split()
            key = self.month_str + device + channel
            MonthlyTask.hbaseinterface.write(key, {"a:a": value})

    # 播放量
    @timed
    def _b(self):
        sql = """select count(*), device, channel
                 from daily_logs where parsets >= "%s" and parsets <= "%s" 
                 and event = "video_start"
                 group by device, channel
              """ % (self.startday_str, self.endday_str)
        res = MonthlyTask.hiveinterface.execute(sql)
        if not res:
            res = []
        for li in res:
            value, device, channel = li.split()
            key = self.month_str + device + channel
            MonthlyTask.hbaseinterface.write(key, {"a:b": value})

    def execute(self):
        self._a()
        self._b()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        daylist = [datetime.datetime.now()]
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
        task = MonthlyTask(day)
        task.execute()
                                           
