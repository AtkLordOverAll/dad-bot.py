import discord
from discord.ext import commands
import json
import os

parent = os.path.dirname(os.path.dirname(__file__))

with open(parent + os.path.sep + "config.json") as f:
    configJSON = json.load(f)
    devs = [configJSON["devs"]]
    mods = [configJSON["mods"]] + devs
    tier3 = [configJSON["tier3"]] + mods
    tier2 = [configJSON["tier2"]] + tier3
    tier1 = [configJSON["tier1"]] + tier2

def t1():
    def predicate(ctx):
        authMe = ctx.message.author
        if authMe is ctx.message.server.owner:
            return True
        elif any(role.id in tier1 for role in authMe.roles):
            return True
        else:
            return False
    return commands.check(predicate)

def t2():
    def predicate(ctx):
        authMe = ctx.message.author
        if authMe is ctx.message.server.owner:
            return True
        elif any(role.id in tier2 for role in authMe.roles):
            return True
        else:
            return False
    return commands.check(predicate)

def t3():
    def predicate(ctx):
        authMe = ctx.message.author
        if authMe is ctx.message.server.owner:
            return True
        elif any(role.id in tier3 for role in authMe.roles):
            return True
        else:
            return False
    return commands.check(predicate)

def mods():
    def predicate(ctx):
        authMe = ctx.message.author
        if authMe is ctx.message.server.owner:
            return True
        elif any(role.id in mods for role in authMe.roles):
            return True
        else:
            return False
    return commands.check(predicate)

def devs():
    def predicate(ctx):
        authMe = ctx.message.author
        if authMe is ctx.message.server.owner:
            return True
        elif any(role.id in devs for role in authMe.roles):
            return True
        else:
            return False
    return commands.check(predicate)

def owner():
    def predicate(ctx):
        if ctx.message.author is ctx.message.server.owner:
            return True
        else:
            return False
    return commands.check(predicate)
