import discord
from discord.ext import commands
import json
import re
import traceback

from plugins import pcheck
from plugins.pyson import Pyson

# Load globals
config = Pyson("./config")
if config.data == {}:
    print("Please come back when you've set yourself up a config file")
    quit()

CTResponses = Pyson("./data/cleanTextResponses")
CTSuggestions = Pyson("./data/cleanTextSuggestions")
perms = Pyson("./data/permLevels")

cleaner = re.compile(u"(<:[^\s]*>)|[~_*`]|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]", flags=re.UNICODE)
# End globals

bot = commands.Bot(command_prefix = config.data["prefix"], description = "The dadliest dad there is.")

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
        prettyError = discord.Embed(title="You made a boo-boo!", description=error.original.__traceback__, color=0xff0000)
        prettyError.set_footer(text="Now go think about what you've done")
        await bot.send_message(channel, embed = prettyError)
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

    cleanMsg = re.sub(cleaner, "", message.content.lower()) # regex removes :emotes: and *~_` characters

    if cleanMsg in CTResponses.data.keys():
        await bot.send_message(message.channel, CTResponses.data[message.content])
        return

    if cleanMsg.startswith("im "):
        await bot.send_message(message.channel, dadJoke(cleanMsg[3:]))
        return
    elif cleanMsg.startswith(("i m ", "i'm ")):
        await bot.send_message(message.channel, dadJoke(cleanMsg[4:]))
        return
    elif cleanMsg.startswith("i am "):
        await bot.send_message(message.channel, dadJoke(cleanMsg[5:]))
        return
    # End plain text functionality

    await bot.process_commands(message)

@pcheck.t1()
@bot.command(pass_context = True)
async def noticeMe(ctx):
    await bot.say("Hi {}".format(ctx.message.author.name))

@pcheck.t1()
@bot.command(pass_context = True)
async def aliasSuggest(ctx, trigger, response):
    if not CTSuggestions.data[ctx.message.author.id]:
        CTSuggestions.data[ctx.message.author.id] = {}
    CTSuggestions.data[ctx.message.author.id][trigger] = response
    await bot.say("Suggestion received for moderator review.")
    await bot.delete_message(ctx.message)

@pcheck.mods()
@bot.command(pass_context = True)
async def alias(ctx, trigger, response):
    trigger = re.sub(cleaner, "", trigger)
    if trigger in CTResponses.data.keys():
        await bot.say("Alias for that phrase already exists I'm afraid")
    else:
        CTResponses.data[trigger] = response
        await bot.say("New hip and trendy phrase acquired. Watch out kiddos!")
    await bot.delete_message(ctx.message)

@bot.command(pass_context = True)
async def updatePerms(ctx, member: discord.Member = None):
    if not manualPermCheck(ctx.message.author, 4):
        await bot.say("Insufficient permissions to use that command")
    if member:
        permIndividualUpdate(member)
        await bot.say("Permission levels updated for {}. Hope that helps.".format(member.name))
    else:
        perms.data = permFullUpdate(ctx.message.server)
        perms.save(True)
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

@pcheck.owner()
@bot.command(pass_context = True)
async def shutdown(ctx):
    await bot.say("Goodbye 👋")
    await bot.logout()

@pcheck.owner()
@bot.command(pass_context = True)
async def setGame(ctx, gameName:str = None):
    if gameName:
        await bot.change_presence(game = discord.Game(game = gameName))
    else:
        await bot.change_presence(game = None)

    config.data["game"] = gameName
    config.save()
    await bot.say("All sorted. That better?")

def dadJoke(phrase):
    wList = phrase.split(" ")
    for n in range(len(wList)):
        wList[n] = wList[n][0].upper() + wList[n][1:]
        if wList[n].endswith((",", ".", "?", "!", "&")):
            wList[n] = wList[n][:-1]
            wList = wList[:n+1]
            break
    return "Hi {}, I'm Dad.".format(" ".join(wList))

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
        if config.data["ownerID"] == user.id:
            return True
    elif config.data[levels[level]] in user.roles:
        return True
    else:
        try:
            return manualPermCheck(user, level + 2)
        except IndexError:
            return False

def permLevel(member):
    if member.bot:
        return 0
    elif config.data["ownerID"] == member.id:
        return 6

    holding = 0

    for role in member.roles:
        if role.id == config.data["devs"]:
            return 5
        elif role.id == config.data["mods"] and holding < 4:
            holding = 4
        elif role.id == config.data["tier3"] and holding < 3:
            holding = 3
        elif role.id == config.data["tier2"] and holding < 2:
            holding = 2
        elif role.id == config.data["tier1"] and holding < 1:
            holding = 1

    return holding

def permIndividualUpdate(member):
    perms.data[member.id] = permLevel(member)
    perms.save(True)

def permFullUpdate(server):
    notPermLevels = {}

    for member in server.members:
        notPermLevels[member.id] = permLevel(member)

    return notPermLevels

bot.run(config.data["token"])
