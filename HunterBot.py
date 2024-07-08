import discord
from discord.ext import commands
import os
import sqlite3
from aiohttp import web

# Configuration des intents nécessaires pour le bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Fonction pour configurer la base de données
def setup_database():
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            url TEXT PRIMARY KEY,
            shown INTEGER DEFAULT 0,
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

setup_database()

# Fonction pour démarrer un serveur web minimaliste
async def web_app():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 9000)   # Écoute sur le port 9000
    await site.start()

# Démarrage du serveur web et du bot
async def main():
    await web_app()  # Démarrer le serveur web
    token = os.getenv('DISCORD_TOKEN')
    await bot.start(token)  # Démarrer le bot Discord

# Exécution principale
if __name__ == '__main__':
    bot.loop.run_until_complete(main())
