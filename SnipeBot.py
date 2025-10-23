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
from interactions.ext.paginators import Paginator

#Imports - Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#Loading Token (for Discord connection)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
FIREBASE_KEY_PATH = os.getenv('FIREBASE_KEY')

#Firebase connection
cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred, {'databaseURL': 'https://snipebot-5bac2-default-rtdb.firebaseio.com/'})
ref = db.reference("/")

#Initializing bot
bot = Client(intents=Intents.DEFAULT)

achievementsTotal = Embed(
    title="Achievements - Total Snipes",
    description="Get a lot of Snipes to earn these!",
    color=0xB3A369
)

achievementsStreak = Embed(
    title="Achievements - Killstreak",
    description="Get a high Killstreak to earn these!",
    color=0xB3A369
)

achievementsVariety = Embed(
    title="Achievements - Variety",
    description="You need to complete various tasks to earn these!",
    color=0xB3A369
)

achievementsSniped = Embed(
    title="Achievements - Sniped",
    description="To earn these, you need to... be sniped???",
    color=0xB3A369
)

achievementsSpecial = Embed(
    title="Achievements - Special",
    description="Unique achievements that are either hidden or really hard to get!",
    color=0xB3A369
)

achievementsTotal.add_field(name="Official", value="Get your first Snipe!", inline=True)
achievementsTotal.add_field(name="Earning Your Stripes", value="Get 5 Total Snipes", inline=True)
achievementsTotal.add_field(name="Contract Killer", value="Get 10 Total Snipes", inline=True)
achievementsTotal.add_field(name="Sentinel", value="Get 25 Total Snipes", inline=True)
achievementsTotal.add_field(name="Sniping Legend", value="Get 50 Total Snipes", inline=True)

achievementsStreak.add_field(name="Streak Activated", value="Get a Killstreak of 2", inline=True)
achievementsStreak.add_field(name="On a Roll", value="Get a Killstreak of 3", inline=True)
achievementsStreak.add_field(name="Menace", value="Get a Killstreak of 5", inline=True)
achievementsStreak.add_field(name="The White Death", value="Get a Killstreak of 10", inline=True)

achievementsVariety.add_field(name="Sniper Sniper", value="Snipe someone with the Sniper role", inline=True)
achievementsVariety.add_field(name="Double Kill", value="Snipe 2 people at once", inline=True)
achievementsVariety.add_field(name="Bouncing Bullet", value="Snipe 3 people at once", inline=True)
achievementsVariety.add_field(name="Be Polite", value="Snipe 5 different people", inline=True)
achievementsVariety.add_field(name="Be Efficient", value="Snipe 10 different people", inline=True)
achievementsVariety.add_field(name="Have a Plan to Kill Everyone You Meet", value="Snipe all Snipers", inline=True)

achievementsSniped.add_field(name="Welcome to the Afterlife", value="Get Sniped", inline=True)
achievementsSniped.add_field(name="Repeat Handshaker", value="Get Sniped 5 times", inline=True)
achievementsSniped.add_field(name="Cemetery Sightseer", value="Get Sniped 10 times", inline=True)

achievementsSpecial.add_field(name="Every Last One", value="Get all achievements from all categories")

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
              "\"The tide of war has turned.\" - Karl Fairburne",
              "\"After the trigger pull lies a blissful eternity.\" - Widowmaker"]
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

    if (snipeRoleId in member.roles):
        with open("snipeData.json", "r") as f:
            content = f.read().strip()
            if content:
                local = json.loads(content)
            else:
                local = {}

        ref = db.reference(f"/{guildId}")
        firebaseData = ref.get()
        if firebaseData is not None:
            local[str(guildId)] = firebaseData
        else:
            local.setdefault(str(guildId), {})

        memberData = local[str(guildId)].get(str(memberId), {})

        if "Killstreak" not in memberData or "Max Killstreak" not in memberData or "Achievements" not in memberData or "Sniped Users" not in memberData:
            if ("Killstreak" not in memberData):
                memberData["Killstreak"] = 0
                local[str(guildId)][str(memberId)] = memberData

                with open("snipeData.json", "w") as f:
                    json.dump(local, f, indent=4)

                ref.set(local[str(guildId)])
                await ctx.send("Sniper data updated: You can now have a Killstreak!")
            if ("Max Killstreak" not in memberData):
                memberData["Max Killstreak"] = 0
                local[str(guildId)][str(memberId)] = memberData

                with open("snipeData.json", "w") as f:
                    json.dump(local, f, indent=4)

                ref.set(local[str(guildId)])
                await ctx.send("Sniper data updated: You now have a Max Killstreak!")
            if ("Achievements" not in memberData):
                memberData["Achievements"] = []
                local[str(guildId)][str(memberId)] = memberData

                with open("snipeData.json", "w") as f:
                    json.dump(local, f, indent=4)
                
                ref.set(local[str(guildId)])
                await ctx.send("Sniper data updated: You can now start collecting achievements!")
            if ("Sniped Users" not in memberData):
                memberData["Sniped Users"] = []
                local[str(guildId)][str(memberId)] = memberData

                with open("snipeData.json", "w") as f:
                    json.dump(local, f, indent=4)
                
                ref.set(local[str(guildId)])
                await ctx.send("Sniper data updated: You can now track users you've sniped!")
        else:
            await ctx.send("You are already a Sniper, so get Sniping!")
    else:
        await member.add_role(sniperRole)

        with open("snipeData.json", "r") as f:
            content = f.read().strip()
            if content:
                local = json.loads(content)
            else:
                local = {}

        ref = db.reference(f"/{guildId}")
        firebaseData = ref.get()
        if firebaseData is not None:
            local[str(guildId)] = firebaseData
        else:
            local.setdefault(str(guildId), {})

        # Create entry if missing
        if str(memberId) not in local[str(guildId)]:
            local[str(guildId)][str(memberId)] = {
                "Snipes": 0,
                "Points": 0,
                "Times Sniped": 0,
                "Killstreak": 0,
                "Max Killstreak": 0,
                "Achievements": [],
                "Users Sniped": []
            }

        with open("snipeData.json", "w") as f:
            json.dump(local, f, indent=4)

        ref.set(local[str(guildId)])
        await ctx.send("You're a Sniper now!")
 
#Target - Snipe someone else (gain points, add 1 to Snipe count, increment target's times Sniped)
@slash_command(
    name="snipe",
    description="SnipeBot Commands",
    sub_cmd_name="target",
    sub_cmd_description="Snipe another member of the server!"
)
@slash_option(
    name="target_1",
    description="User you Sniped",
    required=True,
    opt_type=OptionType.USER,
    argument_name="user"
)
@slash_option(
    name="target_2",
    description="Second User you Sniped",
    required=False,
    opt_type=OptionType.USER,
    argument_name="user2"
)
@slash_option(
    name="target_3",
    description="Third User you Sniped",
    required=False,
    opt_type=OptionType.USER,
    argument_name="user3"
)
async def target(ctx: SlashContext, user: Member, user2: Member = None, user3: Member = None):
    snipeRoleId = next((role for role in ctx.guild.roles if role.name == "Sniper"), None)
    member = ctx.author
    memberId = ctx.author.id
    guild = ctx.guild
    guildId = ctx.guild_id
    userId = user.id
    user2Id = None
    user3Id = None
    if (user2 is not None):
        user2Id = user2.id
    if (user3 is not None):
        user3Id = user3.id
    await ctx.defer()

    sniperRole = guild.get_role(snipeRoleId)

    if (sniperRole not in member.roles):
        await ctx.send("Sorry, you're not a Sniper yet.")
        await ctx.send("Run \"/snipe register\" to become a Sniper and try this Snipe again!")
    else:
        if (user.id == memberId):
            return await ctx.send("You can't Snipe yourself!")
        if (user.id == ctx.bot.user.id):
            return await ctx.send("You can't Snipe the bot!")
        if (user2 is not None and user2.id == memberId):
            return await ctx.send("You can't Snipe yourself!")
        if (user2 is not None and user2.id == ctx.bot.user.id):
            return await ctx.send("You can't Snipe the bot!")
        if (user3 is not None and user3.id == memberId):
            return await ctx.send("You can't Snipe yourself!")
        if (user3 is not None and user3.id == ctx.bot.user.id):
            return await ctx.send("You can't Snipe the bot!")
        
        await ctx.send("You Sniped: "+user.mention+"!")
        if (user2 is not None):
            await ctx.send("You Sniped: "+user2.mention+"!")
        if (user3 is not None):
            await ctx.send("You Sniped: "+user3.mention+"!")

        ref = db.reference(f"/"+str(guildId))
        data = ref.get()
        with open("snipeData.json", "w") as f:
            json.dump({str(guildId): data}, f, indent=4)

        with open("snipeData.json", "r") as f:
            data = json.load(f)

        snipes = data[str(guildId)][str(memberId)]["Snipes"]
        usersSniped = data[str(guildId)][str(memberId)].get("Users Sniped", [])
        if (userId not in usersSniped):
            usersSniped.append(userId)
        killstreak = data[str(guildId)][str(memberId)].get("Killstreak", 0)
        snipes += 1
        if (user2 is not None):
            if (user2Id not in usersSniped):
                usersSniped.append(user2Id)
            snipes += 1
            killstreak += 1
        if (user3 is not None):
            if (user3Id not in usersSniped):
                usersSniped.append(user3Id)
            snipes += 1
            killstreak += 1
        killstreak += 1
        maxStreak = data[str(guildId)][str(memberId)].get("Max Killstreak", 0)
        if (killstreak > maxStreak):
            maxStreak = killstreak
        points = data[str(guildId)][str(memberId)]["Points"]
        userAchievements = data[str(guildId)][str(memberId)].get("Achievements", [])
        if (sniperRole in user.roles):
            if ("Sniper Sniper" not in userAchievements):
                userAchievements.append("Sniper Sniper")
                await ctx.send("You earned an achievement: Sniper Sniper!")
                points += 25
            points += 10
            otherTimesSniped = data[str(guildId)][str(userId)]["Times Sniped"]
            otherTimesSniped += 1
            data[str(guildId)][str(userId)]["Times Sniped"] = otherTimesSniped
            data[str(guildId)][str(userId)]["Killstreak"] = 0
            checkOtherSniped = checkOtherSnipedAchievements(otherTimesSniped)
            otherAchievements = data[str(guildId)][str(userId)].get("Achievements", [])
            if (checkOtherSniped >= 1 and "Welcome to the Afterlife" not in otherAchievements):
                otherAchievements.append("Welcome to the Afterlife")
                await ctx.send(user.mention+" earned an achievement: Welcome to the Afterlife!")
            elif (checkOtherSniped >= 2 and "Repeat Handshaker" not in otherAchievements):
                otherAchievements.append("Repeat Handshaker")
                await ctx.send(user.mention+" earned an achievement: Repeat Handshaker!")
            elif (checkOtherSniped >= 3 and "Cemetery Sightseer" not in otherAchievements):
                otherAchievements.append("Cemetery Sightseer")
                await ctx.send(user.mention+" earned an achievement: Cemetery Sightseer!")
            if (len(otherAchievements) == 18):
                otherAchievements.append("Every Last One")
                await ctx.send("Congratulations "+user.mention+"! You just got Every Last One!!")
                otherPoints = data[str(guildId)][str(userId)]["Points"]
                otherPoints += 500
                data[str(guildId)][str(userId)]["Points"] = otherPoints
            data[str(guildId)][str(userId)]["Achievements"] = otherAchievements
        else:
            points += 5
        if (user2 is not None):
            if (sniperRole in user2.roles):
                if ("Sniper Sniper" not in userAchievements):
                    userAchievements.append("Sniper Sniper")
                    await ctx.send("You earned an achievement: Sniper Sniper!")
                    points += 25
                points += 10
                otherTimesSniped = data[str(guildId)][str(user2Id)]["Times Sniped"]
                otherTimesSniped += 1
                data[str(guildId)][str(user2Id)]["Times Sniped"] = otherTimesSniped
                data[str(guildId)][str(user2Id)]["Killstreak"] = 0
                checkOtherSniped = checkOtherSnipedAchievements(otherTimesSniped)
                otherAchievements = data[str(guildId)][str(user2Id)].get("Achievements", [])
                if (checkOtherSniped >= 1 and "Welcome to the Afterlife" not in otherAchievements):
                    otherAchievements.append("Welcome to the Afterlife")
                    await ctx.send(user.mention+" earned an achievement: Welcome to the Afterlife!")
                elif (checkOtherSniped >= 2 and "Repeat Handshaker" not in otherAchievements):
                    otherAchievements.append("Repeat Handshaker")
                    await ctx.send(user.mention+" earned an achievement: Repeat Handshaker!")
                elif (checkOtherSniped >= 3 and "Cemetery Sightseer" not in otherAchievements):
                    otherAchievements.append("Cemetery Sightseer")
                    await ctx.send(user.mention+" earned an achievement: Cemetery Sightseer!")
                if (len(otherAchievements) == 18):
                    otherAchievements.append("Every Last One")
                    await ctx.send("Congratulations "+user2.mention+"! You just got Every Last One!!")
                    otherPoints = data[str(guildId)][str(user2Id)]["Points"]
                    otherPoints += 500
                    data[str(guildId)][str(user2Id)]["Points"] = otherPoints
                data[str(guildId)][str(user2Id)]["Achievements"] = otherAchievements
            else:
                points += 5
        if (user3 is not None):
            if (sniperRole in user3.roles):
                if ("Sniper Sniper" not in userAchievements):
                    userAchievements.append("Sniper Sniper")
                    await ctx.send("You earned an achievement: Sniper Sniper!")
                    points += 25
                points += 10
                otherTimesSniped = data[str(guildId)][str(user3Id)]["Times Sniped"]
                otherTimesSniped += 1
                data[str(guildId)][str(user3Id)]["Times Sniped"] = otherTimesSniped
                data[str(guildId)][str(user3Id)]["Killstreak"] = 0
                checkOtherSniped = checkOtherSnipedAchievements(otherTimesSniped)
                otherAchievements = data[str(guildId)][str(user3Id)].get("Achievements", [])
                if (checkOtherSniped >= 1 and "Welcome to the Afterlife" not in otherAchievements):
                    otherAchievements.append("Welcome to the Afterlife")
                    await ctx.send(user.mention+" earned an achievement: Welcome to the Afterlife!")
                elif (checkOtherSniped >= 2 and "Repeat Handshaker" not in otherAchievements):
                    otherAchievements.append("Repeat Handshaker")
                    await ctx.send(user.mention+" earned an achievement: Repeat Handshaker!")
                elif (checkOtherSniped >= 3 and "Cemetery Sightseer" not in otherAchievements):
                    otherAchievements.append("Cemetery Sightseer")
                    await ctx.send(user.mention+" earned an achievement: Cemetery Sightseer!")
                if (len(otherAchievements) == 18):
                    otherAchievements.append("Every Last One")
                    await ctx.send("Congratulations "+user3.mention+"! You just got Every Last One!!")
                    otherPoints = data[str(guildId)][str(user3Id)]["Points"]
                    otherPoints += 500
                    data[str(guildId)][str(user3Id)]["Points"] = otherPoints
                data[str(guildId)][str(user3Id)]["Achievements"] = otherAchievements
            else:
                points += 5

        data[str(guildId)][str(memberId)]["Snipes"] = snipes
        data[str(guildId)][str(memberId)]["Killstreak"] = killstreak
        data[str(guildId)][str(memberId)]["Max Killstreak"] = maxStreak
        #Achievements Time!
        checkTotal = checkTotalSnipeAchievements(snipes)
        if (checkTotal >= 1 and "Official" not in userAchievements):
            userAchievements.append("Official")
            await ctx.send("You earned an achievement: Official!")
            points += 25
        if (checkTotal >= 2 and "Earning Your Stripes" not in userAchievements):
            userAchievements.append("Earning Your Stripes")
            await ctx.send("You earned an achievement: Earning Your Stripes!")
            points += 50
        if (checkTotal >= 3 and "Contract Killer" not in userAchievements):
            userAchievements.append("Contract Killer")
            await ctx.send("You earned an achievement: Contract Killer!")
            points += 75
        if (checkTotal >= 4 and "Sentinel" not in userAchievements):
            userAchievements.append("Sentinel")
            await ctx.send("You earned an achievement: Sentinel")
            points += 100
        if (checkTotal >= 5 and "Sniping Legend" not in userAchievements):
            userAchievements.append("Sniping Legend")
            await ctx.send("You earned an achievement: Sniping Legend!")
            points += 125
            
        checkStreak = checkStreakAchievements(killstreak)
        if (checkStreak >= 1 and "Streak Activated" not in userAchievements):
            userAchievements.append("Streak Activated")
            await ctx.send("You earned an achievement: Streak Activated!")
            points += 25
        if (checkStreak >= 2 and "On a Roll" not in userAchievements):
            userAchievements.append("On a Roll")
            await ctx.send("You earned an achievement: On a Roll!")
            points += 50
        if (checkStreak >= 3 and "Menace" not in userAchievements):
            userAchievements.append("Menace")
            await ctx.send("You earned an achievement: Menace!")
            points += 100
        if (checkStreak >= 4 and "The White Death" not in userAchievements):
            userAchievements.append("The White Death")
            await ctx.send("You earned an achievement: The White Death!")
            points += 200

        if (user2 is not None and "Double Kill" not in userAchievements):
            userAchievements.append("Double Kill")
            await ctx.send("You earned an achievement: Double Kill!")
            points += 25
        if (user3 is not None and "Bouncing Bullet" not in userAchievements):
            userAchievements.append("Bouncing Bullet")
            await ctx.send("You earned an achievement: Bouncing Bullet!")
            points += 75
        if (len(usersSniped) >= 5 and "Be Polite" not in userAchievements):
            userAchievements.append("Be Polite")
            await ctx.send("You earned an achievement: Be Polite!")
            points += 50
        if (len(usersSniped) >= 10 and "Be Efficient" not in userAchievements):
            userAchievements.append("Be Efficient")
            await ctx.send("You earned an achievement: Be Efficient!")
            points += 100
        if (len(usersSniped) + 1 == len(data[str(guildId)]) and "Have a Plan to Kill Everyone You Meet" not in userAchievements and len(usersSniped) >= 10):
            userAchievements.append("Have a Plan to Kill Everyone You Meet")
            await ctx.send("You earned an achievement: Have a Plan to Kill Everyone You Meet!")
            points += 150
        
        if (len(userAchievements) == 18):
            userAchievements.append("Every Last One")
            await ctx.send("Congratulations! You just got Every Last One!!!")
            points += 500
        data[str(guildId)][str(memberId)]["Users Sniped"] = usersSniped
        data[str(guildId)][str(memberId)]["Points"] = points
        data[str(guildId)][str(memberId)]["Achievements"] = userAchievements
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
        SlashCommandChoice(name="Times Sniped", value="Times Sniped"),
        SlashCommandChoice(name="Killstreak", value="Killstreak"),
        SlashCommandChoice(name="Max Killstreak", value="Max Killstreak")
    ]
)
async def leaderboard(ctx: SlashContext, leader: str):
    await ctx.defer()
    guildId = ctx.guild.id
    ref = db.reference(f"/"+str(guildId))
    data = ref.get()
    with open("snipeData.json", "w") as f:
        json.dump({str(guildId): data}, f, indent=4)

    with open("snipeData.json", "r") as f:
        data = json.load(f)

    guildData = data[str(ctx.guild.id)]
    leaderData = {}
    for userid in guildData:
        memberName = await ctx.guild.fetch_member(int(userid))
        memberName = memberName.display_name
        leaderData[memberName] = guildData[userid].get(leader, 0)
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
            inline = True
        )
    await ctx.send(embeds=board)

@slash_command(
    name="snipe",
    description="SnipeBot Commands",
    group_name="achievement",
    group_description="Achievement-related Commands",
    sub_cmd_name="list",
    sub_cmd_description="List of all Achievements, by category (or all)"
)
@slash_option(
    name="category",
    opt_type=OptionType.STRING,
    description="Category to view (or all)",
    argument_name="category",
    required=False,
    choices = [
        SlashCommandChoice(name="Total Snipes", value="Total"),
        SlashCommandChoice(name="Killstreak", value="Streak"),
        SlashCommandChoice(name="Variety", value="Variety"),
        SlashCommandChoice(name="Getting Sniped", value="Sniped"),
        SlashCommandChoice(name="Special", value="Special")
    ]
)
async def achievementList(ctx: SlashContext, category: str = "All"):
    await ctx.defer()
    #TODO: Make it so that if the user selects all, bot response is paged so that the user isn't flooded

    #await ctx.send(embeds=achievements)
    if (category == "Total"):
        return await ctx.send(embed=achievementsTotal)
    elif (category == "Streak"):
        return await ctx.send(embed=achievementsStreak)
    elif (category == "Variety"):
        return await ctx.send(embed=achievementsVariety)
    elif (category == "Sniped"):
        return await ctx.send(embed=achievementsSniped)
    elif (category == "Special"):
        return await ctx.send(embed =achievementsSpecial)
    else:
        embeds=[achievementsTotal, achievementsStreak, achievementsVariety, achievementsSniped, achievementsSpecial]
        paginator = Paginator.create_from_embeds(bot, *embeds)
        return await paginator.send(ctx)

@slash_command(
    name="snipe",
    description="SnipeBot Commands",
    group_name="achievement",
    group_description="Achievement-related Commands",
    sub_cmd_name="personal",
    sub_cmd_description="Your personal list of Achievements"
)
@slash_option(
    name="category",
    opt_type=OptionType.STRING,
    description="Category to view (or all)",
    argument_name="category",
    required=False,
    choices = [
        SlashCommandChoice(name="Total Snipes", value="Total"),
        SlashCommandChoice(name="Killstreak", value="Streak"),
        SlashCommandChoice(name="Variety", value="Variety"),
        SlashCommandChoice(name="Getting Sniped", value="Sniped"),
        SlashCommandChoice(name="Special", value="Special")
    ]
)
async def personalAchievements(ctx: SlashContext, category: str = "All"):
    member = ctx.author
    memberId = ctx.author.id
    guild = ctx.guild
    guildId = ctx.guild_id

    snipeRoleId = next((role for role in ctx.guild.roles if role.name == "Sniper"), None)
    sniperRole = guild.get_role(snipeRoleId)

    if (sniperRole not in member.roles):
        await ctx.send("Sorry, you're not a Sniper yet.")
        return await ctx.send("Run \"/snipe register\" to become a Sniper and try this command again!")
    
    ref = db.reference(f"/"+str(guildId))
    data = ref.get()
    with open("snipeData.json", "w") as f:
        json.dump({str(guildId): data}, f, indent=4)

    with open("snipeData.json", "r") as f:
        data = json.load(f)

    ments = data[str(guildId)][str(memberId)].get("Achievements", [])

    personalTotal = Embed(
        title="Your Achievements - Total Snipes",
        color=0xB3A369
    )
    personalStreak = Embed(
        title="Your Achievements - Killstreak",
        color=0xB3A369
    )
    personalVariety = Embed(
        title="Your Achievements - Variety",
        color=0xB3A369
    )
    personalSniped = Embed(
        title="Your Achievements - Times Sniped",
        color=0xB3A369
    )
    personalSpecial = Embed(
        title="Your Achievements - Special"
    )
    
    if ("Official" in ments):
        personalTotal.add_field(name="Official", value="Get your first Snipe!", inline=True)
    if ("Earning Your Stripes" in ments):
        personalTotal.add_field(name="Earning Your Stripes", value="Get 5 Total Snipes", inline=True)
    if ("Contract Killer" in ments):
        personalTotal.add_field(name="Contract Killer", value="Get 10 Total Snipes", inline=True)
    if ("Sentinel" in ments):
        personalTotal.add_field(name="Sentinel", value="Get 25 Total Snipes", inline=True)
    if ("Sniping Legend" in ments):
        personalTotal.add_field(name="Sniping Legend", value="Get 50 Total Snipes", inline=True)
    if ("Streak Activated" in ments):
        personalStreak.add_field(name="Streak Activated", value="Get a Killstreak of 2", inline=True)
    if ("On a Roll" in ments):
        personalStreak.add_field(name="On a Roll", value="Get a Killstreak of 3", inline=True)
    if ("Menace" in ments):
        personalStreak.add_field(name="Menace", value="Get a Killstreak of 5", inline=True)
    if ("The White Death" in ments):
        personalStreak.add_field(name="The White Death", value="Get a Killstreak of 10", inline=True)
    if ("Sniper Sniper" in ments):
        personalVariety.add_field(name="Sniper Sniper", value="Snipe someone with the Sniper role", inline=True)
    if ("Double Kill" in ments):
        personalVariety.add_field("Double Kill", value="Snipe 2 people at once", inline=True)
    if ("Bouncing Bullet" in ments):
        personalVariety.add_field(name="Bouncing Bullet", value="Snipe 3 people at once", inline=True)
    if ("Be Polite" in ments):
        personalVariety.add_field(name="Be Polite", value="Snipe 5 different people", inline=True)
    if ("Be Efficient" in ments):
        personalVariety.add_field(name="Be Efficient", value="Snipe 10 different people", inline=True)
    if ("Have a Plan to Kill Everyone You Meet" in ments):
        personalVariety.add_field(name="Have a Plan to Kill Everyone You Meet", value="Snipe all Snipers", inline=True)
    if ("Welcome to the Afterlife" in ments):
        personalSniped.add_field(name="Welcome to the Afterlife", value="Get Sniped", inline=True)
    if ("Repeat Handshaker" in ments):
        personalSniped.add_field(name="Repeat Handshaker", value="Get Sniped 5 times", inline=True)
    if ("Cemetery Sightseer" in ments):
        personalSniped.add_field(name="Cemetery Sightseer", value="Get Sniped 10 times", inline=True)
    if ("Every Last One" in ments):
        personalSpecial.add_field(name="Every Last One", value="Get all achievements from all categories")
    
    if (category == "Total"):
        return await ctx.send(embed=personalTotal)
    if (category == "Streak"):
        return await ctx.send(embed=personalStreak)
    if (category == "Variety"):
        return await ctx.send(embed=personalVariety)
    if (category == "Sniped"):
        return await ctx.send(embed=personalSniped)
    if (category == "Special"):
        return await ctx.send(embed=personalSpecial)
    embeds=[personalTotal, personalStreak, personalVariety, personalSniped, personalSpecial]
    paginator = Paginator.create_from_embeds(bot, *embeds)
    return await paginator.send(ctx)

def checkTotalSnipeAchievements(snipes: int):
    if (snipes >= 1 and snipes < 5):
        return 1
    if (snipes >= 5 and snipes < 10):
        return 2
    if (snipes >= 10 and snipes < 25):
        return 3
    if (snipes >= 25 and snipes < 50):
        return 4
    return 5

def checkStreakAchievements(streak: int):
    if (streak == 2):
        return 1
    if (streak == 3):
        return 2
    if (streak == 5):
        return 3
    if (streak == 10):
        return 4
    return 0

def checkOtherSnipedAchievements(sniped: int):
    if (sniped >= 1 and sniped < 5):
        return 1
    if (sniped >= 5 and sniped < 10):
        return 2
    if (sniped >= 10):
        return 3
bot.start(TOKEN)