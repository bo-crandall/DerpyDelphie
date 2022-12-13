import mysql.connector as mysql
import re
import string
import time

dbc = mysql.connect(
    host = "delphi",
    user = "delphi",
    password = "delphi",
    database = "delphi"

)

sql = dbc.cursor()

f = open("lovecraft-sentences.txt")
dbc.start_transaction()
sql.execute("truncate dub")
dbc.commit()
lines = 0
dbc.start_transaction()
start_time = time.time();
for text in f:
    if lines % 10 == 1:
        dbc.commit()
        dbc.start_transaction()
        percent = round((lines/16660),2)
        runtime = time.time() - start_time
        if not percent == 0:
            remaining = (runtime / percent) - runtime
        else:
            remaining = 0
        print(runtime,lines,16660,percent * 100,remaining,remaining/60)
    lines += 1
    text = re.sub(r'[^a-zA-Z0-9 ]','',text.lower().strip()) #simplify the string
    stext = text.split() #split the text into words
    for w in range(len(stext)-1):
        #dubs pass
        if w == 0:
            first = "#"
            second = stext[0]
            next = stext[1]
        elif w == len(stext) - 2:
            first = stext[w]
            second = stext[w+1]
            next = "!"
        else:
            first = stext[w]
            second = stext[w+1]
            next = stext[w+2]
        sql.execute("select weight,id from dub where first = %s and second = %s and next = %s",(first,second,next))
        dbresult = sql.fetchall()
        #print("DBResult:",dbresult)
        if len(dbresult) == 0: #if there are zero occurances of that first and next, make a new one
            sql.execute("insert into dub (first, second, next, weight) values (%s, %s, %s, 1)",(first, second, next))
        else: #if it does already exist, update the weight
            newweight = dbresult[0][0] + 1
            sql.execute("update dub set weight = %s where id = %s",(newweight, dbresult[0][1]))
dbc.commit()