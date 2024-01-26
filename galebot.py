import os
import discord
from discord.ext import commands
import datetime
import random
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up Discord intents to enable the message content intent
intents = discord.Intents.default()
intents.message_content = True

# Create a Discord bot with command prefix '!' and specified intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Define the file where brain entries are stored
brain_file = 'brain.txt'
quotes_file = 'startrek_quotes.json'

# Load Star Trek quotes from JSON file
def load_star_trek_quotes():
    try:
        with open(quotes_file, 'r', encoding='utf-8') as file:
            star_trek_quotes = json.load(file)
        return star_trek_quotes
    except FileNotFoundError:
        # If the file doesn't exist, return an empty list
        return []

# Ensure that this function is defined before it's called in the code.
star_trek_quotes = load_star_trek_quotes()

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
        bot_nickname = message.guild.me.display_name.lower() if message.guild and message.guild.me.display_name else None
        
        mentioned = bot.user.mentioned_in(message)
        starts_with_username = message.content.lower().startswith(bot_name)
        starts_with_display_name = message.content.lower().startswith(bot_nickname) if bot_nickname else False
        
        # Check if the bot's name or nickname is mentioned, or if the message starts with them
        if bot_name in message.content.lower() or (bot_nickname and (bot_nickname in message.content.lower() or starts_with_display_name)) or starts_with_username or mentioned:
            response = get_random_entry_from_brain(message.guild)
            await message.channel.send(response)

    await bot.process_commands(message)

# Command to display the current date
@bot.command(name='date')
async def show_current_date(ctx):
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    await ctx.send(f'The current date is: {current_date}')

# Command to get a random Star Trek quote
@bot.command(name='trekquote')
async def get_trek_quote(ctx):
    try:
        random_quote = random.choice(star_trek_quotes)
        quote_text = random_quote['quote']
        author = random_quote['author']
        await ctx.send(f'Star Trek Quote by {author}: {quote_text}')
    except Exception as e:
        await ctx.send(f'Error fetching Star Trek quote: {e}')

# Check function to verify if the command author is the server owner
def is_owner():
    async def predicate(ctx):
        return ctx.guild and ctx.author.id == ctx.guild.owner_id
    return commands.check(predicate)

# Command to change the bot's nickname (only accessible by the server owner)
@bot.command(name='nickname')
@is_owner()
async def change_bot_nickname(ctx, new_nickname: str):
    try:
        await ctx.guild.me.edit(nick=new_nickname)
        await ctx.send(f'Nickname changed to: {new_nickname}')
    except Exception as e:
        await ctx.send(f'Error changing nickname: {e}')

# Run the bot
bot.run(TOKEN)
