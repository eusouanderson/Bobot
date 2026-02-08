from typing import Optional

import aiohttp
import discord
from discord.ext import commands

from bobot.ai.factory import create_llm_service
from bobot.ai.prompts import (
    build_ask_prompt,
    build_code_prompt,
    build_debug_prompt,
    build_docs_prompt,
)
from bobot.config import BOT_TOKEN, ID_CANAL
from bobot.domain.exceptions import ExternalServiceError, RateLimitError
from bobot.urls import C, CSHARP, URL_CSS, URL_HTML, URL_JAVASCRIPT, URL_MONGO, URL_PYTHON
from bobot.utils.logging import configure_logging, get_logger
from bobot.utils.text import chunk_text

# Configuração das intenções do bot
intents = discord.Intents.default()
intents.messages = True
intents.typing = True
intents.reactions = True
intents.message_content = True

configure_logging()
logger = get_logger(__name__)

bot = commands.Bot(command_prefix="!", intents=intents)
llm_service = create_llm_service()


@bot.event
async def on_ready():
    logger.info("We have logged in as %s", bot.user)


@bot.command(name="comandos")
async def help_commands(ctx):
    embed = discord.Embed(
        title="📚 Comandos Disponíveis",
        description="Veja abaixo tudo que o B.O.BOT pode fazer:",
        color=0x00FF00,
    )
    embed.add_field(name="👋 Saudações", value="`!ola`", inline=False)
    embed.add_field(
        name="🧮 Cálculos",
        value=(
            "`!calc soma a b`\n"
            "`!calc sub a b`\n"
            "`!calc mult a b`\n"
            "`!calc div a b`"
        ),
        inline=False,
    )
    embed.add_field(
        name="📖 Documentação",
        value=(
            "`!python`, `!javascript`/`!js`, `!html`, `!css`, `!mongo`/`!mongodb`, "
            "`!csharp`/`!c#`, `!c`"
        ),
        inline=False,
    )
    embed.add_field(
        name="🧩 Snippets",
        value=(
            "`!snippet <linguagem> [termo]`\n"
            "Fonte: https://www.30secondsofcode.org/"
        ),
        inline=False,
    )
    embed.add_field(
        name="🔎 Pesquisa",
        value=(
            "`!pesquisa <consulta>`\n"
            "`!youtube <consulta>`"
        ),
        inline=False,
    )
    embed.add_field(
        name="🧪 Execução",
        value="`!run <linguagem> <código>`",
        inline=False,
    )
    embed.add_field(
        name="✨ IA Local",
        value=(
            "`!pergunta <texto>`\n"
            "`!codigo <linguagem> <tema>`\n"
            "`!debug <erro>`\n"
            "`!docs <tecnologia>`\n"
            "`!status`"
        ),
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.command(name="versão")
async def version(ctx):
    if ctx.channel.id == int(ID_CANAL):
        await ctx.send("Versão: 1.0.5")
    else:
        logger.info(
            "Comando \"versão\" não no canal especificado. Esperado: %s, Obtido: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="ola")
async def ola(ctx):
    user = ctx.author
    await ctx.send(
        f"Olá, {user.name}! Eu sou um bot em desenvolvimento e estou aqui para ajudar! 😄 "
        "Como posso ser útil hoje?"
    )


@bot.command(name="python")
async def python_docs(ctx):
    if ctx.channel.id == int(ID_CANAL):
        await ctx.send(f"Python: {URL_PYTHON}")
    else:
        logger.info(
            "Command \"python\" not in the specified channel. Expected: %s, Got: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="javascript", aliases=["js"])
async def javascript_docs(ctx):
    if ctx.channel.id == int(ID_CANAL):
        await ctx.send(f"JavaScript: {URL_JAVASCRIPT}")
    else:
        logger.info(
            "Command \"javascript\" not in the specified channel. Expected: %s, Got: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="html")
async def html_docs(ctx):
    if ctx.channel.id == int(ID_CANAL):
        await ctx.send(f"HTML: {URL_HTML}")
    else:
        logger.info(
            "Command \"html\" not in the specified channel. Expected: %s, Got: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="css")
async def css_docs(ctx):
    if ctx.channel.id == int(ID_CANAL):
        await ctx.send(f"CSS: {URL_CSS}")
    else:
        logger.info(
            "Command \"css\" not in the specified channel. Expected: %s, Got: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="mongodb", aliases=["mongo"])
async def mongodb_docs(ctx):
    if ctx.channel.id == int(ID_CANAL):
        await ctx.send(f"MongoDB: {URL_MONGO}")
    else:
        logger.info(
            "Command \"mongodb\" not in the specified channel. Expected: %s, Got: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="c#", aliases=["csharp"])
async def csharp(ctx):
    if ctx.channel.id == int(ID_CANAL):
        await ctx.send(f"Documentação de C#: {CSHARP}")
    else:
        logger.info(
            "Comando \"c#\" não no canal especificado. Esperado: %s, Obtido: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="c")
async def c_docs(ctx):
    if ctx.channel.id == int(ID_CANAL):
        await ctx.send(f"C: {C}")
    else:
        logger.info(
            "Command \"c\" not in the specified channel. Expected: %s, Got: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="snippet")
async def snippet(ctx, op: str, query: Optional[str] = None):
    if ctx.channel.id == int(ID_CANAL):
        op = op.lower()
        query = query.lower() if query else ""
        if query:
            query = "/" + query
        if op == "python":
            op = "python"
        elif op in ["js", "javascript"]:
            op = "js"
        elif op == "react":
            op = "react"
        elif op == "css":
            op = "css"
        elif op in ["node", "nodejs"]:
            op = "js/node/p/1/"
        else:
            await ctx.send("Linguagem ou framework não suportado.")
            return
        await ctx.send(f"Snippet: https://www.30secondsofcode.org/{op}{query}/p/1/")
    else:
        await ctx.send("Este comando só pode ser usado no canal específico.")
        logger.info(
            "Command \"snippet\" not in the specified channel. Expected: %s, Got: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="pesquisa", aliases=["search"])
async def pesquisa(ctx, *, query: str):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    await ctx.send(f"Pesquisas: {search_url}")


@bot.command(name="youtube")
async def youtube(ctx, *, query: str):
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    await ctx.send(f"Pesquisas: {search_url}")


@bot.command(name="calc")
async def calc(ctx, op: str, a: int, b: int):
    if ctx.channel.id == int(ID_CANAL):
        if op == "soma":
            result = a + b
            await ctx.send(f"{a} + {b} = {result}")
        elif op == "sub":
            result = a - b
            await ctx.send(f"{a} - {b} = {result}")
        elif op == "mult":
            result = a * b
            await ctx.send(f"{a} * {b} = {result}")
        elif op == "div":
            if b != 0:
                result = a / b
                await ctx.send(f"{a} / {b} = {result}")
            else:
                await ctx.send("Divisão por zero não é permitida.")
        else:
            await ctx.send("Operação inválida. Use \"soma\", \"sub\", \"mult\" ou \"div\".")
    else:
        logger.info(
            "Command \"calc\" not in the specified channel. Expected: %s, Got: %s",
            int(ID_CANAL),
            ctx.channel.id,
        )


@bot.command(name="run")
async def run(ctx, lang: str = None, *, code: str = None):
    if lang is None or code is None:
        await ctx.send(
            "Uso correto: !run <linguagem> <código>\n"
            "Exemplo: !run python print('Hello, World!')"
        )
        return

    languages = {
        "python": "python3",
        "javascript": "javascript",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "php": "php",
    }

    lang = lang.lower()
    if lang not in languages:
        await ctx.send("Linguagem não suportada.")
        return

    data = {
        "language": languages[lang],
        "version": "*",
        "files": [
            {
                "name": f"my_code.{lang}",
                "content": code,
            }
        ],
        "stdin": "",
        "args": [],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://emkc.org/api/v2/piston/execute", json=data
            ) as resp:
                response_text = await resp.text()
                logger.info("Resposta da API Piston: %s", response_text)

                if resp.status != 200:
                    await ctx.send(f"Erro ao executar o código. Status: {resp.status}")
                    return

                result = await resp.json()
                run_result = result.get("run", {})
                output = run_result.get("output", "Erro ao obter a saída.")
                await ctx.send(f"Resultado da execução:\n```\n{output}\n```")
    except Exception as exc:
        await ctx.send(f"Ocorreu um erro: {exc}")


@bot.event
async def on_typing(channel, user, when):
    if isinstance(channel, discord.TextChannel) and channel.id == int(ID_CANAL):
        logger.info("%s is typing in %s (%s)", user.name, channel.name, channel.id)


def main():
    bot.run(BOT_TOKEN)


async def _send_paginated_ctx(ctx, content: str) -> None:
    chunks = chunk_text(content, max_size=1900)
    if not chunks:
        chunks = [""]
    for chunk in chunks:
        await ctx.send(chunk)


async def _handle_llm(ctx, prompt: str, title: str) -> None:
    try:
        async with ctx.typing():
            result = await llm_service.generate(prompt, user_key=str(ctx.author.id))
            content = f"**{title}**\n\n{result}"
            await _send_paginated_ctx(ctx, content)
    except RateLimitError as exc:
        await _send_paginated_ctx(ctx, f"Limite excedido: {exc}")
    except ExternalServiceError as exc:
        await _send_paginated_ctx(ctx, f"Falha ao consultar LLM: {exc}")
    except Exception as exc:
        await _send_paginated_ctx(ctx, f"Erro inesperado: {exc}")


@bot.command(name="pergunta")
async def ask_command(ctx, *, pergunta: str) -> None:
    prompt = build_ask_prompt(pergunta)
    await _handle_llm(ctx, prompt, "Pergunta")


@bot.command(name="codigo")
async def code_command(ctx, linguagem: str, *, tema: str) -> None:
    prompt = build_code_prompt(linguagem, tema)
    await _handle_llm(ctx, prompt, "Código")


@bot.command(name="debug")
async def debug_command(ctx, *, erro: str) -> None:
    prompt = build_debug_prompt(erro)
    await _handle_llm(ctx, prompt, "Debug")


@bot.command(name="docs")
async def docs_command(ctx, *, tecnologia: str) -> None:
    prompt = build_docs_prompt(tecnologia)
    await _handle_llm(ctx, prompt, "Docs")


@bot.command(name="status")
async def status_command(ctx) -> None:
    results = await llm_service.health()
    if not results:
        await _send_paginated_ctx(ctx, "Nenhum provider LLM configurado.")
        return

    lines = [f"- {name}: {'OK' if ok else 'OFF'}" for name, ok in results.items()]
    await _send_paginated_ctx(ctx, "**Status LLM**\n\n" + "\n".join(lines))
