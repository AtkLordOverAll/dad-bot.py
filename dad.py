import discord
from discord.ext import commands
import json
import re

from plugins import pcheck

# Load globals
with open("config.json") as f:
    config = json.load(f)
with open("./data/cleanTextResponses.json") as f:
    CTResponses = json.load(f)
with open("./data/cleanTextSuggestions.json") as f:
    CTSuggestions = json.load(f)
with open("./data/permLevels.json") as f:
    perms = json.load(f)
# End globals

bot = commands.Bot(command_prefix = config["prefix"], description = "The dadliest dad there is.")

@bot.event
async def on_ready():
    print("Logged in as {} (ID: {})\n".format(bot.user.name, bot.user.id))

@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.CommandInvokeError):
        print("Exception in command '{}', {}".format(ctx.command.qualified_name, error.original))
        traceback.print_tb(error.original.__traceback__)
    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(channel, "Insufficient permissions for this command. Sorry son.")

@bot.event
async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)


@bot.event
async def on_message(message):
    # Plain text functionality
    if message.author.bot:
        return

    cleanMsg = re.sub("(:[^\s]*:)|[~_*`]", "", message.content.lower()) # regex removes :emotes: and *~_` characters

    if cleanMsg in CTResponses.keys():
        await bot.send_message(message.channel, CTResponses[message.content])
        return

    if cleanMsg.startswith(("i'm ", "im ", "i am ", "i m ")):
        # dad joke (snip 3)
        return
    elif cleanMsg.startswith(("i m ", "i'm ")):
        # dad joke (snip 4)
        return
    elif cleanMsg.startswith("i am "):
        # dad joke (snip 5)
        return
    # End plain text functionality

    await bot.process_commands(message)

@pcheck.t1()
@bot.command(pass_context = True)
async def noticeMe(ctx):
    await bot.say("Hi {}".format(ctx.message.author.name))

@bot.command(pass_context = True)
async def updatePerms(ctx, member: discord.Member = None):
    if not manualPermCheck(ctx.message.author, 4):
        await bot.say("Insufficient permissions to use that command")
    if member:
        permIndividualUpdate(member)
        await bot.say("Permission levels updated for {}. Hope that helps.".format(member.name))
    else:
        permFullUpdate(ctx.message.server)
        await bot.say("Permission levels updated for everyone. Glad to be of service.")

@pcheck.devs()
@bot.command(pass_context = True)
async def joinUs(ctx):
    await bot.whisper("Add me to your server with this: {}".format(discord.utils.oauth_url(bot.user.id)))
    await bot.reply("DM'd 😉")

@pcheck.devs()
@bot.command(pass_context = True)
async def log(ctx):
    print(ctx.message.content)

@pcheck.devs()
@bot.command(pass_context = True)
async def shutdown(ctx):
    await bot.say("Goodbye 👋")
    await bot.logout()
    quit()

@pcheck.owner()
@bot.command(pass_context = True)
async def setGame(ctx, gameName:str = None):
    if gameName:
        await bot.change_presence(game = discord.Game(game = gameName))
    else:
        await bot.change_presence(game = None)

    config["game"] = gameName
    saveJSON(config, "config")
    await bot.say("All sorted. That better?")

def manualPermCheck(user, level = 1):
    """
    Function
    Checks for user having a specific permission level, or one higher than specified

    Parameters: user (Discord member object), level (power level as integer)
    Returns: True if user has >= permissions, False otherwise
    """
    level -= 1
    levels = ["tier1", "tier2", "tier3", "mods", "devs", "owner"]

    if level == 5:
        if config["ownerID"] == user.id:
            return True
    elif config[levels[level]] in user.roles:
        return True
    else:
        try:
            return manualPermCheck(user, level + 2)
        except IndexError:
            return False

def permLevel(member):
    if member.bot:
        return 0
    elif config["ownerID"] == member.id:
        return 6

    holding = 0

    for role in member.roles:
        if role.id == config["devs"]:
            return 5
        elif role.id == config["mods"] and holding < 4:
            holding = 4
        elif role.id == config["tier3"] and holding < 3:
            holding = 3
        elif role.id == config["tier2"] and holding < 2:
            holding = 2
        elif role.id == config["tier1"] and holding < 1:
            holding = 1

    return holding

def permIndividualUpdate(member):
    perms[member.id] = permLevel(member)
    saveJSON(perms, "./data/permLevels", True)

def permFullUpdate(server):
    notPermLevels = {}

    for member in server.members:
        notPermLevels[member.id] = permLevel(member)

    saveJSON(notPermLevels, "./data/permLevels", True)
    return notPermLevels

def saveJSON(data, fileName = "data", sort = False):
    """
    Procedure
    Parameters: data (variable to save), fileName (name to give file, without prefix), sort (bool as to whether or not the data should be sorted)
    Saves a JSON file of given data
    """
    if not fileName.endswith(".json"):
        fileName += ".json"
    with open(fileName, "w") as outFile:
        json.dump(data, outFile, sort_keys = sort, indent = 4)

bot.run(config["token"])
