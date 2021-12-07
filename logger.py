#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# SQLite3 database file has to be created beforehands

import sqlite3 as lite
import sys
import time
import psutil
from gpiozero import CPUTemperature


db_name = 'sensorsData.db'
table_name = 'Raspberry_data'
con = lite.connect(db_name)


def init_db(con):
    
    with con:
        cur = con.cursor() 
        if not len(cur.fetchall()) > 0:
            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
            cur.execute(f"CREATE TABLE {table_name} (timestamp DATETIME PRIMARY KEY, cpu NUMERIC, ram NUMERIC, temp NUMERIC)")


sampleFreq = 1 * 60 # time in seconds ==> Sample each 5 min


def getCPUtempdata():	
    cpu = CPUTemperature()
    temp = cpu.temperature

    if temp is not None:
        temp = round(temp, 1)
    return temp # log sensor data on database


def getCPUload():
    # gives a single float value
    return psutil.cpu_percent()


def getRAMpercent():
    # gives an object with many fields
    ram = psutil.virtual_memory() 
    return ram[2]


def logData (ram, cpu, temp):
    conn=lite.connect(db_name)
    curs=conn.cursor()
    curs.execute(f"INSERT INTO {table_name} values(datetime('now'), (?), (?), (?))", (ram, cpu, temp))
    conn.commit()
    conn.close()# main function

if __name__ == '__main__':
    init_db(con)

    while True:
        ram = getRAMpercent()
        cpu = getCPUload()
        temp = getCPUtempdata()
        logData(ram, cpu, temp)
        time.sleep(sampleFreq) # ------------ Execute program