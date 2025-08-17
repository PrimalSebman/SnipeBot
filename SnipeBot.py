# Imports
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # Needed to read messages
intents.members = True          # Needed if you want member info

bot = commands.Bot(command_prefix="/snipe ", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='quote', help="Gives a random quote from a video game sniper.")
async def writeQuote(ctx):
    sniperQuotes = ["\"You're all a bunch of no-hopers.\" - TF2 Sniper",
                    "\"Acceptance of mediocrity is the first step towards failure.\" - Jaimini Kalimohan \"Kali\" Shah",
                    "\"The tide of war has turned.\" - Karl Fairburne",
                    "\"Do you know what an artist and a sniper have in common? Details.\" - Timur \"Glaz\" Glazkov"]
    
    response = random.choice(sniperQuotes)
    await ctx.send(response)
    
bot.run(TOKEN)