memory = {}
banned = ["moutonvache"]
channels = []
bannedwords = "nig.+|sk.+|gyat.+|sigm.+"

import re
import random
import discord
from discord.ext import commands
from discord import app_commands

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="idk!")
import json

try:
    with open("memory.json", "r") as f:
        memory = json.load(f)
except Exception as e:
    print(e)
try:
    with open("channels.json", "r") as f:
        channels = json.load(f)
except:
    pass


def learn(sentence):
    tmp = sentence.lower().split(" ")
    state = 0
    currentword0 = ""
    currentword1 = ""
    print("Generating pairs...")
    for word in tmp:
        if re.match(bannedwords, word):
            print("Blocked word", word)
            return
        if state == 0:
            print("State: 0!", word)
            currentword0 = word
            if currentword1 != "":
                try:
                    memory[currentword1].append(word)
                except:
                    memory[currentword1] = []
                    memory[currentword1].append(word)
            state = 1
        else:
            print("State: 1!", word)
            try:
                memory[currentword0].append(word)
            except:
                memory[currentword0] = []
                memory[currentword0].append(word)
            currentword1 = word
            state = 0
    try:
        repl = memory[tmp[-1]]
    except:
        repl = ""
    if len(tmp) == 1 and repl == "":
        memory[tmp[-1]] = []
        print("Learnt last word as a placeholder.")
    else:
        print(len(tmp))
    with open("memory.json", "w") as f:
        json.dump(memory, f, indent=4)
    print("Generated pairs")


def genfromword(word):
    nomatch = 0
    currentword = word.lower()
    pos = 0
    sentence = []
    counter = 0
    state = True
    if re.match(bannedwords, word):
        return "Blocked response"
    if word.split(" ") != 1 and not re.match("h.+?(?=o)|h.+i|b.+?(?=e)|hi|.+h.+?(?=o)|.+h.+i|.+b.+?(?=e)|hi", word):
        currentword = word.split(" ")[-1].lower() 
    elif re.match("h.+?(?=o)|h.+i|b.+?(?=e)|hi|.+h.+?(?=o)|.+h.+i|.+b.+?(?=e)|hi", word):
        currentword = word.split(" ")[0].lower() 
        print("Got greeting")
    sentence.append(currentword)
    while state:
        if counter > 50:
            state = False
        try:
            match = memory[currentword]
            if len(match) != 0:
                print("Match!", match)
                word = random.choice(list(match))
                if word == currentword and len(match) < 2:
                    while count < 5:
                        # brute force, hehe
                        word = random.choice(list(match))
                        count += 1
                sentence.append(word)
                currentword = word
                counter += 1
                print(counter)
            else:
                state = False
        except:
            state = False
    print("Generating finished, got", sentence)
    if sentence != []:
        return " ".join(sentence)
    else:
        print("Generating random sentence...")
        return "**IDK** what to say\n-# > Teach me"


@bot.command()
@commands.has_permissions(administrator=True)
async def set(ctx):
    channels.append(str(ctx.channel.id))
    with open("channels.json", "w") as f:
        json.dump(channels, f)
    await ctx.channel.send("Channel set successfully!")


@bot.command()
@commands.has_permissions(administrator=True)
async def unset(ctx):
    try:
        channels.remove(str(ctx.channel.id))
    except:
        pass
    with open("channels.json", "w") as f:
        json.dump(channels, f)
    await ctx.channel.set("Channel unset successfully.")


@bot.event
async def on_message(message):
    if message.author.name in banned:
        print("Banned user tried to use the bot")
        return
    oldlen = len(memory)
    if (
        not message.content.startswith("idk!")
        and not message.author.bot
        and str(message.channel.id) in channels
        and message.attachments
    ):
        learn(f"{message.content} {message.attachments[0].url}")
    elif (
        not message.content.startswith("idk!")
        and str(message.channel.id) in channels
        and message.attachments
        and not message.author.bot
        and not message.content
    ):
        learn("{message.attachments[0].url}")
    elif (
        not message.content.startswith("idk!")
        and str(message.channel.id) in channels
        and not message.author.bot
        and message.content
    ):
        learn(message.content)
    if str(message.channel.id) in channels and not message.author.bot:
        async with message.channel.typing():
            try:
                await message.channel.send(
                    f'{genfromword(message.content).replace("@everyone", "").replace("<@", "").replace("@here", "").replace("<#", "")}\n> -# Current vocabulary length: {len(memory)}\n> -# You increased the vocabulary length by {len(memory) - oldlen}.'
                )
            except:
                pass
    # if not message.content.startswith("idk!"):
    #    learn(message.content)
    await bot.process_commands(message)


@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name=genfromword("hi").replace("hi", "")))
    print("Synced commands and connected to API")
    print("====================================")


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command()
async def gen(interaction, prompt: str):
    await interaction.response.defer()
    if interaction.user.name in banned:
        return
    await interaction.edit_original_response(
        content=f'{genfromword(prompt).replace("<#", "").replace("@everyone", "").replace("<@", "").replace("@here", "")}\n> -# Current vocabulary length: {len(memory)}'
    )


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@bot.tree.command(name="learn")
async def cmd(interaction, prompt: str):
    await interaction.response.defer()
    if interaction.user.name in banned:
        return
    oldlen = len(memory)
    learn(prompt)
    await interaction.edit_original_response(
        content=f":white_check_mark:\n> -# You increased the vocabulary length by {len(memory) - oldlen}."
    )

bot.run("token here")
