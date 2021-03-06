#!/usr/bin/python
# -*- coding: utf-8 -*- 
import sys

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from hbase import Hbase
from hbase.ttypes import *

class NotFoundTable(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class HbaseInterface:
    def __init__(self, address, port, table):
        self.tableName = table
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(address, port))
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Hbase.Client(self.protocol)
        self.transport.open()
        tables = self.client.getTableNames()
        if self.tableName not in tables:
            raise NotFoundTable(self.tableName)
            
    def __del__(self):
        self.transport.close()

    def write(self, key, d):
        mutations = []
        for k,v in d.iteritems():
            mutations.append(Mutation(column=k, value=v))
        self.client.mutateRow(self.tableName, key, mutations, {})


    def read(self, key, columns):
        scannerId = self.client.scannerOpenWithPrefix(self.tableName, key, columns, None)
        rowlist = self.client.scannerGet(scannerId)
        self.client.scannerClose(scannerId)
        if len(rowlist) >= 1:
            return rowlist[0]
        return None
    
    def read_all(self, prefix, columns):
        scannerId = self.client.scannerOpenWithPrefix(self.tableName, prefix, columns, None)
        rowlist = self.client.scannerGetList(scannerId, 100000)
        self.client.scannerClose(scannerId)
        return rowlist

HBASEHOST = "hadoopns410"
def get_sn_pos(day):
    client = HbaseInterface(HBASEHOST, "9090", "sn_table")    
    colkeys = ["a:device", "a:province", "a:city"]
    rowlist = client.read_all(day, colkeys)

    res = []
    for r in rowlist:
        day_sn = r.row
        cols = r.columns
        t = {}
        t["day"] = day_sn[0:8]
        t["sn"] = day_sn[9:]
        try:
            t["device"] = cols["a:device"].value
        except:
            t["device"] = "-"
        try:
            t["province"] = cols["a:province"].value
        except:
            t["device"] = "-"
        try:
            t["city"] = cols["a:city"].value
        except:
            t["city"] = "-"
        res.append(t)
    return res

if __name__ == "__main__":
    key = "20140102"
    if len(sys.argv) == 2:
        key = sys.argv[1]
    res = get_sn_pos(key)
    for t in res:
        print t


