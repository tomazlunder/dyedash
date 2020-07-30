import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
import importlib
import sqlite3
import dash_bootstrap_components as dbc
import json
import urllib.request

from something import goldFromInteger


from something import getInOrderOfLastAvailabe
from dataManager import ganttData

def createGantt():
    df = ganttData()
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Resource")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height = 700)

    return fig

def createKitPanel():
    data = getInOrderOfLastAvailabe()

    #print(data)

    title = ['Hi Dash', 'Hello World']
    link = [html.A(html.P('Link'), href="yahoo.com"), html.A(html.P('Link'), href="google.com")]

    dictionary = {"title": title, "link": link}
    df = pd.DataFrame(dictionary)
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


    return

def createDyePanel(id):
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    query = "SELECT name,realId,color1,color2,color3 FROM Dye WHERE kitId = %s"%id
    cursor.execute(query)
    a = cursor.fetchall()

    #print(a)

    text = "https://api.guildwars2.com/v2/commerce/prices?ids="
    for each in a:
        realId = each[1]
        text = text + str(realId) + ","
    print(text)

    f = urllib.request.urlopen(text)
    myfile = f.read().decode('utf-8')
    buyJSON = json.loads(myfile)


    elements = []
    i = 0
    for each in a:
        subElements = []

        name = each[0]
        realId = each[1]
        color1 = each[2]
        color2 = each[3]
        color3 = each[4]

        itemData = buyJSON[i]
        #print(itemData)
        buyPrice = itemData["buys"]
        #print(buyPrice)
        buyPrice = buyPrice["unit_price"]
        #print(buyPrice)

        sellPrice = itemData["sells"]
        sellPrice = sellPrice["unit_price"]

        subElements.append(html.Td(html.Label(name)))

        #RealId
        #subElements.append(html.Td(html.Label(realId)))

        subElements.append(html.Td(html.A("Spidy", href="https://www.gw2spidy.com/item/%s"%realId)))
        subElements.append(html.Td(html.A("GW2TP", href="https://www.gw2tp.com/item/%s"%realId)))

        print(color1)
        subElements.append(html.Td(html.P(html.Label(),style={'background-color': "#%s"%color1, 'width':22, 'height':22,'border-width':1,'border-style':'solid', 'border-color':'black'})))
        subElements.append(html.Td(html.P(html.Label(),style={'background-color': "#%s"%color2, 'width':22, 'height':22,'border-width':1,'border-style':'solid', 'border-color':'black'})))
        subElements.append(html.Td(html.P(html.Label(),style={'background-color': "#%s"%color3, 'width':22, 'height':22,'border-width':1,'border-style':'solid', 'border-color':'black'})))

        subElements.append(html.Td(html.P(goldFromInteger(buyPrice))))
        subElements.append(html.Td(html.P(goldFromInteger(sellPrice))))



        elements.append(html.Tr(subElements,style={'font-size':13}))
        i+=1

    conn.close()
    return dbc.Table(elements, id="panel")