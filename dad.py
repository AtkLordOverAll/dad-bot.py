import discord
from discord.ext import commands
import re
import traceback
from datetime import timedelta

from plugins import pcheck
from plugins.pyson import Pyson
from plugins.pyckle import Pyckle

# Custom classes #
class Suggestion():
    def __init__(self, trigger, response):
        self.trigger = trigger
        self.response = response
        self.say = f"{trigger} -> {response}"
        self.msg = None
# End custom classes

# Load globals
config = Pyson("./config")
if config.data == {}:
    print("Please come back when you've set yourself up a config file")
    quit()

CTResponses = Pyson("./data/cleanTextResponses")
CTSuggestions = Pyckle("./data/CTSuggestions")

CLEANER = re.compile(u"(<:[^\s]*>)|[~_*`]|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]", flags=re.UNICODE)
BLURPLE = discord.Colour(0x7289da)
# End globals

bot = commands.Bot(command_prefix = config.data["prefix"], description = "The dadliest dad there is.")

@bot.event
async def on_ready():
    if CTSuggestions.data == None:
        CTSuggestions.data = {}
        for server in bot.servers:
            CTSuggestions.data[server.id] = {}
            for member in server.members:
                CTSuggestions.data[server.id][member.id] = []
        CTSuggestions.save()

    print(f"Running discord.py version {discord.__version__}")
    gameName = config.data["game"]
    if gameName:
        await bot.change_presence(game = discord.Game(name = gameName))
    print("Logged in as {} (ID: {})\n".format(bot.user.name, bot.user.id))

"""
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
"""

@bot.event
async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'), color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'), color=discord.Color.blue())
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

    cleanMsg = re.sub(CLEANER, "", message.content.lower()) # regex removes :emotes: and *~_` characters

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
    print(CTSuggestions.data)
    trigger = re.sub(CLEANER, "", trigger.lower())
    storeThis = Suggestion(trigger, response)
    lst = CTSuggestions.data[ctx.message.server.id][ctx.message.author.id] # errors hard
    lst.append(storeThis)
    CTSuggestions.save()
    await bot.say(f"{ctx.message.author.display_name}, your suggestion was received for moderator review.")
    await bot.delete_message(ctx.message)

@pcheck.mods()
@bot.command(pass_context = True)
async def alias(ctx, trigger, response):
    trigger = re.sub(CLEANER, "", trigger)
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
    for trigger, response in CTResponses.data.items():
        em.add_field(name = trigger, value = response, inline = False)

    await bot.whisper(embed = em)
    await bot.say("DM'd :wink:")

@pcheck.mods()
@bot.command()
async def aliasRemove(*, trigger):
    trigger = re.sub(CLEANER, "", trigger)
    try:
        del CTResponses.data[trigger]
        CTResponses.save()
        await bot.say("Alias removed. Sorry for any offense caused. It's hard being in with the kids.")
    except KeyError:
        await bot.say("Specified alias/trigger could not be found. Try again?")

@pcheck.mods()
@bot.command(pass_context = True)
async def aliasReview(ctx, number = -1, user: discord.Member = None):
    count = int(number)

    if number == 0:
        await bot.say("There was literally one number you couldn't use, and this was it")
        return

    if user:
        if len(CTSuggestions.data[ctx.message.server.id][user.id]) > 0:
            await bot.say("Sure thing")
            await bot.whisper(f"__Suggestions from {user.display_name}:__")
            for suggestion in CTSuggestions.data[ctx.message.server.id][user.id]:
                suggestion.msg = await bot.whisper(f"\"{suggestion.trigger}\" :arrow_right: \"{suggestion.response}\"")

                count -= 1
                if count == 0:
                    break
        else:
            await bot.say(f"No suggestions from {user.display_name} were found")

    else:
        await bot.say("Sure thing")
        for memberID, suggestions in CTSuggestions.data[ctx.message.server.id].items():
            if len(suggestions) > 0:
                await bot.whisper(f"__Suggestions from {ctx.message.server.get_member(memberID).display_name}:__")
                for suggestion in suggestions:
                    suggestion.msg = await bot.whisper(f"\"{suggestion.trigger}\" :arrow_right: \"{suggestion.response}\"")

                    count -= 1
                    if count == 0:
                        break

@pcheck.mods()
@bot.command(pass_context = True)
async def aliasReviewComplete(ctx, user: discord.Member = None):
    accepts = 0
    rejects = 0
    if user and len(CTSuggestions.data[ctx.messsage.server.id][user.id]) > 0:
        for suggestion in CTSuggestions.data[ctx.messsage.server.id][user.id]:
            if suggestion.msg:
                message = await bot.get_message(ctx.message.author.id, suggestion.msg)
                for react in message.reactions:
                    print(react.id)
                    if react.id ==
            else:
                break # if only a certain amount of suggestions were checked, they are sent in the same order this loop runs, so there shouldn't be any items with a message id after this
    else:
        for suggestList in CTSuggestions.data[ctx.messsage.server.id].values():
            if len(suggestList) > 0:
                for suggestion in suggestList:
                    if suggestion.msg:
                        message = await bot.get_message(ctx.message.author.id, suggestion.msg)
                        for react in message.reactions:
                            print(react.id)
                            if react.id == "yesvalue":
                                accepts += 1
                                changeTo = f"Accepted ~~{message.content}~~"
                                pass
                            elif react.id == "novalue":
                                rejects += 1
                                changeTo = f"Rejected ~~{message.content}~~"
                                pass
                            else:
                                continue

                            await bot.edit_message(message, changeTo)

@pcheck.devs()
@bot.command()
async def joinUs():
    await bot.whisper("Add me to your server with this: {}".format(discord.utils.oauth_url(bot.user.id)))
    await bot.reply("DM'd :wink:")

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

bot.run(config.data["token"])
