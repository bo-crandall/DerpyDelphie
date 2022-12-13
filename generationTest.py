import mysql.connector as mysql
import re
import string
import time
import random

dbc = mysql.connect(
    host = "delphi",
    user = "delphi",
    password = "delphi",
    database = "delphi"

)

def buildResponse(word):
    resp = ""
    random.seed(time.time())
    db = dbc.cursor()
    getWeight = "select sum(weight) from single where first = '{}' and weight > 1".format(word)
    getWords = "select next,weight from single where first = '{}' and weight > 1 order by weight desc".format(word)

    #steps to find a word: get total weight, select a random number, fetch word list, interate through, recusively select next work
    db.execute(getWeight)
    sumWeight = db.fetchall()
    #print(sumWeight)
    if len(sumWeight) == 0:
        db.close()
        return ""
    selection = random.randint(1,sumWeight[0][0])
    db.execute(getWords)
    words = db.fetchall()
    if len(words) == 0:
        db.close()
        return ""
    db.close()
    for i in words:
        weight = i[1]
        selection -= weight
        if selection > 0:
            continue
        print(i[0])
        if str(i[0]) == "!":
            return ""
        else:
            return str(i[0]) + " " + buildResponse(i[0])

print(buildResponse("#"))