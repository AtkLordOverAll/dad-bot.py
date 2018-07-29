import discord
from discord.ext import commands
import json
import pickle
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
with open("./data/CTSuggestions.pickle") as f:
    CTSuggestions = pickle.load(f) #Pyson("./data/cleanTextSuggestions")
perms = Pyson("./data/permLevels")

cleaner = re.compile(u"(<:[^\s]*>)|[~_*`]|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]", flags=re.UNICODE)
BLURPLE = discord.Colour(0x7289da)
# End globals

# Custom classes #
class Suggestion():
    def __init__(userID, trigger, response):
        self.userID = userID
        self.trigger = trigger
        self.response = response
        self.msgID = None
# End custom classes

bot = commands.Bot(command_prefix = config.data["prefix"], description = "The dadliest dad there is.")

@bot.event
async def on_ready():
    print(f"Running discord.py version {discord.__version__}")
    gameName = config.data["game"]
    if gameName:
        await bot.change_presence(game = discord.Game(name = gameName))
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
async def on_member_join(member):
    if not member.bot:
        await bot.add_roles(member, discord.utils.get(member.server.roles, id = config.data["tier1"]))
        await bot.send_message(member.server.get_channel("218804362061807617"), f"Welcome {member.display_name}, it's nice to meet you!")
    else:
        await bot.send_message(member.server.get_channel("218804362061807617"), "Another bot rivals my presence... my jimmies are rustled.")

@bot.event
async def on_message(message):
    # Plain text functionality
    if message.author.bot or message.channel.is_private:
        return

    if message.mentions and message.mentions[0].mention == message.content.strip():
        await bot.send_message(message.channel, message.content)
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
    await bot.say("Hi {}!".format(ctx.message.author.display_name))

@pcheck.t1()
@bot.command(pass_context = True)
async def rgb(ctx, r , g, b):
    """
    Describes a colour to the user based on a given RGB value

    Usage: rgb [red value] [green value] [blue value]
    """

    try:
        if float(r) > 255 or float(g) > 255 or float(b) > 255:
            await bot.say("Use realistic numbers son. Don't you know your powers of two?")
            return
        rgb = (float(r) // 85, float(g) // 85, float(b) // 85)
    except ValueError:
        await bot.say("It'd be nice if you used numbers son. Have you been skipping school?")
        return

    await bot.say("Good question son!")
    output = "As you can clearly see, "

    if rgb[0] == 0:
        output += "there isn't a lot of red, "
    elif rgb[0] == 1:
        output += "you've got some red in there, "
    elif rgb[0] >= 2:
        output += "you've got a healthy dollop of red, "

    if rgb[1] == 0:
        output += "not much green, "
    elif rgb[1] == 1:
        output += "you've got some green, "
    elif rgb[1] >= 2:
        output += "a strong dollop of Shrek in the mix, "

    if rgb[2] == 0:
        output += "and barely any blue to be frank."
    elif rgb[2] == 1:
        output += "and a splotch of blue to round it all off."
    elif rgb[2] >= 2:
        output += "and holy cow this is my jam!\n*I'm blue da ba dee da ba daa*\n*Da ba dee da ba daa, da ba dee da ba daa, da ba dee da ba daa*\n*Da ba dee da ba daa, da ba dee da ba daa, da ba dee da ba daa*"

    await bot.say(output)
    await bot.say("I hope that helped you come to terms with that colour you just gave me. I've basically inherited the abilities of one of my many sons, Mallen.")

@pcheck.t1()
@bot.command(pass_context = True)
async def armyify(ctx, *, phrase = None):
    await bot.say(f"**Sir {ctx.message.author.display_name}, yes sir!**")

    if phrase:
        phrase = phrase.upper()
        await bot.delete_message(ctx.message)
        sub = Pyson("./data/phoneticAlphabet")
        output = ""
        newWord = True

        for letter in phrase:
            if letter in sub.data.keys():
                if newWord:
                    output += "**{}**".format(sub.data[letter])
                    newWord = False
                else:
                    output += sub.data[letter]
                output += " "
            elif letter == " ":
                newWord = True
            else:
                output += letter

        output = output[:-1] + ", sir!"

        await bot.say(output)

@pcheck.t1()
@bot.command(pass_context = True)
async def aliasSuggest(ctx, trigger, response):
    if not CTSuggestions[ctx.message.server.id]:
        CTSuggestions[ctx.message.server.id] = []
    CTSuggestions[ctx.message.server.id].append(Suggestion(ctx.message.author.id, re.sub(cleaner, "", trigger.content.lower()), response))
    await bot.say(f"{ctx.message.author.display_name}, your suggestion was received for moderator review.")
    await bot.delete_message(ctx.message)

    with open("./data/CTSuggestions.pickle") as f:
        pickle.dump(CTSuggestions, f, protocol=pickle.HIGHEST_PROTOCOL)

@pcheck.mods()
@bot.command(pass_context = True)
async def alias(ctx, trigger, response):
    trigger = re.sub(cleaner, "", trigger)
    if trigger in CTResponses.data.keys():
        await bot.say("Alias for that phrase already exists I'm afraid")
    else:
        CTResponses.data[trigger] = response
        CTResponses.save()
        await bot.say("New hip and trendy phrase acquired. Watch out kiddos!")
    await bot.delete_message(ctx.message)

@pcheck.mods()
@bot.command()
async def aliasList():
    em = discord.Embed(title="**Aliases**", description="*Please do not share this around, it will result in swift removal of both your message and ability to use this command.*", color=BLURPLE)
    for key in CTResponses.data.keys():
        em.add_field(name = key, value = CTResponses.data[key], inline = False)

    await bot.whisper(embed = em)
    await bot.say("DM'd 😉")

@pcheck.mods()
@bot.command()
async def aliasRemove(*, trigger):
    trigger = re.sub(cleaner, "", trigger)
    try:
        del CTResponses.data[trigger]
        await bot.say("Alias removed. Sorry for any offense caused. It's hard being in with the kids.")
    except KeyError:
        await bot.say("Specified alias/trigger could not be found. Try again?")

@pcheck.mods()
@bot.command(pass_context = True)
async def aliasReview(ctx, user: discord.Member = None):
    #messageStore = {}
    if user:
        iterateOver = CTSuggestions.data[user.id]
        if iterateOver == None or iterateOver == {}:
            await bot.say(f"No suggestions from that {user.display_name} were found.")
        else:
            pass
    else:
        if CTSuggestions.data == None or CTSuggestions.data == {}:
            await bot.say("No suggestions found to review.")
        else:
            pass

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
@bot.command()
async def joinUs():
    await bot.whisper("Add me to your server with this: {}".format(discord.utils.oauth_url(bot.user.id)))
    await bot.reply("DM'd 😉")

@pcheck.devs()
@bot.command()
async def log(*, toLog):
    print(toLog)

@pcheck.devs()
@bot.command(pass_context = True)
async def listIDs(ctx):
    embed=discord.Embed(title="Role IDs for {}".format(ctx.message.server.name), color=BLURPLE)
    embed.set_footer(text="As requested by you, son.")
    for role in ctx.message.server.roles:
        embed.add_field(name=role.name, value=role.id, inline=False)

    await bot.say(embed = embed)

@pcheck.owner()
@bot.command()
async def shutdown():
    await bot.say("Goodbye 👋")
    await bot.logout()

@pcheck.owner()
@bot.command()
async def setGame(*, gameName:str = None):
    if gameName:
        await bot.change_presence(game = discord.Game(name = gameName))
        await bot.say("All sorted for you, dearest son.")
    else:
        await bot.change_presence(game = None)
        await bot.say("Playing status cleared. And they all lived happily ever after.")

    if not gameName == config.data["game"]:
        config.data["game"] = gameName
        config.save()

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
