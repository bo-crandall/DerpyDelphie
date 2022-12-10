import discord
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

    if message.content.startswith('$seed'):
        f = open("input.txt")
        for l in f:
            await message.channel.send(l)

client.run(token)