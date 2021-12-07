#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# SQLite3 database file has to be created beforehands

import sqlite3 as lite
import sys
import time
import psutil
from gpiozero import CPUTemperature

# connexion à la base de données
db_name = 'sensorsData.db'
table_name = 'Raspberry_data'
con = lite.connect(db_name)


def init_db(con):
    """fonction d'initialisation de la base de données

    Args:
        con (connexion sqlite3): connexion à la base de données
    """
    
    with con:
        cur = con.cursor() 
        if not len(cur.fetchall()) > 0:
            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
            cur.execute(f"CREATE TABLE {table_name} (timestamp DATETIME PRIMARY KEY, cpu NUMERIC, ram NUMERIC, temp NUMERIC)")


sampleFreq = 1 * 60 # fréquence d'échantillonnage


def getCPUtempdata():
    """renvoie la température du CPU

    Returns:
        float: température en degrés Celsius
    """
    cpu = CPUTemperature()
    temp = cpu.temperature

    if temp is not None:
        temp = round(temp, 1)
    return temp


def getCPUload():
    """renvoie la charge CPU

    Returns:
        float: pourcentage de charge
    """
    return psutil.cpu_percent()


def getRAMpercent():
    """renvoie la charge de la RAM

    Returns:
        float: pourcentage de charge
    """
    ram = psutil.virtual_memory() # renvoie un objet avec beaucoup d'attributs
    return ram[2]


def logData (ram, cpu, temp):
    """enregistre les valeurs mesurées dans la base de données.

    Args:
        ram (float): pourcentage de charge de la RAM
        cpu (float): pourcentage de charge du CPU
        temp (float): température en degrés Celsius du CPU
    """
    conn=lite.connect(db_name)
    curs=conn.cursor()
    curs.execute(f"INSERT INTO {table_name} values(datetime('now'), (?), (?), (?))", (ram, cpu, temp))
    conn.commit()
    conn.close()# main function

if __name__ == '__main__':
    init_db(con)
    print("Start logging")

    while True:
        ram = getRAMpercent()
        cpu = getCPUload()
        temp = getCPUtempdata()
        logData(ram, cpu, temp)
        time.sleep(sampleFreq) # ------------ Execute program