import discord
import asyncio
import aiohttp
import os
import re
import random
import json

def parseReplys(reply):
    regex = r"\$\{([\w\ ]+)\}"
    parsed = reply
    matches = re.finditer(regex, reply, re.MULTILINE)
    if not matches:
        return parsed
    
    for i in matches:
        com = i.group(1).split()
        if com[0] == "rand":
            if len(com) >= 3:
                result = random.randint(int(com[1]), int(com[2]))
                parsed = parsed.replace(i.group(), str(result), 1)
        else:
            parsed = parsed.replace(i.group(), "\"ERROR\"")

    return parsed


async def asyncDereInfoSend(message, userID):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://deresute.me/{}/json".format(userID)) as resp:
            userData = await resp.json()
            if "api_error" in userData:
                await message.channel.send("api error : " + str(userData["api_error"]))
            elif "name" in userData:
                await message.channel.send(userData["name"] + " " + str(userData["level"]) + " " + userData["comment"])
            else:
                await message.channel.send("Wrong response. Contact developer.")


class discordClient(discord.Client):
    async def on_ready(self):
        print("Bot logged on as", self.user)

    async def on_message(self, message):
        # We don't need to respond to ourselves
        if message.author == self.user:
            return
        
        splitedMessage = message.content.split(' ')
        # All commands start with mirei
        if (splitedMessage[0] == "mirei") & (len(splitedMessage) > 1):
            # For test ping
            if splitedMessage[1] == "test":
                await message.channel.send("test pong")
            # CGSS user info
            elif splitedMessage[1] == "info":
                # Process game info asyncronously to prevent programme from hogging
                async with message.channel.typing():
                    await asyncDereInfoSend(message, splitedMessage[2])
            else:
                if splitedMessage[1] in staticReplys:
                    if "image" in staticReplys[splitedMessage[1]]:
                        await message.channel.send(content = parseReplys(staticReplys[splitedMessage[1]]["reply"]),
                                                   file = discord.File(staticReplys[splitedMessage[1]]["image"]))
                    else:
                        await message.channel.send(parseReplys(staticReplys[splitedMessage[1]]["reply"]))
                else:
                    await message.channel.send("그런 거 없다")

try:
    with open("./staticReplys.json", 'r') as file:
        staticReplys = json.load(file)
        file.close()
except FileNotFoundError:
    print("Need to make staticReplys.json")
    raise SystemExit()
    

bot = discordClient()
bot.run(os.environ["DISCORDBOT_TOKEN"])