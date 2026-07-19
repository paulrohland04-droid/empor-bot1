import discord
from discord import app_commands
import database
import config

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.id in config.ADMIN_IDS

@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot online as {client.user}")

@tree.command(name="createkey", description="Create a new license key")
@app_commands.describe(duration="Key duration")
@app_commands.choices(duration=[
    app_commands.Choice(name="1 Day", value="1day"),
    app_commands.Choice(name="7 Days", value="7days"),
    app_commands.Choice(name="30 Days", value="30days"),
    app_commands.Choice(name="Lifetime", value="lifetime"),
])
async def createkey(interaction: discord.Interaction, duration: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return
    key = database.create_license(duration)
    if not key:
        await interaction.response.send_message("❌ Failed to create key", ephemeral=True)
        return
    labels = {"1day": "1 Day", "7days": "7 Days", "30days": "30 Days", "lifetime": "Lifetime"}
    embed = discord.Embed(title="✅ Key Created", color=0x00ff00)
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.add_field(name="Duration", value=labels.get(duration, duration), inline=True)
    embed.add_field(name="Status", value="`unused`", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="keys", description="List all license keys")
async def keys(interaction: discord.Interaction):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return
    rows = database.get_all_licenses()
    if not rows:
        await interaction.response.send_message("No keys found", ephemeral=True)
        return
    labels = {"1day": "1d", "7days": "7d", "30days": "30d", "lifetime": "∞"}
    chunks = []
    for row in rows[:25]:
        hwid_short = row["hwid"][:12] + "..." if row["hwid"] and len(row["hwid"]) > 12 else (row["hwid"] or "-")
        expires = row["expires_at"][:10] if row["expires_at"] else "∞"
        chunks.append(f"`{row['license_key']}` | {labels.get(row['duration'], '?')} | {row['status']} | HWID:{hwid_short} | Ablauf:{expires}")
    text = "\n".join(chunks)
    if len(text) > 1900:
        text = text[:1900] + "..."
    embed = discord.Embed(title=f"📋 License Keys ({len(rows)})", description=text, color=0x3498db)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="deletekey", description="Delete a license key")
@app_commands.describe(key="The key to delete")
async def deletekey(interaction: discord.Interaction, key: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return
    key = key.upper().strip()
    database.delete_license(key)
    await interaction.response.send_message(f"🗑️ Deleted `{key}`", ephemeral=True)

@tree.command(name="resetkey", description="Reset a license key to unused")
@app_commands.describe(key="The key to reset")
async def resetkey(interaction: discord.Interaction, key: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ No permission", ephemeral=True)
        return
    key = key.upper().strip()
    database.reset_license(key)
    await interaction.response.send_message(f"🔄 Reset `{key}` to unused", ephemeral=True)

if __name__ == "__main__":
    client.run(config.DISCORD_TOKEN)
