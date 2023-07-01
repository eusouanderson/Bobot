import discord
from discord.ext import commands
import api_youtube
import requests
import json
import SECRET_KEY as SECRET_KEY
import openai

intents = discord.Intents.default()
intents.typing = False
intents.presences = False


bot = commands.Bot(command_prefix='', intents=intents)
openai.api_key = SECRET_KEY.GPT_KEY

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')



@bot.event
async def on_message(message):
    # Verificar se a mensagem não foi enviada pelo bot para evitar loops
    if message.author.bot:
        return
    '''
    try:
        # Enviar a mensagem para a API do ChatGPT
        response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=message.content,
        temperature=0.7,
        max_tokens=50,
        n=1,
        stop=None,
    )
        # Extrair a resposta da API do ChatGPT
        reply = response.choices[0].text.strip()
    except Exception:
        # Enviar a resposta para o canal do Discord
        await message.channel.send('Desculpe acabou a cota free de usar API da IA o Papai B.O.B precisa pagar agora $$$')
        
    finally:
        await message.channel.send(reply)


    # Continuar processando comandos do bot
    await bot.process_commands(message)'''

    @bot.command()
    async def Ola(ctx):
        await ctx.send('Olá!, Tudo bem')
        
    @bot.command()
    async def ping(ctx):
        await ctx.send('Pong!')


    @bot.command()
    async def youtube(ctx, arg):
        """Ex. youtube musica desejada"""
        await ctx.send(f'{api_youtube.search_videos({arg})}')



    @bot.command()
    async def BOT(ctx, *, arg):
        '''Use BOT para conversar com a IA '''    
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