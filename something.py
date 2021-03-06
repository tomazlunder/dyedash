import sqlite3
from datetime import datetime
import plotly.express as px
from scrape_wiki import getBuyHistory
from scrape_wiki import getSellHistory
import json
from pandas import DataFrame
import pandas
import datetime
from datetime import date

#TODO: FUNCITONS IN THIS FILE NEED TO BE MOVED, ONLY TEMP HERE

def goldFromInteger(a):
    #print(a)
    strmoney = "%08d"%a
    copper = strmoney[-2:]
    silver = strmoney[-4:-2]
    gold = strmoney[:-4]
    gold = int(gold)
    gold = str(gold)

    out = "%sg %ss %sc"%(gold,silver,copper)
    return out

def getInOrderOfLastAvailabe():
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    query = """SELECT Kit.id,Kit.name,sub.maxDateTo  FROM Kit LEFT JOIN (
        SELECT id,MAX(date_from) as maxDateFrom,MAX(date_to) as maxDateTo FROM Blc GROUP BY id ORDER BY maxDateTo DESC) as sub
        ON Kit.id = sub.id
        WHERE Kit.id NOT IN (SELECT Curr.id FROM Curr)
        ORDER BY sub.maxDateTo DESC"""
    #print(query)

    cursor.execute(query)
    df = DataFrame(cursor.fetchall())
    df.columns = ["id","name", "maxDateTo"]

    query = """SELECT Kit.id, Kit.name FROM Curr LEFT JOIN Kit ON Kit.id = Curr.id"""
    cursor.execute(query)
    df2 = DataFrame(cursor.fetchall())
    df2.columns = ["id","name"]

    today = date.today()
    maxDateTo = []
    for i in range(len(df2)):
        maxDateTo.append(str(today))
    df2.insert(2, "maxDateTo", maxDateTo, True)

    conn.close()
    return pandas.concat([df2,df])

def addKitTimeStats(df):
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    daySinceColumn = []
    lastTimeUnavailable = []

    today = date.today()
    for i in range(len(df)):
        # Days since
        str = df.iloc[i]["maxDateTo"]
        if (str is None):
            #daySinceColumn.append(999)
            daySinceColumn.append("NA")
            lastTimeUnavailable.append("NA")
            continue
        then = datetime.datetime.strptime(str, "%Y-%m-%d").date()
        delta = today - then
        daySinceColumn.append(delta.days)

        # Last time period unavailable

        #print(df.iloc[i]["id"])
        str = "SELECT date_from, date_to from Blc WHERE id=%s ORDER BY date_to DESC"%df.iloc[i]["id"]
        cursor.execute(str)
        a = cursor.fetchall()
        #print(a)

        if a is None or len(a) < 2:
            lastTimeUnavailable.append("NA")
        else:
            dateFromLast = a[0][0]
            dateToSecondLast = a[1][1]
            then = datetime.datetime.strptime(dateFromLast, "%Y-%m-%d").date()
            thenthen = datetime.datetime.strptime(dateToSecondLast, "%Y-%m-%d").date()
            delta = then - thenthen

            if delta.days == 0:
                if len(a) > 2:
                    dateFromLast = a[1][0]
                    dateToSecondLast = a[2][1]
                    then = datetime.datetime.strptime(dateFromLast, "%Y-%m-%d").date()
                    thenthen = datetime.datetime.strptime(dateToSecondLast, "%Y-%m-%d").date()
                    delta = then - thenthen
                    lastTimeUnavailable.append(delta.days)
                else:
                    lastTimeUnavailable.append("NA")
            else:
                lastTimeUnavailable.append(delta.days)

        #TODO: Mean time unavailable

    df.insert(3, "Days since", daySinceColumn, True)
    df.insert(4, "Last time away", lastTimeUnavailable, True)

    conn.close()
    return df



