import urllib.request
import re
import sqlite3
import time

historicalURLs = ["https://wiki.guildwars2.com/wiki/Black_Lion_Chest/historical",
        "https://wiki.guildwars2.com/wiki/Black_Lion_Chest/historical_3",
        "https://wiki.guildwars2.com/wiki/Black_Lion_Chest/historical_2"]

#Historical 1 is before chest rework, no good info anyway
#  "https://wiki.guildwars2.com/wiki/Black_Lion_Chest/historical_1"

currentURL = "https://wiki.guildwars2.com/wiki/Black_Lion_Chest"

dyesURL = "https://wiki.guildwars2.com/wiki/Dye"

def get_kits3():
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    f = urllib.request.urlopen("https://wiki.guildwars2.com/wiki/Dye")
    myfile = f.read().decode('utf-8')

    start = "promo expandable craftvariants table"
    end = "</table>"

    tableString = myfile[myfile.find(start)+len(start):myfile.rfind(end)]
    #print(tableString)
    #print("***")

    kitFields = tableString.split("<tr>\n<th>")
    foundKits = []

    i=0
    for kitField in kitFields[1:]:
        #print("***")
        #print(kitField)
        tdSplit = kitField.split("<td>")

        #Name
        nameTd = tdSplit[2]
        #print("**")
        #print(nameTd)
        nameMatch = re.findall(">[A-Za-z -\']+</a>", nameTd)
        if(len(nameMatch) == 0):
            continue
        kitName = nameMatch[0][1:-4]

        #print("*")
        #print(kitName)

        if(kitName in foundKits):
            continue

        foundKits.append(kitName)
        str = "INSERT OR IGNORE INTO Kit VALUES (\"%s\",\"%s\")" % (i, kitName)
        print(str)
        cursor.execute(str)
        conn.commit()

        #Dyes
        dyeFields = tdSplit[1].split("<dd>")

        j = 0
        for dyeField in dyeFields[1:]:
            dyeNameMatch = re.findall(">[A-Za-z -\']+</a>", dyeField)
            if(len(dyeNameMatch) == 0): continue
            dyeName = dyeNameMatch[0][1:-4]

            str = "INSERT OR IGNORE INTO Dye VALUES (\"%s\",\"%s\",\"%s\", null,null,null,null)" % (i, j, dyeName)
            print(str)
            cursor.execute(str)
            conn.commit()
            j+=1

        i+=1

    conn.close()
    print("Kits and dyes have been scraped.")
    return

def scrape_current():
    print("Scraping current chest data... : %s"%currentURL)

    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    f = urllib.request.urlopen(currentURL)
    myfile = f.read().decode('utf-8')

    matches = re.findall("[A-Za-z]+ Dye Kit", myfile)
    #print(matches)

    cursor.execute("SELECT MAX (date_to) AS \"md\" FROM Blc")
    a = cursor.fetchone()
    currentKitStartDate = a[0]

    unique = []
    for match in matches:
        if match not in unique:
            unique.append(match)

    #print(unique)

    for dyeKitName in unique:
        str = "SELECT id FROM Kit WHERE name = \"%s\";" % (dyeKitName)
        # print(str)
        cursor.execute(str)
        id = cursor.fetchone()
        # print("id:%s" % id[0])

        str = "INSERT OR IGNORE INTO Curr VALUES (%s, \'%s\')" % (id[0], currentKitStartDate)
        print(str)
        cursor.execute(str)
        conn.commit()

    conn.close()
    print("Scraped current chest data.")
    return

def scrape_historic():
    print("Scraping historic chest data...")
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    i = 0
    for url in historicalURLs:
        print("CURRENTLY SCRAPING [%s/%s]: %s"%(i+1,len(historicalURLs),url))
        i+=1
        f = urllib.request.urlopen(url)
        myfile = f.read().decode('utf-8')

        h2split = myfile.split("<h2><span")

        dyeKitName = 0
        startDate = 0
        endDate = 0

        for each in h2split[1:]:
            #print(each)

            matches = re.findall("[\'A-Za-z \-]+ Chest", each)

            if (len(matches) > 0):
                print(matches[0])
            else:
                continue

            datesRaw = re.findall("<ul><li>20[A-Za-z0-9 \-]+ to [A-Za-z0-9 \-]+</li></ul>", each)
            #print(datesRaw)

            if(len(datesRaw) == 0):
                continue

            matches2 = re.findall("[0-9]+[ -][0-9]+[ -][0-9]+", datesRaw[0])
            #print(" %s"%matches2)

            startDate = matches2[0]
            endDate = matches2[1]

            #EU DATES
            #startDate = startDate[8:10] + " " + startDate[5:7] + " " + startDate[0:4]
            #endDate = endDate[8:10] + " " + endDate[5:7] + " " + endDate[0:4]

            #US Formatting
            startDate = startDate[0:4] + "-" + startDate[5:7] + "-" + startDate[8:10]
            endDate = endDate[0:4] + "-" + endDate[5:7] + "-" + endDate[8:10]

            matchesKits = re.findall(">[A-Za-z -\']+ Dye Kit",each)
            for kit in matchesKits:
                dyeKitName = kit[1:]
                #print(" "+dyeKitName)

                str = "SELECT id FROM Kit WHERE name = \"%s\";" % (dyeKitName)
                #print(str)
                cursor.execute(str)
                id = cursor.fetchone()
                #print("id:%s" % id[0])

                if(id[0] == None):
                    continue

                str = "INSERT OR IGNORE INTO Blc VALUES (%s, \'%s\', \'%s\')" % (id[0], startDate, endDate)
                print(str)
                cursor.execute(str)
                conn.commit()


        time.sleep(2) #To avoid DOS prevention

    conn.close()
    print("Scraped historic chest data.")
    return

#unused
def idFromName2(itemName):
    formatedName = itemName.replace(" ", "_")
    url = "https://wiki.guildwars2.com/wiki/%s"%formatedName

    f = urllib.request.urlopen(url)
    myfile = f.read().decode('utf-8')

    matches = re.findall("href=\"https://www.gw2spidy.com/item/[0-9]+",myfile)
    if(len(matches) == 0): return -1

    match = matches[0]
    matches = re.findall("[0-9][0-9][0-9]+", match)

    if(len(matches) == 0): return -1

    id = matches[0]

    return id

def dyeScraper(itemName):
    formatedName = itemName.replace(" ", "_")
    url = "https://wiki.guildwars2.com/wiki/%s"%formatedName

    f = urllib.request.urlopen(url)
    myfile = f.read().decode('utf-8')

    matches = re.findall("href=\"https://www.gw2spidy.com/item/[0-9]+",myfile)
    if(len(matches) == 0): return -1

    match = matches[0]
    matches = re.findall("[0-9][0-9][0-9]+", match)

    if(len(matches) == 0): return -1

    id = matches[0]
    #Colors
    matches = re.findall("Cloth: [A-Za-z0-9]+\"", myfile)
    c1 = matches[0]
    print(c1)
    c1 = c1[7:-1]

    matches = re.findall("Leather: [A-Za-z0-9]+\"",myfile)
    c2 = matches[0]
    c2 = c2[9:-1]

    matches = re.findall("Metal: [A-Za-z0-9]+\"",myfile)
    c3 = matches[0]
    c3 = c3[7:-1]

    return [id,c1,c2,c3]

def scrape_dye_info():
    conn = sqlite3.connect('dyes.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM Dye")
    a = cursor.fetchall()

    for each in a:
        dyeInfo = dyeScraper(each[0])
        id = dyeInfo[0]
        c1 = dyeInfo[1]
        c2 = dyeInfo[2]
        c3 = dyeInfo[3]

        if(id == -1): continue

        str = "UPDATE Dye SET realID = \"%s\", color1 = \"%s\", color2 = \"%s\", color3 = \"%s\" WHERE name = \"%s\""%(id,c1,c2,c3,each[0])
        print(str)
        cursor.execute(str)
        conn.commit()

        time.sleep(0.5)

    print("Scrapped additional dye info from wiki.")
    conn.close()
    return

#TODO: Multiple pages
def getSellHistory(id):
    url = "http://www.gw2spidy.com/api/v0.9/json/listings/%s/sell/1"%id

    f = urllib.request.urlopen(url)
    myfile = f.read().decode('utf-8')
    return myfile


def getBuyHistory(id):
    url = "http://www.gw2spidy.com/api/v0.9/json/listings/%s/sell/1"%id

    f = urllib.request.urlopen(url)
    myfile = f.read().decode('utf-8')
    return myfile

#get_kits3()
#scrape_historic()
#scrape_current()
#scrape_dye_info()
