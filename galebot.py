import os
import discord
from discord.ext import commands
import datetime
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Function to get the current date and time
def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Set up Discord intents to enable the message content intent
intents = discord.Intents.default()
intents.message_content = True  

# Create a Discord bot with command prefix '!' and specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Define the file where brain entries are stored
brain_file = 'brain.txt'

# Event handler for bot's readiness
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')
    print('------')

# Function to get a random entry from the brain file
def get_random_entry_from_brain(guild):
    try:
        with open(brain_file, 'r', encoding='utf-8') as file:
            entries = file.readlines()
            random_entry = random.choice(entries).strip()

            return random_entry
    except Exception as e:
        print(f'Error reading brain.txt: {e}')
        return 'Error: Unable to fetch response'

# Function to log messages to the brain.txt file
async def log_message(message):
    with open(brain_file, 'a', encoding='utf-8') as file:
        print(f"Logging message: {message.content}")
        content = message.content
        for mention in message.mentions:
            content = content.replace(mention.mention, '%USER%')
        file.write(f"{content}\n")

# Event handler for responding when the bot's name is mentioned
@bot.event
async def on_message(message):
    if message.author != bot.user:  # Avoid logging bot's own messages
        await log_message(message)
        bot_name = bot.user.name.lower()
        mentioned = bot.user.mentioned_in(message)
        starts_with_username = message.content.lower().startswith(bot.user.name.lower())
        starts_with_display_name = message.content.lower().startswith(bot.user.display_name.lower())
        # Check if the bot's name is mentioned or the message starts with the bot's name
        if bot_name in message.content.lower() or starts_with_display_name or starts_with_username or mentioned:
            response = get_random_entry_from_brain(message.guild)
            await message.channel.send(response)
    await bot.process_commands(message)

# Command to display the current date
@bot.command(name='date')
async def show_current_date(ctx):
    current_date = get_current_date()
    await ctx.send(f'The current date is: {current_date}')

# Check function to verify if the command author is the server owner
def is_owner():
    async def predicate(ctx):
        return ctx.guild and ctx.author.id == ctx.guild.owner_id
    return commands.check(predicate)

# Command to change the bot's nickname (only accessible by the server owner)
@bot.command(name='nickname')
@is_owner()
async def change_bot_nickname(ctx, *, new_nickname):
    try:
        await ctx.guild.me.edit(nick=new_nickname)
        await ctx.send(f'Nickname changed to: {new_nickname}')
    except Exception as e:
        await ctx.send(f'Error changing nickname: {e}')

# Run the bot
bot.run(TOKEN)
