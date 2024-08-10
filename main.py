import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event

async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count += 1
    print(f" - ShatGPT is in " + str(guild_count) + " guilds.")


@bot.command()

async def hello(ctx):
    msg = f'Hi {ctx.author.mention}'
    await ctx.send(msg)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"I'm sorry {ctx.author.mention}, I'm afraid I can't do that. The command you entered is not recognized.")

bot.run(DISCORD_TOKEN)