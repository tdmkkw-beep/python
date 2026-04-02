import os
import discord
import asyncio
import sys
from flask import Flask
from threading import Thread

# ====================== AYARLAR ======================
TOKEN = os.getenv("TOKEN")
ADMINS = [1260707131284520960]
SELF_DEAF = True
SELF_MUTE = False
# ====================================================

# --- UYKU ENGELLEYİCİ SİSTEM (FLASK) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot 7/24 Aktif! 🏰"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)
ses_dongusu = False

@client.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"✅ Giriş Yapıldı: {client.user}")
    print(f"🎮 Komutlar: .katıl, .çık, .sesgircik, .dur")
    print(f"{'='*50}\n")

@client.event
async def on_message(message):
    global ses_dongusu
    if message.author.id not in ADMINS:
        return

    if message.content.startswith(".katıl"):
        try:
            parts = message.content.split()
            vc_id = int(parts[1])
            channel = client.get_channel(vc_id)
            if channel and isinstance(channel, discord.VoiceChannel):
                if client.voice_clients:
                    for vc in client.voice_clients:
                        await vc.disconnect(force=True)
                await channel.connect(self_deaf=SELF_DEAF, self_mute=SELF_MUTE, reconnect=True)
                await message.channel.send(f"✅ `{channel.name}` kanalına girdim.")
        except Exception as e:
            await message.channel.send(f"❌ Hata: {e}")

    elif message.content == ".çık":
        ses_dongusu = False
        for vc in client.voice_clients:
            await vc.disconnect(force=True)
        await message.channel.send("🔌 Çıkış yapıldı.")

    elif message.content == ".dur":
        ses_dongusu = False
        await message.channel.send("🛑 Döngü durduruldu.")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ HATA: TOKEN bulunamadı!")
        sys.exit(1)
    
    keep_alive() # Flask'ı başlat (Render'ı uyanık tutar)
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"❌ Çalıştırma hatası: {e}")
