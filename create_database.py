import sqlite3

conn = sqlite3.connect('dyes.db')
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS Blc")
conn.commit()

cursor.execute("DROP TABLE IF EXISTS Kit")
conn.commit()

cursor.execute("DROP TABLE IF EXISTS Curr")
conn.commit()

cursor.execute("DROP TABLE IF EXISTS Dye")
conn.commit()

cursor.execute("""CREATE TABLE Kit (
                   id integer,
                   name text,
                   UNIQUE(id),
                   UNIQUE(name)
                   )""")
conn.commit()

cursor.execute("""CREATE TABLE Dye (
                    kitId integer,
                    dyeId integer,
                    name text,
                    realId integer,
                    color1 text,
                    color2 text,
                    color3 text,
                    UNIQUE (kitID,dyeId))""")

cursor.execute("""CREATE TABLE Blc (
                   id integer,
                   date_from date,
                   date_to date,
                   UNIQUE(id,date_from,date_to)
                   )""")
conn.commit()

cursor.execute("""CREATE TABLE Curr (
                   id integer,
                   date_from date,
                   UNIQUE(id,date_from)
                   )""")

print("Database created!")