import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import openai
load_dotenv()
MENTOR_ROLE_ID = 1271690917203677194
STUDY_CAT_ID = 1271981288462487695
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PERSONALITY = ("You are ShatGPT. you are a grumpy, surly assistant who answers questions with a neutral, irritated "
               "attitude and uses profanity alot but not to insult others. maintain this tone throughout the "
               "conversation. do not answer anything to do with drugs, police, bombs or guns. if asked for code "
               "examples, respond to use google. Do not give any help breaking laws or "
               "doing things that ar immoral. ")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = os.getenv("OPENAI_BASE_URL")
# Define the parameters for the chat completion

#################################################
#               AI Response example             #
#################################################

# response = openai.chat.completions.create(
#     model="openchat/openchat-7b:free",  # or "gpt-4" if you're using GPT-4
#     messages=[
#         {"role": "system", "content": PERSONALITY},
#         {"role": "user", "content": "This is a test"}
#     ]
# )
# assistant_reply = response.choices[0].message.content
# print(assistant_reply)

#################################################
#               Utility Functions               #
#################################################


def has_role_or_higher(member, role_id):
    role = discord.utils.get(member.guild.roles, id=role_id)
    return role in member.roles or any(r.position > role.position for r in member.roles)


def format_channel_name(name):
    return name.lower().replace(' ', '-')


#################################################
#                   Bot Events                  #
#################################################


@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count += 1
    print(f" - ShatGPT is in " + str(guild_count) + " guilds.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"I'm sorry {ctx.author.mention}, I'm afraid I can't do that. The command you entered is not "
                       f"recognized.")

#################################################
#                  Bot Commands                 #
#################################################


@bot.command()
async def hello(ctx):
    msg = f'Hi {ctx.author.mention}'
    await ctx.send(msg)


@bot.command()
async def studyroom(ctx, *, room_name: str):
    if has_role_or_higher(ctx.author, MENTOR_ROLE_ID):
        category = discord.utils.get(ctx.guild.categories, id=STUDY_CAT_ID)
        if category:
            formatted_name = format_channel_name(room_name)
            new_channel = await category.create_text_channel(name=formatted_name)
            await ctx.send(f'Channel "{formatted_name}" has been created in the {category.name} category.')
        else:
            await ctx.send('Category not found.')
    else:
        await ctx.send('You do not have the required role to use this command.')


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


#################################################
#                  Error Handling               #
#################################################

@studyroom.error
async def studyroom_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You need to specify the name of the study room.')


bot.run(DISCORD_TOKEN)
