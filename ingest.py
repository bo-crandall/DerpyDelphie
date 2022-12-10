import discord
import mysql.connector as mysql
import re

dbc = mysql.connect(
    host = "delphi",
    user = "delphi",
    password = "delphi",
    database = "delphi"

)

sql = dbc.cursor()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

f = open("token.ini")
token = f.readline()
f.close()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$ping'):
        await message.channel.send('Pong!')

    if message.content.startswith('$scan'):
        guild = message.guild
        channel = message.channel
        for i in guild.text_channels:
            #await i.send("#I am scanning this channel")
            async for m in i.history(limit=10,oldest_first=False):
                text = str(m.clean_content).encode('ascii','ignore').decode() #cast content to string and convert it to ascii only, ignoring any characters that don't fit.
                #start filtering unsuitable messages, we don't want attachments, embeds,  or stickers 
                if len(m.attachments) > 0:
                    continue
                if len(m.embeds) > 0:
                    continue
                if len(m.stickers) > 0:
                    continue
                text = re.sub(r'[^a-zA-Z0-9 ]','',text.lower().strip()) #simplify the string
                stext = text.split() #split the text into words
                dbc.start_transaction()
                for w in range(len(stext)):
                    #singles pass
                    if w == 0:
                        first = "#"
                        next = stext[0]
                    elif w == len(stext) - 1:
                        first = stext[w]
                        next = "!"
                    else:
                        first = stext[w]
                        next = stext[w+1]
                    sql.execute("select count(*) from single where first = %s and next = %s",(first,next))
                    dbresult = sql.fetchall()
                    if dbresult[0][0] == 0:
                        sql.execute("insert into single (first, next, weight) values (%s, %s, 1)",(first, next))
                        print("Insert", first, next)
                    else:
                        sql.execute("update single set weight = weight + 1")
                        print("Update", first, next)
                dbc.commit()

                        





client.run(token)