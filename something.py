import sqlite3
from datetime import datetime
import plotly.express as px
from scrape_wiki import getBuyHistory
from scrape_wiki import getSellHistory
import json
from pandas import DataFrame
import datetime
from datetime import date

def drawGantt():
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()
    currentDate = datetime.datetime.today().strftime('%Y-%m-%d')

    cursor.execute("SELECT MAX (date_to) AS \"md\" FROM Blc")
    a = cursor.fetchone()
    currentKitStartDate = a[0]

    cursor.execute("SELECT * FROM Kit")
    a = cursor.fetchall()
    #print(a)

    df = []

    for each in a:
        #print(each)
        id = each[0]
        name = each[1]

        cursor.execute("SELECT * FROM Blc WHERE id =%s"%id)
        b = cursor.fetchall()
        for every in b:
            start = every[1]
            end = every[2]

            dic = dict(Task=name, Start=start, Finish=end, Resource=name)
            df.append(dic)

        cursor.execute("SELECT * FROM Curr WHERE id =%s"%id)
        b = cursor.fetchall()

        for every in b:
            start = currentKitStartDate
            end = currentDate
            dic = dict(Task=name, Start=start, Finish=end, Resource=name)
            #print(dic)
            df.append(dic)

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Resource")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height = 700)

    conn.close()
    return fig

def goldFromInteger(a):
    strmoney = "%08d"%a
    copper = strmoney[-2:]
    silver = strmoney[-4:-2]
    gold = strmoney[:-4]
    gold = int(gold)
    gold = str(gold)

    out = "%sg %ss %sc"%(gold,silver,copper)
    return out



def drawPriceChart(id):
    buyDataFile = getBuyHistory(id)
    sellDataFile = getSellHistory(id)

    buyJSON = json.loads(buyDataFile)
    buyRes = buyJSON["results"]

    sellJSON = json.loads(sellDataFile)
    sellRes = sellJSON["results"]

    print(buyRes)
    fig = px.line(buyRes, x='listing_datetime', y='unit_price')
    fig.update_xaxes(rangeslider_visible=True)

    return fig

def test():
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Kit")
    a = cursor.fetchall()
    print(a)

    cursor.execute("SELECT * FROM Blc WHERE id = 6")
    a = cursor.fetchall()
    print(a)

    conn.close()

def getInOrderOfLastAvailabe():
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    str = """SELECT Kit.id,Kit.name,sub.maxDateTo  FROM Kit LEFT JOIN (
        SELECT id,MAX(date_from) as maxDateFrom,MAX(date_to) as maxDateTo FROM Blc GROUP BY id ORDER BY maxDateTo DESC) as sub
        ON Kit.id = sub.id
        WHERE Kit.id NOT IN (SELECT Curr.id FROM Curr)
        ORDER BY sub.maxDateTo DESC"""
    print(str)

    cursor.execute(str)
    df = DataFrame(cursor.fetchall())
    df.columns = ["id","name", "maxDateTo"]

    conn.close()
    return df

def addStats(df):
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    daySinceColumn = []
    lastTimeUnavailable = []

    today = date.today()
    for i in range(len(df)):
        # Days since
        str = df.iloc[i]["maxDateTo"]
        if (str is None):
            daySinceColumn.append(999)
            lastTimeUnavailable.append("NA")
            continue
        then = datetime.datetime.strptime(str, "%Y-%m-%d").date()
        delta = today - then
        daySinceColumn.append(delta.days)

        # Last time period unavailable

        print(df.iloc[i]["id"])
        str = "SELECT date_from, date_to from Blc WHERE id=%s ORDER BY date_to DESC"%df.iloc[i]["id"]
        cursor.execute(str)
        a = cursor.fetchall()
        print(a)

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

        # Mean time unavailable

    print(lastTimeUnavailable)

    df.insert(3, "Days since", daySinceColumn, True)
    df.insert(4, "Last time away", lastTimeUnavailable, True)


    conn.close()
    return df



