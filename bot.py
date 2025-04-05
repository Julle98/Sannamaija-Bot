import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp as youtube_dl
import asyncio
import logging
import os
import datetime
import pytz
from datetime import datetime
import random
import re
from bs4 import BeautifulSoup
from pypresence import Presence
from collections import deque
from discord import ui, TextInput
from discord.ui import Modal, TextInput
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
APPLICATION_ID = int(os.getenv("APPLICATION_ID"))  
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = commands.Bot(command_prefix="!", intents=intents, application_id=APPLICATION_ID)

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.music_queue = deque()
        self.current_status = "Online"

statuses = [
    "Valmiina soittamaan musiikkia",
    "Odottaa uusia komentoja",
    "Auttaa 24G ryhmäläisiä",
    "Kerään tietonne",
    "Seurana keskusteluissa",
    "Käynnissä 24G ryhmän kanssa",
    "Odottaa musiikkia",
    "Toimin osittain luultavasti"
]

music_queue = deque()
original_status = random.choice(statuses)

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
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'default_search': 'auto'
}

ffmpeg_options = {'options': '-vn'}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

import discord
import asyncio
import yt_dlp

ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
}
ytdl = yt_dlp.YoutubeDL(ytdl_opts)

ffmpeg_options = {
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data):
        super().__init__(source)
        self.data = data
        self.title = data.get('title')
        self.duration = data.get('duration')
        self.start_time = datetime.now(pytz.utc)
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(
            filename, 
            executable="YOUR_FILE_LOCATION", 
            **ffmpeg_options), data=data)

music_queue = []

youtube_dl.utils.bug_reports_message = lambda: ''

from datetime import datetime, timezone, timedelta

def get_current_time_in_utc_plus_2():
    utc_plus_2 = timezone(timedelta(hours=2))
    current_time = datetime.now(utc_plus_2)
    return current_time.strftime('%d-%m-%Y %H:%M:%S')

@bot.event
async def on_member_join(member): 
    tervetuloviesti = (
        "Tervetuloa 24G discord palvelimelle. Olen yksi palvelimen boteista ja minua voit ohjata erilaisilla `/` komennoilla. "
        "Odota kuitenkin ensin rauhassa hyväksymistä palvelimelle. Manuaalinen verifiointi voi viedä aikaa. "
        "Hauska nähdä sinut täällä!\n\n(tämä viesti on lähetetty automaattisesti)"
    )

    try:
        await member.send(tervetuloviesti)
        print(f"Tervetuloviesti lähetetty käyttäjälle {member.name}")
    except discord.Forbidden:
        print(f"En voinut lähettää tervetuloviestiä käyttäjälle {member.name}")

@bot.event
async def update_status():
    while True:
        new_status = random.choice(statuses)
        await bot.change_presence(activity=discord.Game(name=new_status))
        await asyncio.sleep(3600)  

@bot.event
async def on_ready():

    synced = await bot.tree.sync()
    print(f"Synkronoitu {len(synced)} komentoa!")

    bot_status_kanava = discord.utils.get(bot.get_all_channels(), name="YOUR_CHANNEL")
    if bot_status_kanava:
        async for message in bot_status_kanava.history(limit=100):
            await message.delete()
        current_time = get_current_time_in_utc_plus_2()
        await bot_status_kanava.send(f"Botti on nyt toiminnassa, käynnistetty: {current_time}")

    await bot.change_presence(activity=discord.Game(name=original_status))
    bot.loop.create_task(update_status())

UTC_CITIES = {
    -12: "Baker Island",
    -11: "Pago Pago",
    -10: "Honolulu",
    -9: "Anchorage",
    -8: "Los Angeles",
    -7: "Denver",
    -6: "Mexico City",
    -5: "New York",
    -4: "Santiago",
    -3: "Buenos Aires",
    -2: "South Georgia",
    -1: "Azores",
    0: "London",
    1: "Berlin",
    2: "Helsinki",
    3: "Moscow",
    4: "Dubai",
    5: "Karachi",
    6: "Dhaka",
    7: "Bangkok",
    8: "Beijing",
    9: "Tokyo",
    10: "Sydney",
    11: "Nouméa",
    12: "Auckland",
    13: "Samoa",
    14: "Kiritimati"
}

class AikaModal(discord.ui.Modal, title="Aikakysely"):
    kysymys = discord.ui.TextInput(label="UTC aika? (Esim. 2, -5, 0, 3)", placeholder="Kirjoita UTC aika", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_input = self.kysymys.value.strip()

        if user_input.isdigit() or (user_input.startswith('-') and user_input[1:].isdigit()):
            utc_offset = int(user_input)
            timezone = pytz.FixedOffset(utc_offset * 60)
            city = UTC_CITIES.get(utc_offset, "Tuntematon kaupunki")
        else:
            timezone = pytz.timezone('Europe/Helsinki')
            city = "Helsinki"

        current_time = datetime.now(timezone).strftime('%H:%M:%S')
        await interaction.response.send_message(f'Kello on nyt **{current_time}** kaupungissa **{city}** (UTC {utc_offset:+d})')

@bot.tree.command(name="aika", description="Näytä nykyinen aika haluamassasi UTC-ajassa")
@app_commands.checks.has_role("YOUR_ROLE")
async def aika(interaction: discord.Interaction):
    await interaction.response.send_modal(AikaModal())

@bot.tree.command(name="moikka", description="Moikkaa takaisin")
@app_commands.checks.has_role("YOUR_ROLE")
async def moikka(interaction):
    await interaction.response.send_message("Moikka!")

@bot.tree.command(name="ruokailuvuorot", description="Näytä ruokailuvuorot")
@app_commands.checks.has_role("YOUR_ROLE")
async def ruokailuvuorot(interaction):
    await interaction.response.send_message("https://drive.google.com/file/d/1BFU02aJIFbSRYhPHix8VvqI_g_waMCNp/view?pli=1")

@bot.tree.command(name="ruoka", description="Näytä Ruokalista")
@app_commands.checks.has_role("YOUR_ROLE")
async def ruokailuvuorot(interaction):
    await interaction.response.send_message("https://kouluruoka.fi/menu/vantaa_tikkurilanlukio/")

@bot.tree.command(name="sano", description="Sano Sannamaijalle sanottavaa")
@app_commands.checks.has_role("YOUR_ROLE")
async def sano(interaction: discord.Interaction, viesti: str):
    kielletyt_sanat = ["YOUR_FORBIDDEN_WORDS"]

    if any(re.search(rf"\b{kielletty_sana}\b", viesti, re.IGNORECASE) for kielletty_sana in kielletyt_sanat):
        await interaction.response.send_message("Viestisi sisältää kiellettyjä sanoja, eikä sitä lähetetty.", ephemeral=True)
    else:
        try:
            await interaction.response.send_message(viesti)
        except discord.Forbidden:
            await interaction.response.send_message("Minulla ei ole oikeuksia lähettää viestejä tähän kanavaan.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Viestin lähetys epäonnistui.", ephemeral=True)

@bot.tree.command(name="mielipide", description="Kysy mielipide Sannamaijalta")
@app_commands.checks.has_role("YOUR_ROLE")
async def mielipide(interaction: discord.Interaction):
    modal = MielipideModal()
    await interaction.response.send_modal(modal)

class MielipideModal(Modal):
    def __init__(self):
        super().__init__(title="Anna mielipide")
        self.add_item(TextInput(label="Mielipiteen kohde", placeholder="Kirjoita kohde, josta haluat mielipiteen"))

    async def on_submit(self, interaction: discord.Interaction):
        kohde = self.children[0].value
        vastaukset = [
            ("W", 50),
            ("L", 42),
            ("Ehdottomasti", 3),
            ("En usko", 2),
            ("Vaikea sanoa", 1),
            ("Mahdollisesti", 1),
            ("Ei todellakaan", 1)
        ]

        valinta = random.choices(
            population=[v[0] for v in vastaukset],
            weights=[v[1] for v in vastaukset],
            k=1
        )[0]

        await interaction.response.send_message(f"Mielipiteeni kohteesta {kohde} on {valinta}")

@bot.tree.command(name="sammutus", description="Sammuta botti")
@app_commands.checks.has_role("YOUR_ROLE")
async def sammutus(interaction: discord.Interaction):
    bot_status_kanava = discord.utils.get(interaction.guild.text_channels, name="bot-status")
    if not bot_status_kanava:
        bot_status_kanava = await interaction.guild.create_text_channel(name="bot-status")

    async for message in bot_status_kanava.history(limit=100):
        await message.delete()

    timezone = pytz.timezone('Europe/Helsinki')
    sammutusaika = datetime.now(timezone).strftime('%d-%m-%Y %H:%M:%S')
    await bot_status_kanava.send(f"Botti sammutettu {sammutusaika}.")
    await interaction.response.send_message("Botti sammuu...")

    await bot.close()  

@bot.tree.command(name="vaihda_tilaviesti", description="Vaihda tilaviesti botilta")
@app_commands.checks.has_role("YOUR_ROLE")
async def vaihda_tilaviesti(interaction: discord.Interaction, uusi_teksti: str):
    global current_status
    current_status = uusi_teksti
    await bot.change_presence(activity=discord.Game(name=current_status))
    await interaction.response.send_message(f"Tilaviesti vaihdettu: {current_status}")


@bot.tree.command(name="uudelleenkaynnistys", description="Käynnistä botti uudelleen")
@app_commands.checks.has_role("YOUR_ROLE")
async def uudelleenkaynnistys(interaction: discord.Interaction):
    bot_status_kanava = discord.utils.get(interaction.guild.text_channels, name="bot-status")
    if not bot_status_kanava:
        bot_status_kanava = await interaction.guild.create_text_channel(name="bot-status")

    async for message in bot_status_kanava.history(limit=100):
        await message.delete()

    await bot_status_kanava.send("Botti käynnistyy uudelleen...")
    await interaction.response.send_message("Botti käynnistetään uudelleen...")
    await bot.close()
    os.system("python " + __file__)
    await bot.change_presence(activity=discord.Game(name=current_status))

from discord import ui, TextInput

class ChannelClearModal(Modal):
    def __init__(self):
        super().__init__(title="Tyhjennä kanava")

        self.channel_name = TextInput(label="Kanavan nimi")
        self.confirmation = TextInput(label="Kirjoita 'KYLLÄ' vahvistaaksesi", placeholder="KYLLÄ")

        self.add_item(self.channel_name)
        self.add_item(self.confirmation)

    async def on_submit(self, interaction: discord.Interaction):
        channel_name = self.channel_name.value
        confirmation = self.confirmation.value
        channel = discord.utils.get(interaction.guild.channels, name=channel_name)

        if channel is None:
            await interaction.response.send_message("Kanavaa ei löytynyt. Yritä uudelleen.", ephemeral=True)
            return

        if confirmation.strip().upper() != "KYLLÄ":
            await interaction.response.send_message("Vahvistus epäonnistui. Kirjoita 'KYLLÄ' vahvistaaksesi.", ephemeral=True)
            return

        try:
            await channel.purge()
            await interaction.response.send_message(f"Kaikki viestit on poistettu kanavasta {channel_name}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Minulla ei ole oikeuksia poistaa viestejä tässä kanavassa.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Viestien poistaminen epäonnistui.", ephemeral=True)

@bot.tree.command(name="clear", description="Poista kaikki viestit kanavasta")
@app_commands.checks.has_role("YOUR_ROLE")
async def clear(interaction: discord.Interaction):
    modal = ChannelClearModal()
    await interaction.response.send_modal(modal)


@bot.tree.command(name="mute", description="Aseta mute jäsenelle")
@app_commands.checks.has_role("YOUR_ROLE")
async def mute(interaction: discord.Interaction, jäsen: discord.Member, kesto: str):
    mestari_role = discord.utils.get(interaction.guild.roles, name="Mestari")
    if mestari_role in jäsen.roles:
        await interaction.response.send_message("Et voi asettaa mutea käyttäjälle, jolla on Mestari-rooli.")
        return

    try:
        seconds = int(kesto[:-1])
        duration_type = kesto[-1]
        if duration_type == "s":
            delay = seconds
        elif duration_type == "m":
            delay = seconds * 60
        elif duration_type == "h":
            delay = seconds * 3600
        else:
            await interaction.response.send_message("Virheellinen aikaformaatti. Käytä esimerkiksi: 10s, 5m, 1h")
            return

        remove_role = discord.utils.get(interaction.guild.roles, name="24G")
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")

        if not remove_role:
            await interaction.response.send_message("Roolia '24G' ei löytynyt.")
            return

        if not mute_role:
            mute_role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False, add_reactions=False)

        await jäsen.remove_roles(remove_role)
        await jäsen.add_roles(mute_role)
        await interaction.response.send_message(f"{jäsen.mention} asetettu jäähylle {kesto}.")
        await asyncio.sleep(delay)
        await jäsen.remove_roles(mute_role)
        await jäsen.add_roles(remove_role)
        await interaction.response.send_message(f"{jäsen.mention} jäähy päättynyt ja rooli palautettu.")

    except ValueError:
        await interaction.response.send_message("Virheellinen aikaformaatti. Käytä esimerkiksi: 10s, 5m, 1h")

    except asyncio.TimeoutError:
        await interaction.response.send_message("Aikakatkaisu. Jäähyä ei asetettu.")


@bot.tree.command(name="huolto", description="Aseta botti huoltotilaan")
@app_commands.checks.has_role("YOUR_ROLE")
async def huolto(interaction: discord.Interaction):
    await interaction.response.send_message("Kuinka kauan kestää huolto? (Esimerkiksi: 10s, 5m, 1h)")

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=30.0)
        kesto = msg.content

        await interaction.followup.send("Kerro lisätiedot korjattavasta asiasta:")

        try:
            lisatiedot = await bot.wait_for("message", check=check, timeout=60.0)
            lisatiedot_text = lisatiedot.content

            try:
                seconds = int(kesto[:-1])
                duration_type = kesto[-1]
                if duration_type == "s":
                    delay = seconds
                elif duration_type == "m":
                    delay = seconds * 60
                elif duration_type == "h":
                    delay = seconds * 3600
                else:
                    await interaction.followup.send("Virheellinen aikaformaatti. Käytä esimerkiksi: 10s, 5m, 1h")
                    return

                huolto_kanava = discord.utils.get(interaction.guild.text_channels, name="bot-status")
                if not huolto_kanava:
                    huolto_kanava = await interaction.guild.create_text_channel(name="bot-status")

                await huolto_kanava.send(f"Botti menee huoltotilaan. Arvioitu kesto: {kesto}. Lisätiedot: {lisatiedot_text}")
                await interaction.followup.send(f"Huoltoaika {kesto} ja lisätiedot {lisatiedot_text} vahvistettu ja merkitty kanavalle {huolto_kanava.mention}.")
                await bot.close()

            except ValueError:
                await interaction.followup.send("Virheellinen aikaformaatti. Käytä esimerkiksi: 10s, 5m, 1h")

        except asyncio.TimeoutError:
            await interaction.followup.send("Aikakatkaisu. Et antanut lisätietoja ajoissa.")

    except asyncio.TimeoutError:
        await interaction.response.send_message("Aikakatkaisu. Huoltokomennon suoritus keskeytetty.")

@sammutus.error
@uudelleenkaynnistys.error
@vaihda_tilaviesti.error
@clear.error
@mute.error
@huolto.error
async def command_error(interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Tämä komento on vain rooleille 'YOUR_ROLE'.")

music_queue = deque()

from discord.ui import Modal, TextInput

@bot.tree.command(name="liity", description="Liity puhekanavaan kuuntelemaan musiikkia")
@app_commands.checks.has_role("YOUR_ROLE")
async def liity(interaction: discord.Interaction):
    modal = VoiceChannelJoinModal()
    await interaction.response.send_modal(modal)

class VoiceChannelJoinModal(Modal):
    def __init__(self):
        super().__init__(title="Liity puhekanavaan")
        self.channel_name = TextInput(label="Puhekanavan nimi")
        self.add_item(self.channel_name)

    async def on_submit(self, interaction: discord.Interaction):
        channel_name = self.channel_name.value
        channel = discord.utils.get(interaction.guild.channels, name=channel_name)
        if channel is None or not isinstance(channel, discord.VoiceChannel):
            await interaction.response.send_message("Puhekanavaa ei löytynyt. Yritä uudelleen.", ephemeral=True)
            return
        
        try:
            await channel.connect()
            await interaction.response.send_message(f"Liitytty kanavaan: {channel.name}", ephemeral=True)
        except discord.errors.ClientException as e:
            await interaction.response.send_message(f"Virhe liittyessä puhekanavaan: {e}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Yleinen virhe liittyessä puhekanavaan: {str(e)}", ephemeral=True)

@bot.tree.command(name="soita", description="Soita musiikkia annetusta Youtube URL:sta")
@app_commands.checks.has_role("YOUR_ROLE")
async def soita(interaction: discord.Interaction, url: str):
    await interaction.response.defer(ephemeral=True)  

    if interaction.user.voice and interaction.guild.voice_client and interaction.user.voice.channel == interaction.guild.voice_client.channel:
        async with interaction.channel.typing():
            try:
                player = await YTDLSource.from_url(url, loop=bot.loop)
                music_queue.append(player)

                if not interaction.guild.voice_client.is_playing():
                    await play_next(interaction)
                    await bot.change_presence(activity=discord.Game(name="Soittaa musiikkia"))
                    await interaction.followup.send(f"Soitetaan nyt: {player.title}", ephemeral=True)
                else:
                    await interaction.followup.send(f'Lisätty jonoon: {player.title}', ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Virhe musiikkia soittaessa: {str(e)}", ephemeral=True)
    else:
        await interaction.followup.send("Sinun täytyy olla samalla puhekanavalla botin kanssa käyttääksesi tätä komentoa.", ephemeral=True)

@bot.tree.command(name="kuuntelutiedot", description="Näytä kuuntelutiedot")
@app_commands.checks.has_role("YOUR_ROLE")
async def kuuntelutiedot(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        current_player = interaction.guild.voice_client.source
        elapsed_time = (datetime.now(pytz.utc) - current_player.start_time).seconds
        minutes, seconds = divmod(elapsed_time, 60)
        queue_length = len(music_queue)
        await interaction.response.send_message(f"Kuuntelussa: {current_player.title}\nKuunneltu: {minutes} min {seconds} sek\nBiisejä jonossa: {queue_length}")
    else:
        await interaction.response.send_message("Ei biisiä soitossa juuri nyt.")

@bot.tree.command(name="jono", description="Lisää biisi jonoon annetusta Youtube URL:sta")
@app_commands.checks.has_role("YOUR_ROLE")
async def jono(interaction: discord.Interaction, url: str):
    if not interaction.user.voice or not interaction.guild.voice_client or interaction.user.voice.channel != interaction.guild.voice_client.channel:
        await interaction.response.send_message("Sinun täytyy olla samalla puhekanavalla botin kanssa käyttääksesi tätä komentoa.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)  
    
    try:
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        music_queue.append(player)
        await interaction.followup.send(f'Lisätty jonoon: {player.title}', ephemeral=True)

        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            await bot.change_presence(activity=discord.Game(name="Soittaa paljon musiikkia"))
    except Exception as e:
        await interaction.followup.send(f"Virhe lisättäessä jonoon: {str(e)}", ephemeral=True)

async def play_next(interaction: discord.Interaction):
    if music_queue and interaction.guild.voice_client:
        player = music_queue.popleft()

        def after_play(err):
            if err:
                print(f"Virhe soitossa: {err}")
            if music_queue:  
                coro = play_next(interaction)
                fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
                fut.result()

        interaction.guild.voice_client.play(player, after=after_play)
        await interaction.channel.send(f'Soitto käynnissä: {player.title}')
    else:
        await interaction.channel.send("Jono on tyhjä.")  

@bot.tree.command(name="skip", description="Ohita nykyinen kappale seuraavaan")
@app_commands.checks.has_role("YOUR_ROLE")
async def skip(interaction: discord.Interaction):
    if interaction.user.voice and interaction.guild.voice_client and interaction.user.voice.channel == interaction.guild.voice_client.channel:
        if not music_queue:
            await interaction.response.send_message("Jono on tyhjä, ei ole mitään kappaletta, jonka voisi ohittaa.")
        elif interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("Biisi vaihdettu!")
        else:
            await interaction.response.send_message("Ei biisiä soitossa juuri nyt.")
    else:
        await interaction.response.send_message("Sinun täytyy olla samalla puhekanavalla botin kanssa käyttääksesi tätä komentoa.")

@bot.tree.command(name="jonolista", description="Näytä jonossa olevat biisit")
@app_commands.checks.has_role("YOUR_ROLE")
async def jonolista(interaction: discord.Interaction):
    if not music_queue:
        await interaction.response.send_message("Jono on tyhjä.", ephemeral=True)
        return

    queue_list = "\n".join(f"{i+1}. {player.title}" for i, player in enumerate(music_queue))

    if len(queue_list) > 2000:
        messages = [queue_list[i:i+2000] for i in range(0, len(queue_list), 2000)]
        await interaction.response.send_message(messages[0], ephemeral=True)
        for msg in messages[1:]:
            await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(f"Jonossa olevat biisit:\n{queue_list}", ephemeral=True)

@bot.tree.command(name="loppu", description="Katkaise yhteys botilta puhekanavasta")
@app_commands.checks.has_role("YOUR_ROLE")
async def loppu(interaction: discord.Interaction):
    if interaction.user.voice and interaction.guild.voice_client and interaction.user.voice.channel == interaction.guild.voice_client.channel:
        if interaction.guild.voice_client:
            interaction.guild.voice_client.stop()
            await interaction.guild.voice_client.disconnect()
            await bot.change_presence(activity=discord.Game(name=original_status))
            await interaction.response.send_message(f"Yhteys puhekanavasta katkaistu", ephemeral=True)
        else:
            await interaction.response.send_message("Botti ei ole puhekanavassa.")
    else:
        await interaction.response.send_message("Sinun täytyy olla samalla puhekanavalla botin kanssa käyttääksesi tätä komentoa.")

@bot.event
async def on_message(message):
    print(f"Viesti vastaanotettu: {message.content}")
    await bot.process_commands(message)  

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()  
    token = os.getenv("DISCORD_BOT_TOKEN")
    bot.run(token)