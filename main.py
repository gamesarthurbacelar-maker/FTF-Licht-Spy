
import os
import aiohttp
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
FORUM_URL = "https://devforum.roblox.com/latest.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


async def buscar_topicos():
    async with aiohttp.ClientSession() as session:
        async with session.get(FORUM_URL) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)
    return data.get("topic_list", {}).get("topics", [])


def link_topico(topico):
    return (
        "https://devforum.roblox.com/t/"
        f"{topico.get('slug', 'topico')}/{topico.get('id', '')}"
    )


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"FTF Licht Spy conectado como {bot.user}")


@bot.tree.command(name="status", description="Consultar novidades públicas")
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        topicos = await buscar_topicos()
        linhas = [
            f"• [{t.get('title', 'Tópico')}]({link_topico(t)})"
            for t in topicos[:8]
        ]
        await interaction.followup.send(
            "**🕵️ FTF Licht Spy — Status**\n"
            + ("\n".join(linhas) if linhas else "Nenhum tópico encontrado.")
        )
    except Exception:
        await interaction.followup.send(
            "Não consegui consultar o DevForum agora."
        )


@bot.tree.command(name="mrwindy", description="Consultar atividade pública")
async def mrwindy(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        topicos = await buscar_topicos()
        encontrados = [
            t for t in topicos
            if t.get("last_poster_username", "").lower() == "mrwindy"
        ][:8]
        if encontrados:
            texto = "\n".join(
                f"• [{t.get('title', 'Tópico')}]({link_topico(t)})"
                for t in encontrados
            )
            await interaction.followup.send(
                "**Atividade pública encontrada:**\n" + texto
            )
        else:
            await interaction.followup.send(
                "Nenhuma atividade recente encontrada na lista consultada. "
                "Isso não confirma que MrWindy esteja offline."
            )
    except Exception:
        await interaction.followup.send(
            "Não consegui consultar o DevForum agora."
        )


@bot.tree.command(name="indev", description="Estado da consulta ao INDEV")
async def indev(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🧪 Ainda precisamos configurar uma fonte pública do INDEV."
    )


@bot.tree.command(
    name="probabilidade",
    description="Consultar sinais de possível atualização"
)
async def probabilidade(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        topicos = await buscar_topicos()
        relevantes = [
            t for t in topicos
            if "flee the facility" in t.get("title", "").lower()
            or t.get("title", "").lower().startswith("ftf ")
        ]
        await interaction.followup.send(
            "**📊 Sinais públicos do FTF**\n"
            f"Tópicos potencialmente relevantes: {len(relevantes)}\n\n"
            "Ainda não há dados suficientes para uma probabilidade "
            "confiável de atualização. Este número não é uma previsão."
        )
    except Exception:
        await interaction.followup.send(
            "Não consegui consultar as fontes agora."
        )


if not TOKEN:
    raise RuntimeError("Configure a variável DISCORD_TOKEN.")

bot.run(TOKEN)
