import urllib.request
import urllib.error
import re
import sqlite3
import json
import pandas as pd

def check_api_key(key):
    url = "https://api.guildwars2.com/v2/characters?access_token=%s"%key

    try:
        f = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        return 0
    myfile = f.read().decode('utf-8')

    matches = re.findall("Invalid access token", myfile)
    if len(matches):
        return 0

    return 1


def api_get_prices(ids):
    url = "https://api.guildwars2.com/v2/commerce/prices?ids="
    for each in ids:
        url = url + str(each) + ","
    print(url)

    f = urllib.request.urlopen(url)
    myfile = f.read().decode('utf-8')
    priceJSON = json.loads(myfile)

    return priceJSON

def findOwnedDyes(token):
    if token is None:
        return

    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    query = "SELECT realId,kitID FROM Dye"
    cursor.execute(query)
    a = cursor.fetchall()

    numOf = dict()
    kitDict = dict()
    for each in a:
        realId = each[0]
        numOf[realId] = 0
        kitDict[realId] = each[1]

    #print(numOf)

    #Get bank
    url = "https://api.guildwars2.com/v2/account/bank?access_token=%s"%token

    f = urllib.request.urlopen(url)
    myfile = f.read().decode('utf-8')

    #print("bla")

    if(len(myfile) < 200):
        print(myfile)

    jsonBank = json.loads(myfile)


    for each in jsonBank:
        #print(each)
        if(each is None):
            continue
        if(each["id"] in numOf):
            numOf[each["id"]] = numOf[each["id"]]+each["count"]

    #TODO: Character inventories

    #print(numOf)
    #Get prices for owned dyes
    ownedOnly = {key:val for key,val in numOf.items() if val != 0}
    ownedIDs = list(ownedOnly.keys())

    priceJSON = api_get_prices(ownedIDs)

    numOwned = []
    sellPrices = []
    buyPrices = []
    kitIds = []

    #print(ownedIDs)
    #print(priceJSON)

    i = 0
    for each in ownedIDs:
        numOwned.append(ownedOnly[each])
        itemData = priceJSON[i]

        buyPrice = itemData["buys"]
        buyPrice = buyPrice["unit_price"]

        sellPrice = itemData["sells"]
        sellPrice = sellPrice["unit_price"]

        sellPrices.append(sellPrice)
        buyPrices.append(buyPrice)

        kitIds.append(kitDict[each])

        i+=1


    #REALID, NUMBER, SELL, BUY

    d = {'realId':ownedIDs,'kitId':kitIds,'num':numOwned,'sell':sellPrices,'buy':buyPrices}
    df = pd.DataFrame(data=d)

    conn.close()
    return df