import os
import discord
from discord.ext import commands

# ====================== AYARLAR ======================
TOKEN = os.getenv("TOKEN")

# Komut kullanabilecek kişilerin Discord ID'leri (birden fazla ekleyebilirsin)
ADMINS = [1260707131284520960]

# Varsayılan ayarlar
SELF_DEAF = True      # True = kendini sağır yap (önerilen)
SELF_MUTE = False     # True = kendini sustur
# ====================================================

client = discord.Client()
ses_dongusu = False
aktif_vc = None

@client.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"✅ Selfbot Başarıyla Giriş Yaptı: {client.user}")
    print(f"🎮 Komutlar: .katıl, .çık, .sesgircik, .dur, .durum")
    print(f"{'='*50}\n")

@client.event
async def on_message(message):
    global ses_dongusu, aktif_vc

    if message.author.id not in ADMINS:
        return

    # ====================== KOMUTLAR ======================

    # .katıl [kanal_id] veya .katıl (cevaplanan mesajdaki ses kanalına)
    if message.content.startswith(".katıl"):
        try:
            # Eğer mesajda kanal mention varsa
            if message.channel_mentions or message.raw_channel_mentions:
                channel = message.channel_mentions[0] if message.channel_mentions else client.get_channel(message.raw_channel_mentions[0])
            else:
                parts = message.content.split()
                vc_id = int(parts[1])
                channel = client.get_channel(vc_id)

            if channel and isinstance(channel, discord.VoiceChannel):
                # Önceki bağlantıyı kes
                if client.voice_clients:
                    for vc in client.voice_clients:
                        await vc.disconnect(force=True)

                vc = await channel.connect(self_deaf=SELF_DEAF, self_mute=SELF_MUTE, reconnect=True)
                aktif_vc = vc
                print(f"✅ {channel.name} kanalına bağlanıldı.")
                await message.channel.send(f"✅ `{channel.name}` kanalına girdim.")
            else:
                await message.channel.send("❌ Geçerli bir ses kanalı bulunamadı.")
        except Exception as e:
            await message.channel.send(f"❌ Hata: {e}")

    # .çık
    elif message.content == ".çık":
        ses_dongusu = False
        if client.voice_clients:
            for vc in client.voice_clients:
                await vc.disconnect(force=True)
            print("🔌 Ses kanalından çıkıldı.")
            await message.channel.send("🔌 Ses kanalından çıktım.")
        else:
            await message.channel.send("Zaten ses kanalında değilim.")

    # .durum
    elif message.content == ".durum":
        if client.voice_clients:
            vc = client.voice_clients[0]
            await message.channel.send(f"🎙️ Şu anda `{vc.channel.name}` kanalındayım.")
        else:
            await message.channel.send("Şu anda hiçbir ses kanalında değilim.")

    # .sesgircik [kanal_id] [saniye]
    elif message.content.startswith(".sesgircik"):
        try:
            parts = message.content.split()
            vc_id = int(parts[1])
            bekleme = float(parts[2])

            channel = client.get_channel(vc_id)
            if not channel or not isinstance(channel, discord.VoiceChannel):
                return await message.channel.send("❌ Geçerli bir ses kanalı ID'si gir.")

            ses_dongusu = True
            print(f"🔄 {bekleme} saniye aralıkla gir-çık döngüsü başladı: {channel.name}")

            await message.channel.send(f"🔄 `{channel.name}` kanalında **{bekleme} saniye** aralıkla gir-çık döngüsü başladı.\nDurdurmak için `.dur` yaz.")

            while ses_dongusu:
                try:
                    # Önceki bağlantıyı temizle
                    if client.voice_clients:
                        for vc in client.voice_clients:
                            await vc.disconnect(force=True)
                        await asyncio.sleep(1.5)

                    # Giriş yap
                    vc = await channel.connect(self_deaf=SELF_DEAF, self_mute=SELF_MUTE, reconnect=True)
                    aktif_vc = vc
                    print(f"📥 Giriş yapıldı → {channel.name}")
                    
                    await asyncio.sleep(bekleme)

                    # Çıkış yap
                    if vc.is_connected():
                        await vc.disconnect(force=True)
                        print(f"📤 Çıkış yapıldı → {channel.name}")

                    await asyncio.sleep(bekleme)

                except Exception as e:
                    print(f"⚠️ Döngü hatası: {e}")
                    await asyncio.sleep(3)

        except (IndexError, ValueError):
            await message.channel.send("❌ Kullanım: `.sesgircik <kanal_id> <saniye>`\nÖrnek: `.sesgircik 123456789012345678 45`")

    # .dur (her şeyi durdur)
    elif message.content == ".dur":
        ses_dongusu = False
        if client.voice_clients:
            for vc in client.voice_clients:
                await vc.disconnect(force=True)
        print("🛑 Tüm işlemler durduruldu.")
        await message.channel.send("🛑 Tüm ses işlemleri durduruldu.")

    # Bilinmeyen komut
    elif message.content.startswith("."):
        await message.channel.send("❌ Bilinmeyen komut. Mevcut komutlar: `.katıl`, `.çık`, `.sesgircik`, `.dur`, `.durum`")

# ====================== ÇALIŞTIR ======================
if __name__ == "__main__":
    if not TOKEN or TOKEN == "BURAYA_SADECE_TOKENINI_YAPISTIR":
        print("❌ Token eksik! Lütfen TOKEN kısmını doldur.")
        sys.exit(1)
    
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"❌ Çalıştırma hatası: {e}")
