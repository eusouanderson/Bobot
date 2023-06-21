import discord
from discord.ext import commands
import api_youtube
import requests
import json
import SECRET_KEY

intents = discord.Intents.default()
intents.typing = False
intents.presences = False


bot = commands.Bot(command_prefix='', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')



@bot.event
async def on_message(message):
    
    if message.author != bot.user:

        await message.channel.send('...')

    await bot.process_commands(message)

    
    
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')


@bot.command()
async def youtube(ctx, arg):
    """Ex. !youtube musica desejada"""
    await ctx.send(f'{api_youtube.search_videos({arg})}')



@bot.command()
async def BOT(ctx, *, arg):
    '''Use !chat para conversar com a IA '''    
    headers = {"Authorization": f"Bearer {SECRET_KEY.GPT_KEY}" , "content-type": "Application/json"}

    link = "https://api.openai.com/v1/chat/completions"

    id_modelo = "gpt-3.5-turbo"
    resp = arg
    
    body_mensagem = {
        "model": id_modelo,
        "messages": [{"role": "assistant", "content": "Em portugues pt/BR "}, {"role": "user", "content": f":robot: {resp}"}]
    }

    Body_mensagem = json.dumps(body_mensagem)


    Requisição = requests.post(link, headers=headers, data=Body_mensagem)

    Resposta = Requisição.json()

    Mensagem = Resposta ["choices"][0]["message"]["content"]

    await ctx.send(f'{Mensagem}')

    return Mensagem


bot.run(SECRET_KEY.BOT_TOKEN)