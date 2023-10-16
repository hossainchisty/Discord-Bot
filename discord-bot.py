import os
import facts
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.command(name='hello', help='Responds with a hello message')
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')


@bot.command(name='ping', help='Responds with Pong!')
async def ping(ctx):
    await ctx.send('Pong!')

    
@bot.command(name='fact', help='Returns a random fact')
async def fact(ctx):
    random_fact = random.choice(facts.facts)
    await ctx.send(random_fact)


# Dictionary to store active polls
active_polls = {}

@bot.command(name='createpoll', help='Creates a new poll. Usage: !createpoll <question>;<option1>;<option2>;<option3>...')
async def create_poll(ctx, *, args):
    try:
        question, *options = args.split(';')
        question = question.strip()
        poll_options = [option.strip() for option in options]  
    except ValueError:
        await ctx.send("Invalid format. Usage: !createpoll <question>;<option1>;<option2>;<option3>...")
        return

    if len(poll_options) < 2:
        await ctx.send("A poll must have at least two options.")
        return

    poll = {'question': question, 'options': poll_options, 'votes': [0] * len(poll_options)}
    active_polls[ctx.channel.id] = poll
    await ctx.send("Poll created! To vote, use /vote <option>.")


@bot.command(name='vote', help='Votes for an option in the active poll. Usage: /vote <option>')
async def vote(ctx, *, option):
    if ctx.channel.id not in active_polls:
        await ctx.send("There is no active poll in this channel.")
        return

    poll = active_polls[ctx.channel.id]

    if option in poll['options']:
        index = poll['options'].index(option)
        poll['votes'][index] += 1
        await ctx.send(f"Your vote for '{option}' has been recorded.")
    else:
        await ctx.send("Invalid option. Please vote for one of the available options.")


@bot.command(name='pollresults', help='Displays the results of the active poll.')
async def poll_results(ctx):
    if ctx.channel.id not in active_polls:
        await ctx.send("There is no active poll in this channel.")
        return

    poll = active_polls[ctx.channel.id]
    question = poll['question']
    options = poll['options']
    votes = poll['votes']

    results = "\n".join([f"{option}: {vote} vote(s)" for option, vote in zip(options, votes)])
    await ctx.send(f"**Poll Question:** {question}\n**Results:**\n{results}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Prevent the bot from responding to its own messages

    # await message.reply('How can i help you?')
    await bot.process_commands(message)
    print(message.content)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

bot.run(DISCORD_TOKEN)
