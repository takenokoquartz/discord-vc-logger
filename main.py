import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

vc_watch_targets = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="watch", description="VCの入退出を報告するVCとチャンネルを設定します")
async def watch(interaction: discord.Interaction, vc_channel: discord.VoiceChannel):
    vc_watch_targets[vc_channel.id] = interaction.channel.id
    await interaction.response.send_message(
        f"✅ VC「{vc_channel.name}」のログをこのチャンネルに出力します", ephemeral=False
    )

@bot.tree.command(name="unwatch", description="VCの入退出報告を解除します")
async def unwatch(interaction: discord.Interaction, vc_channel: discord.VoiceChannel):
    if vc_channel.id in vc_watch_targets:
        del vc_watch_targets[vc_channel.id]
        await interaction.response.send_message(
            f"🛑 VC「{vc_channel.name}」の入退出報告を解除しました", ephemeral=False
        )
    else:
        await interaction.response.send_message(
            f"⚠️ VC「{vc_channel.name}」は現在報告対象ではありません", ephemeral=False
        )

@bot.event
async def on_voice_state_update(member, before, after):
    # VC 参加
    if after.channel and after.channel.id in vc_watch_targets:
        text_channel = bot.get_channel(vc_watch_targets[after.channel.id])
        if text_channel:
            await text_channel.send(f"🔔 {member.display_name} が VC「{after.channel.name}」に参加しました。")

    # VC 退出
    if before.channel and before.channel.id in vc_watch_targets:
        text_channel = bot.get_channel(vc_watch_targets[before.channel.id])
        if text_channel:
            await text_channel.send(f"👋 {member.display_name} が VC「{before.channel.name}」から退出しました。")

# Replit 上で動かし続けるための keep_alive
keep_alive()

# ⛔ 自分のBotのトークンをここに貼る（絶対に他人に見せないこと！


# Botを起動
bot.run(os.environ["TOKEN"])
