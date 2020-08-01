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
import math
import datetime

from pandas import DataFrame


from something import goldFromInteger


from something import getInOrderOfLastAvailabe
from dataManager import ganttData

from api_calls import api_get_prices
from api_calls import findOwnedDyes

from something import addStats

import base64

image_gold = 'assets/img/coin_gold.png' # replace with your own image
encoded_image_gold = base64.b64encode(open(image_gold, 'rb').read())

def createTable(df,_id):
    tab  = dash_table.DataTable(
        id=_id,
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_as_list_view=True,
        row_selectable='single',
        css=[{'selector': '.row', 'rule': 'margin: 0'}],
        style_table={'table - layout': 'fixed'}
    )

    return tab

def createGantt():
    df = ganttData()
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Resource")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height = 700)

    return fig

def createPersonalKitPanel(apiKey):
    print("Creating personal kit panel...")

    #Getting owned dyes and price info
    dfOwned = findOwnedDyes(apiKey)

    data = getInOrderOfLastAvailabe()
    data = addStats(data)

    #Getting numDyes, totalSell, totalBuy for every kit
    dfOwned["sellMul"] = dfOwned["sell"] * dfOwned["num"]
    dfOwned["buyMul"] = dfOwned["buy"] * dfOwned["num"]

    #Grouping by kit ID
    groupedDf = dfOwned.groupby(['kitId']).sum()
    groupedDf = groupedDf.drop(columns=['realId', 'sell', 'buy'])
    groupedDf.columns = ['num','sell','buy']
    groupedDf['id'] = groupedDf.index #The grouped by column becomes special, making it normal

    #For debugging (TODO: Remove)
    pd.set_option('display.max_columns', 10)
    pd.options.display.float_format = '{:,.0f}'.format

    #Merging with data
    mergedDf = pd.merge(data, groupedDf, on='id', how='outer')

    mergedDf['sellGold'] = [goldFromInteger(int(x)) if not math.isnan(x) else goldFromInteger(0) for x in mergedDf['sell']]
    mergedDf['buyGold'] = [goldFromInteger(int(x)) if not math.isnan(x) else goldFromInteger(0) for x in mergedDf['buy']]

    mergedDf = mergedDf[['name','maxDateTo','Days since', 'Last time away','num','sellGold','buyGold']]

    #Changing available dyes (today date to AVAILABLE)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    mergedDf.loc[mergedDf.maxDateTo == today, "maxDateTo"] = "AVAILABLE"

    #Renaming columns
    mergedDf.columns = ['Kit name', 'Last sale end', 'Days since', 'Last time away', 'NumOwned', 'Sell value', 'Buy value']

    return createTable(mergedDf, 'personalKitTable')

def createDyePanel(id):
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    query = "SELECT name,realId,color1,color2,color3 FROM Dye WHERE kitId = %s"%id
    cursor.execute(query)
    a = cursor.fetchall()

    ids = []
    for each in a:
        realId = each[1]
        ids.append(realId)

    priceJSON = api_get_prices(ids)

    elements = []
    elements.append(html.Tr([html.Th("Name"),html.Th("SPIDY"),html.Th("GW2TP"),html.Th("CC"),
                             html.Th("CL"),html.Th("CM"),html.Th("Sell/Buy price")]))
    i = 0
    for each in a:
        subElements = []

        name = each[0]
        realId = each[1]
        color1 = each[2]
        color2 = each[3]
        color3 = each[4]

        itemData = priceJSON[i]

        buyPrice = itemData["buys"]
        buyPrice = buyPrice["unit_price"]
        sellPrice = itemData["sells"]
        sellPrice = sellPrice["unit_price"]

        subElements.append(html.Td(html.Label(name)))

        subElements.append(html.Td(html.A("Spidy", href="https://www.gw2spidy.com/item/%s"%realId)))
        subElements.append(html.Td(html.A("GW2TP", href="https://www.gw2tp.com/item/%s"%realId)))

        subElements.append(html.Td(html.P(html.Label(),style={'background-color': "#%s"%color1, 'width':22, 'height':22,'border-width':1,'border-style':'solid', 'border-color':'black'})))
        subElements.append(html.Td(html.P(html.Label(),style={'background-color': "#%s"%color2, 'width':22, 'height':22,'border-width':1,'border-style':'solid', 'border-color':'black'})))
        subElements.append(html.Td(html.P(html.Label(),style={'background-color': "#%s"%color3, 'width':22, 'height':22,'border-width':1,'border-style':'solid', 'border-color':'black'})))

        subElements.append(html.Td([html.Div(goldFromInteger(sellPrice)),html.Br(),html.Div(goldFromInteger(buyPrice))]))

        elements.append(html.Tr(subElements,style={'font-size':13}))
        i+=1

    conn.close()
    return dbc.Table(elements, id="panel", style={'font-size':14})


def createPersonalDyePanel(kitId, apiKey):
    dfOwned2 = findOwnedDyes(apiKey)

    dfOwned2["sellMul"] = dfOwned2["sell"] * dfOwned2["num"]
    dfOwned2["buyMul"] = dfOwned2["buy"] * dfOwned2["num"]
    #print(dfOwned2)

    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    query = "SELECT name,realId,color1,color2,color3 FROM Dye WHERE kitId = %s" % kitId
    cursor.execute(query)
    a = cursor.fetchall()
    dyesDf = DataFrame(a)

    dyesDf.columns = ['name', 'realId','color1','color2','color3']


    #print(dyesDf)

    b = pd.merge(dyesDf, dfOwned2, on='realId', how='left')
    #print(b)

    idsList = b['realId'].tolist()
    priceJSON = api_get_prices(idsList)

    elements = []
    elements.append(html.Tr([html.Th("Name"), html.Th("SPIDY"), html.Th("GW2TP"), html.Th("CC"),
                            html.Th("Sell/Buy"),html.Th("Owned"),html.Th("Total Sell/Buy")]))

    i = 0
    for each in range(len(b)):
        subElements =[]

        name =  b.iloc[i]['name']
        realId = b.iloc[i]['realId']
        color1 = b.iloc[i]['color1']
        color2 = b.iloc[i]['color2']
        color3 = b.iloc[i]['color3']

        numOwned = b.iloc[i]['num']
        sellPrice = b.iloc[i]['sell']
        buyPrice = b.iloc[i]['buy']
        totalSell = b.iloc[i]['sellMul']
        totalBuy = b.iloc[i]['buyMul']

        if(math.isnan(numOwned)):
            numOwned = 0
        if(math.isnan(sellPrice)):
            sellPrice = 0
            sellPrice = priceJSON[i]['sells']['unit_price']
        if(math.isnan(buyPrice)):
            buyPrice = 0
            buyPrice = priceJSON[i]['buys']['unit_price']
        if(math.isnan(totalSell)):
            totalSell = 0
        if(math.isnan(totalBuy)):
            totalBuy = 0

        subElements.append(html.Td(html.Label(name)))

        subElements.append(html.Td(html.A("Spidy", href="https://www.gw2spidy.com/item/%s" % realId)))
        subElements.append(html.Td(html.A("GW2TP", href="https://www.gw2tp.com/item/%s" % realId)))

        """
        subElements.append(html.Td(html.P(html.Label(),
                                          style={'background-color': "#%s" % color1, 'width': 22, 'height': 22,
                                                 'border-width': 1, 'border-style': 'solid', 'border-color': 'black'})))
        """

        subElements.append(html.Td(html.Span([html.Div([],
                                                    style={'background-color': "#%s" % color1, 'width': 22, 'height': 22,
                                                    'border-width': 1, 'border-style': 'solid', 'border-color': 'black'}),
                                            html.Div([],
                                                style={'background-color': "#%s" % color2, 'width': 22, 'height': 22,
                                                       'border-width': 1, 'border-style': 'solid', 'border-color': 'black'}),
                                            html.Div([],
                                                style={'background-color': "#%s" % color3, 'width': 22, 'height': 22,
                                                       'border-width': 1, 'border-style': 'solid', 'border-color': 'black'}),
                                            ])))

        subElements.append(html.Td([html.Div(goldFromInteger(sellPrice)),html.Br(),html.Div(goldFromInteger(buyPrice))]))

        subElements.append(html.Td(html.Label(numOwned)))

        subElements.append(html.Td([html.Div(goldFromInteger(totalSell)),html.Br(),html.Div(goldFromInteger(totalBuy))]))

        elements.append(html.Tr(subElements, style={'font-size': 13}))
        i+=1

    return dbc.Table(elements,id="personal-dye-panel")

