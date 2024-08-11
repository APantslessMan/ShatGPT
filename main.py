import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import openai
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PERSONALITY = ("You are ShatGPT. you are a grumpy, surly assistant who answers questions with a neutral, irritated "
               "attitude and uses profanity alot but not to insult others. maintain this tone throughout the "
               "conversation. if asked for code examples, respond to use google.")


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = os.getenv("OPENAI_BASE_URL")
# Define the parameters for the chat completion
response = openai.chat.completions.create(
    model="openchat/openchat-7b:free",  # or "gpt-4" if you're using GPT-4
    messages=[
        {"role": "system", "content": PERSONALITY},
        {"role": "user", "content": "This is a test"}
    ]
)
assistant_reply = response.choices[0].message.content
print(assistant_reply)


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
        await ctx.send(f"I'm sorry {ctx.author.mention}, I'm afraid I can't do that. The command you entered is not "
                       f"recognized.")


@bot.command()
async def ask(ctx, *, question: str):
    try:
        print("asking question")
        ask_response = openai.chat.completions.create(
            model="openchat/openchat-7b:free",
            messages=[
                {"role": "system",
                 "content": PERSONALITY},
                {"role": "user", "content": question }
            ]
        )
        ask_reply = ask_response.choices[0].message.content
        msg = f'Hi {ctx.author.mention}, {ask_reply}'
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f'an error occured: {e}')
        print(f'error occured: {e}')


bot.run(DISCORD_TOKEN)
