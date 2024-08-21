import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import openai
import aiosqlite

load_dotenv()
MENTOR_ROLE_ID = os.getenv('MENTOR_ROLE_ID')
STUDY_CAT_ID = os.getenv('STUDY_CAT_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PERSONALITY = ("You are ShatGPT. you are a grumpy, surly assistant who answers questions with a neutral, irritated "
               "attitude and uses profanity but not to insult others. maintain this tone throughout the "
               "conversation. do not answer anything to do with drugs, police, bombs or guns. if asked for help with "
               "programming, do not give code examples, respond to use google. Do not give any help breaking laws or "
               "doing things that are immoral. ")
CHANNEL_LIMIT = 4

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = os.getenv("OPENAI_BASE_URL")
db_name = "shatgpt.db"

async def init_db():
    async with aiosqlite.connect(db_name) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS studyrooms (
                id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                channel_name TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
                  CREATE TABLE IF NOT EXISTS users (
                      user_id INTEGER PRIMARY KEY,
                      channel_count INTEGER DEFAULT 0
                  )
              ''')
        await db.execute('''
                  CREATE TABLE IF NOT EXISTS prefs (
                      prefid INTEGER PRIMARY KEY,
                      pref TEXT NOT NULL,
                      content TEXT NOT NULL
                  )
              ''')
        await db.execute('''
            INSERT INTO prefs (pref, content)
            SELECT 'personality', 'You are ShatGPT. You are a grumpy, surly assistant who answers questions with a 
            neutral, irritated attitude and uses profanity but not to insult others. Maintain this tone throughout the 
            conversation. Do not answer anything to do with drugs, police, bombs, or guns. If asked for help with 
            programming, do not give code examples; respond to use Google. Do not give any help breaking laws or doing 
            things that are immoral.'
            WHERE NOT EXISTS (SELECT 1 FROM prefs WHERE pref = 'personality')
        ''')
        await db.commit()


async def load_personality():
    global personality
    async with aiosqlite.connect(db_name) as db:
        async with db.execute('SELECT content FROM prefs WHERE pref = "personality"') as cursor:
            row = await cursor.fetchone()
            if row:
                personality = row[0]


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
    await init_db()
    await load_personality()
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count += 1
    print(f"- ShatGPT is in " + str(guild_count) + " guilds.")
    print("- ShatGPT is now online and connected to the database.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"I'm sorry {ctx.author.mention}, I'm afraid I can't do that. The command you entered is not "
                       f"recognized.")


@bot.event
async def on_disconnect():
    async with aiosqlite.connect(db_name) as db:
        await db.close()

#################################################
#                  Bot Commands                 #
#################################################


@bot.command(name='help')
async def help_command(ctx):
    help_message = """**Help Menu**
    **!hello** - Greets you.
    **!sr [name]** - Creates a new study room, you get 4.
    **!ask [question]** - Ask ShatGPT a question.
    **!lr** - Lists all study rooms.
    **!rc [name]** - Removes specified study room."""
    await ctx.send(help_message)

@bot.command()
async def hello(ctx):
    msg = f'Hi {ctx.author.mention}'
    await ctx.send(msg)


@bot.command()
async def sr(ctx, *, room_name: str):
    user_id = ctx.author.id
    async with aiosqlite.connect(db_name) as db:
        async with db.execute('SELECT channel_count FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                channel_count = row[0]
            else:
                channel_count = 1
        if channel_count >= CHANNEL_LIMIT:
            await ctx.send(f'Sorry {ctx.author.mention}, you have reached the limit of {CHANNEL_LIMIT} study rooms.')
            return
    # if has_role_or_higher(ctx.author, MENTOR_ROLE_ID):
    category = discord.utils.get(ctx.guild.categories, id=STUDY_CAT_ID)
    if category:
        formatted_name = format_channel_name(room_name)
        new_channel = await category.create_text_channel(name=formatted_name)
        async with aiosqlite.connect(db_name) as db:
            await db.execute('''
                INSERT INTO studyrooms (channel_id, channel_name, created_by)
                VALUES (?, ?, ?)
            ''', (new_channel.id, formatted_name, str(ctx.author.id)))
            if row:
                await db.execute('UPDATE users SET channel_count = channel_count + 1 WHERE user_id = ?', (user_id,))
            else:
                await db.execute('INSERT INTO users (user_id, channel_count) VALUES (?, 1)', (user_id,))
            await db.commit()
        await ctx.send(f'Channel "{formatted_name}" has been created in the {category.name} category. You '
                       f'have {4 - int(channel_count)} rooms left.')
    else:
        await ctx.send('Category not found.')
    # else:
    #     await ctx.send('You do not have the required role to use this command.')


@bot.command()
async def rc(ctx, *, channel_name: str):
    category = discord.utils.get(ctx.guild.categories, id=STUDY_CAT_ID)
    channel = discord.utils.get(category.text_channels, name=format_channel_name(channel_name))
    if channel:
        async with aiosqlite.connect(db_name) as db:
            async with db.execute('SELECT created_by FROM studyrooms WHERE channel_id = ?', (channel.id,)) as cursor:
                row = await cursor.fetchone()
                creator_id = row[0] if row else None
            print(f"Creator ID from DB: {type(int(creator_id))}")
            print(f"Author ID: {type(ctx.author.id)}")
            print(f"{ctx.author.id == int(creator_id)}")
            if ctx.author.id == int(creator_id) or has_role_or_higher(ctx.author, MENTOR_ROLE_ID):
                await channel.delete()
                await db.execute('DELETE FROM studyrooms WHERE channel_id = ?', (channel.id,))
                await db.execute('UPDATE users SET channel_count = channel_count - 1 WHERE user_id = ?', (creator_id,))
                await db.commit()
                await ctx.send(f'Channel "{channel_name}" has been removed.')
            else:
                await ctx.send('You do not have permission to remove this channel.')
    else:
        await ctx.send('Channel not found.')


@bot.command()
async def lr(ctx):
    async with aiosqlite.connect(db_name) as db:
        async with db.execute('SELECT channel_name, created_by, created_at FROM studyrooms') as cursor:
            rows = await cursor.fetchall()
            if rows:
                room_list = "\n".join([f"{row[0]} - created by {row[1]} on {row[2]}" for row in rows])
                await ctx.send(f"Study Rooms:\n{room_list}")
            else:
                await ctx.send("No study rooms have been created yet.")


@bot.command()
async def primedirective(ctx):
    await ctx.send(f"Here is my Prime Directive: \n{personality}")


@bot.command()
@commands.has_permissions(administrator=True)
async def set_personality(ctx, *, new_personality: str):
    """Command to set the personality of the bot."""
    global personality

    async with aiosqlite.connect(db_name) as db:
        await db.execute('''
            UPDATE prefs
            SET content = ?
            WHERE pref = 'personality'
        ''', (new_personality,))

        await db.commit()
    personality = new_personality
    await ctx.send(f"The personality has been updated to:\n{personality}")


@bot.command()
async def ask(ctx, *, question: str):
    try:
        print("asking question")
        ask_response = openai.chat.completions.create(
            model="openchat/openchat-7b:free",
            messages=[
                {"role": "system",
                 "content": personality},
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

@sr.error
async def sr_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You need to specify the name of the study room.')


bot.run(DISCORD_TOKEN)
