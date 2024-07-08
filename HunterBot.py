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

# Commande 'hunter' avec un cooldown pour éviter les doubles envois


@bot.command()
@commands.cooldown(1, 4, commands.BucketType.user)
async def hunter(ctx):
    print("appel commande")
    conn = sqlite3.connect('images.db')
    c = conn.cursor()

    # Sélectionne une image aléatoire non montrée
    c.execute(
        "SELECT url FROM images WHERE shown = 0 ORDER BY RANDOM() LIMIT 1")
    result = c.fetchone()

    if result:
        image_filename = result[0]
        image_path = os.path.join('image', image_filename)

        # Vérifie que l'image existe avant d'essayer de l'envoyer
        if os.path.exists(image_path):
            # Marque l'image comme montrée
            c.execute("UPDATE images SET shown = shown + 1 WHERE url = ?",
                      (image_filename, ))
            conn.commit()

            await ctx.send(file=discord.File(image_path))
        else:
            await ctx.send("L'image ne peut pas être trouvée.")
            c.execute("DELETE FROM images WHERE url = ?", (image_filename, ))
            conn.commit()
    else:
        await ctx.send(
            "Pas d'image de disponible ou toutes les images ont été montrées.")

    conn.close()


# Gestionnaire d'erreurs pour traiter les erreurs de cooldown
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = f"Cette commande est en cooldown. Veuillez attendre {error.retry_after:.2f} secondes."
        await ctx.send(msg)
    else:
        raise error  # Renvoie les autres erreurs pour qu'elles ne passent pas sous silence



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
