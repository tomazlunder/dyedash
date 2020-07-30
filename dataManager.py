import sqlite3
from datetime import datetime
import plotly.express as px
from scrape_wiki import getBuyHistory
from scrape_wiki import getSellHistory
import json
from pandas import DataFrame
import datetime
from datetime import date

#Returns a list of kits that were never in BLC
def neverInBlc():
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT *
                      FROM Kit
                      WHERE Kit.id NOT IN (
                         SELECT Blc.id
                         FROM Blc)
                    ;""")
    a = cursor.fetchall()
    #print(a)

    array = []

    return

def ganttData():
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT Blc.id,Kit.name,Blc.date_from,Blc.date_to FROM Blc
                      LEFT JOIN Kit
                      ON Blc.id = Kit.id;
    """)
    history = cursor.fetchall()

    cursor.execute("""SELECT Curr.id, Kit.name, Curr.date_from
                      FROM Curr
                      LEFT JOIN Kit
                      ON Curr.id = Kit.id;
    """)
    current = cursor.fetchall()

    conn.close()

    listOfDicts = []

    today = datetime.datetime.today().strftime('%Y-%m-%d')
    for each in current:
        name = each[1]
        start = each[2]
        end = today

        element = dict(Task=name, Start=start, Finish=end, Resource=name)
        listOfDicts.append(element)

    for each in history:
        name = each[1]
        start = each[2]
        end = each[3]

        element = dict(Task=name, Start=start, Finish=end, Resource=name)
        listOfDicts.append(element)


    return listOfDicts
