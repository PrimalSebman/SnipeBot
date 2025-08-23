# Imports - Generic
import os
from dotenv import load_dotenv
import random
import asyncio

#Imports - Interactions
import interactions
from interactions import slash_command, SlashContext, BaseContext
from interactions import Client, Intents, listen
from interactions import check, has_role, Member
from interactions import Converter, RoleConverter
from interactions import slash_option, slash_user_option, OptionType

#Imports - Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#Setting up connection to Firebase db
cred = credentials.Certificate("TextFiles\snipebot-5bac2-firebase-adminsdk-fbsvc-51c5f40192.json")
firebase_admin.initialize_app(cred)
ref = db.reference("/", None, "https://console.firebase.google.com/u/0/project/snipebot-5bac2/database/snipebot-5bac2-default-rtdb/data")

#Loading Token (for Discord connection)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Initializing bot
bot = Client(intents=Intents.DEFAULT)

#Quote - Mostly just a test command
@slash_command(
    name="snipe",
    description="SnipeBot Commands",
    sub_cmd_name="quote",
    sub_cmd_description="Get a random video game sniper quote"
)
async def snipe_quote(ctx: SlashContext):
    quotes = ["\"Do you know what an artist and a sniper have in common? Details.\" - Timur \"Glaz\" Glazkov",
              "\"Acceptance of mediocrity is the first step towards failure.\" - Jaimini \"Kali\" Shah",
              "\"You're all a bunch of no-hopers.\" - TF2 Sniper",
              "\"The tide of war has turned.\" - Karl Fairburne"]
    sendQuote = random.choice(quotes)
    await ctx.send(sendQuote)

#Register - Gain Sniper role, make new entry for user on Firebase, populate w/ 0 Snipes, 0 Points, 0 times Sniped
@slash_command(
    name="snipe",
    description="SnipeBot Commands",
    sub_cmd_name="register",
    sub_cmd_description="Give yourself the Sniper role"
)
async def register(ctx: SlashContext):
    snipeRoleId = next((role for role in ctx.guild.roles if role.name == "Sniper"), None)
    member = ctx.author
    guild = ctx.guild

    sniperRole = guild.get_role(snipeRoleId)

    if snipeRoleId in member.roles:
        await ctx.send("You are already a Sniper, so get Sniping!")
    else:
        await member.add_role(sniperRole)
        await ctx.send("You're a Sniper now!")
 
#Target - Snipe someone else (gain points, addd 1 to Snipe count, increment target's times Sniped)
@slash_command(
    name="snipe",
    description="SnipeBot Commands",
    sub_cmd_name="target",
    sub_cmd_description="Snipe another member of the server!"
)
@slash_option(
    name="user_option",
    description="User you Sniped",
    required=True,
    opt_type=OptionType.USER,
    argument_name="user"
)
async def target(ctx: SlashContext, user: Member):
    await ctx.send("You Sniped: "+user.mention+"!")

bot.start(TOKEN)