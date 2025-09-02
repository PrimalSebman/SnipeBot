# Imports - Generic
import os
from dotenv import load_dotenv
import random
import asyncio
import json

#Imports - Interactions
import interactions
from interactions import slash_command, SlashContext, BaseContext
from interactions import Client, Intents, listen
from interactions.api.events import Startup
from interactions import check, has_role, Member
from interactions import Converter, RoleConverter, MemberConverter
from interactions import slash_option, slash_user_option, OptionType, slash_str_option, SlashCommandChoice
from interactions import Embed

#Imports - Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#Setting up connection to Firebase db
cred = credentials.Certificate("TextFiles\snipebot-5bac2-firebase-adminsdk-fbsvc-51c5f40192.json")
firebase_admin.initialize_app(cred, {'databaseURL': "https://snipebot-5bac2-default-rtdb.firebaseio.com/"})
ref = db.reference("/")

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
              "\"Acceptance of mediocrity is the first step towards failure.\" - Jaimini Kalimohan \"Kali\" Shah",
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
    memberId = ctx.author.id
    guild = ctx.guild
    guildId = ctx.guild_id
    await ctx.defer()

    sniperRole = guild.get_role(snipeRoleId)

    if snipeRoleId in member.roles:
        await ctx.send("You are already a Sniper, so get Sniping!")
    else:
        await member.add_role(sniperRole)
        with open("snipeData.json", "r") as f:
            dict = json.load(f)
        #Now see if they're in the firebase already
        check = dict.get(str(guildId), {}).get(str(memberId), -1)
        if (check == -1):
            dict[str(guildId)][memberId] = {
                "Snipes": 0,
                "Points": 0,
                "Times Sniped": 0
            }
            with open("snipeData.json", "w") as f:
                json.dump(dict, f)
        ref = db.reference(f"/"+str(guildId))
        ref.set(dict[str(guildId)])
        await ctx.send("You're a Sniper now!")
 
#Target - Snipe someone else (gain points, add 1 to Snipe count, increment target's times Sniped)
@slash_command(
    name="snipe",
    description="SnipeBot Commands",
    sub_cmd_name="target",
    sub_cmd_description="Snipe another member of the server!"
)
@slash_option(
    name="target",
    description="User you Sniped",
    required=True,
    opt_type=OptionType.USER,
    argument_name="user"
)
async def target(ctx: SlashContext, user: Member):
    snipeRoleId = next((role for role in ctx.guild.roles if role.name == "Sniper"), None)
    member = ctx.author
    memberId = ctx.author.id
    guild = ctx.guild
    guildId = ctx.guild_id
    userId = user.id
    await ctx.defer()

    sniperRole = guild.get_role(snipeRoleId)
    if (sniperRole not in member.roles):
        await ctx.send("Sorry, you're not a Sniper yet.")
        await ctx.send("Run \"/snipe register\" to become a Sniper and try this Snipe again!")
    else:
        await ctx.send("You Sniped: "+user.mention+"!")
        with open("snipeData.json", "r") as f:
            data = json.load(f)
        snipes = data.get(str(guildId), {}).get(str(memberId), -1).get("Snipes", -1)
        snipes += 1
        points = data.get(str(guildId), {}).get(str(memberId), -1).get("Points", -1)
        if (sniperRole in user.roles):
            points += 10
            otherTimesSniped = data[str(guildId)][str(userId)].get("Times Sniped", 0)
            otherTimesSniped += 1
            data[str(guildId)][str(userId)]["Times Sniped"] = otherTimesSniped
        else:
            points += 5
        data[str(guildId)][str(memberId)]["Snipes"] = snipes
        data[str(guildId)][str(memberId)]["Points"] = points
        await ctx.send("You have "+str(snipes)+" Snipes!")
        with open("snipeData.json", "w") as f:
                json.dump(data, f)
        ref = db.reference(f"/"+str(guildId))
        ref.set(data[str(guildId)])

@slash_command(
    name="snipe",
    description="SnipeBot Commands",
    sub_cmd_name="leaderboard",
    sub_cmd_description="See the Leaderboard of Snipers!"
)
@slash_option(
    name="leaderboard",
    opt_type=OptionType.STRING,
    argument_name="leader",
    description="Leaderboard!",
    required=True,
    choices=[
        SlashCommandChoice(name="Snipes", value="Snipes"),
        SlashCommandChoice(name="Points", value="Points"),
        SlashCommandChoice(name="Times Sniped", value="Times Sniped")
    ]
)
async def leaderboard(ctx: SlashContext, leader: str):
    await ctx.defer()
    with open("snipeData.json", "r") as f:
        data = json.load(f) #Load data with json file
    guildData = data[str(ctx.guild.id)]
    leaderData = {}
    for userid in guildData:
        memberName = await ctx.guild.fetch_member(int(userid))
        memberName = memberName.display_name
        leaderData[memberName] = guildData[userid][leader]
    sortedData = dict(sorted(leaderData.items(), key = lambda item: item[1], reverse = True))
    board = Embed(
        title="Leaderboard",
        description="Top Snipers!",
        color=0x003057
    )

    for rank, entry in enumerate(sortedData, start=1):
        board.add_field(
            name=f"#{rank}: {entry}",
            value=f"{sortedData[entry]} "+leader,
            inline = False
        )
    await ctx.send(embeds=board)


bot.start(TOKEN)