import discord
import os
import aiohttp
from google import genai
import asyncio 
import yt_dlp
from discord.ext import commands
from dotenv import load_dotenv

# CONFIGURARE YOUTUBE
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename, **ffmpeg_options), data=data)

# 1. INCARCAREA TOKEN-URILOR
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_KEY = os.getenv('WEATHER_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
NEWS_KEY = os.getenv('NEWS_API_KEY')

# 2. CONFIGURARE AI (GEMINI 2.0 FLASH) 
client = genai.Client(api_key=GEMINI_KEY)
model_id = "gemini-2.0-flash" 
active_chats = {} # Memoria pentru /ask

# 3. INITIALIZAREA BOTULUI
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True 

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("=========================================")
    print(f"BOTUL {bot.user.name} ESTE ONLINE")
    try:
        synced = await bot.tree.sync() 
        print(f"S-au sincronizat {len(synced)} comenzi Slash.")
    except Exception as e:
        print(f"Eroare sincronizare: {e}")
    print("=========================================")

# 4. COMENZI MUZICA

@bot.tree.command(name="play", description="Pune muzica de pe YouTube")
async def play(interaction: discord.Interaction, cautare: str):
    await interaction.response.defer()
    if not interaction.user.voice:
        return await interaction.followup.send("Trebuie sa fii intr-un canal vocal!")
    query = cautare if cautare.startswith("http") else f"ytsearch:{cautare}"
    canal = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client
    if voice_client is None:
        voice_client = await canal.connect()
    elif voice_client.channel != canal:
        await voice_client.move_to(canal)
    try:
        player = await YTDLSource.from_url(query, loop=bot.loop, stream=True)
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(player)
        await interaction.followup.send(f'Acum canta: {player.title}')
    except Exception as e:
        await interaction.followup.send(f"Eroare redare: {e}")

@bot.tree.command(name="stop", description="Opreste muzica")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message("Am oprit muzica.")
    else:
        await interaction.response.send_message("Nu sunt intr-un canal vocal.")

# 5. COMENZI VREMEA SI STIRI

@bot.tree.command(name="salut", description="Saluta botul")
async def slash_hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Salut, {interaction.user.mention}! Eu sunt **DoBuDu**.')

@bot.tree.command(name="vremea", description="Temperatura intr-un oras")
async def slash_weather(interaction: discord.Interaction, oras: str):
    await interaction.response.defer()
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': oras, 'appid': WEATHER_KEY, 'units': 'metric'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                temp = data['main']['temp']
                await interaction.followup.send(f"In **{oras.title()}** sunt **{temp} grade Celsius**.")
            else:
                await interaction.followup.send("Oras negasit.")

@bot.tree.command(name="stiri", description="Ultimele stiri")
async def slash_stiri(interaction: discord.Interaction, subiect: str):
    await interaction.response.defer()
    params = {'q': subiect, 'apiKey': NEWS_KEY, 'language': 'ro', 'pageSize': 3}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://newsapi.org/v2/everything", params=params) as resp:
            data = await resp.json()
            articles = data.get('articles', [])
            if not articles: return await interaction.followup.send("Nicio stire gasita.")
            msg = "\n".join([f"**{a['title']}**\n<{a['url']}>" for a in articles])
            await interaction.followup.send(msg)

# 6. COMENZI AI

@bot.tree.command(name="ask", description="Intreaba AI-ul (cu memorie)")
async def slash_ask_ai(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    cid = interaction.channel.id
    if cid not in active_chats:
        active_chats[cid] = []
    
    active_chats[cid].append({"role": "user", "parts": [{"text": prompt}]})
    
    try:
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=active_chats[cid]
        )
        if response.text:
            active_chats[cid].append({"role": "model", "parts": [{"text": response.text}]})
            await interaction.followup.send(response.text[:2000])
        else:
            await interaction.followup.send("Eroare: Raspuns gol.")
    except Exception as e:
        if "429" in str(e):
            await interaction.followup.send("Limita de cereri atinsa. Asteapta putin.")
        else:
            await interaction.followup.send(f"Eroare AI: {e}")

@bot.tree.command(name="reset", description="Sterge memoria AI")
async def slash_reset_chat(interaction: discord.Interaction):
    active_chats.pop(interaction.channel.id, None)
    await interaction.response.send_message("Am uitat tot ce am vorbit aici!")

bot.run(TOKEN)