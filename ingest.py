import discord
import mysql.connector as mysql
import re
import string
import random
import time

optoutid = 1051237774130417684

dbc = mysql.connect(
    host = "delphi",
    user = "delphi",
    password = "delphi",
    database = "delphi"

)

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
        sql = dbc.cursor()
        guild = message.guild
        channel = message.channel
        for i in guild.text_channels:
            #await i.send("#I am scanning this channel")
            messages = 0
            sql = dbc.cursor()
            dbc.start_transaction()
            async for m in i.history(limit=None):
                messages += 1
                if messages % 10 == 0:
                    print(messages)
                #start filtering unsuitable messages, we don't want attachments, embeds,  or stickers 
                if len(m.attachments) > 0:
                    continue
                if len(m.embeds) > 0:
                    continue
                if len(m.stickers) > 0:
                    continue
                text = m.clean_content.encode('ascii','ignore').decode() #convert to ascii only, ignoring any characters that don't fit.
                if text[0] not in ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@"'): #ignore any messages starting with funky characters.  Filters bot commands
                    continue
                text = re.sub(r'(<:)(.*)>',' ',text) #filter customer emojis.  Discord uses in-band signaling for custom emojis, so we just replace that signal with nothing
                #print("Message:",text)
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
                    sql.execute("select weight from single where first = %s and next = %s",(first,next))
                    dbresult = sql.fetchall()
                    #print("DBResult:",dbresult)
                    if len(dbresult) == 0: #if there are zero occurances of that first and next, make a new one
                        sql.execute("insert into single (first, next, weight) values (%s, %s, 1)",(first, next))
                    else: #if it does already exist, update the weight
                        newweight = dbresult[0][0] + 1
                        #print("New Weight:",newweight)
                        sql.execute("update single set weight = %s where first = %s and next = %s",(newweight, first, next))
            dbc.commit()
            sql.close()
    if message.content.startswith("$emote"):
        await message.channel.send("<:rooThink1:580614815408586762>")
    if message.content.startswith("$ryleh"):
        resp = buildResponse("#")
        await message.channel.send(resp)
                        



def buildResponse(word):
    random.seed(time.time())
    db = dbc.cursor()
    getWeight = "select sum(weight) from single where first = %s"
    getWords = "select next,weight from single where first = %s"
    #steps to find a word: get total weight, select a random number, fetch word list, interate through, recusively select next work
    db.execute(getWeight,word)
    sumWeight = db.fetchall()
    if len(sumWeight) == 0:
        db.close()
        return ""
    selection = random.randint(1,sumWeight)
    db.execute(getWords,word)
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
        if i[0] == "!":
            return ""
        else:
            return i[0] + buildResponse(i[0])
    


client.run(token)