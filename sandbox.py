import discord
import mysql.connector as mysql

dbc = mysql.connect(
    host = "delphi",
    user = "delphi",
    password = "delphi",
    database = "delphi"

)

cur = dbc.cursor()

cur.execute("select * from single")

print(cur.fetchall())
