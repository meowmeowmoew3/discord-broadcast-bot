import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Config file to store target channels
CONFIG_FILE = "broadcast_config.json"
PERMISSIONS_FILE = "permissions.json"

# Add your user IDs here (and your friend's)
# To get your Discord ID: Right-click your name → Copy User ID
AUTHORIZED_USERS = [
    # 123456789,  # Your ID here
    # 987654321,  # Your friend's ID here
]

def load_config():
    """Load broadcast configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"channels": []}

def load_permissions():
    """Load authorized users list"""
    if os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, "r") as f:
            return json.load(f)
    return {"authorized_users": AUTHORIZED_USERS}

def save_permissions(data):
    """Save authorized users list"""
    with open(PERMISSIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_authorized(user_id):
    """Check if user is authorized to use broadcast"""
    perms = load_permissions()
    return user_id in perms["authorized_users"]

def save_config(config):
    """Save broadcast configuration"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

@bot.event
async def on_ready():
    """Bot startup message"""
    print(f"✅ Bot logged in as {bot.user}")
    print("Commands synced! Use /broadcast to send messages.")

@bot.tree.command(name="broadcast", description="Send a message to all configured channels")
@discord.app_commands.describe(message="The message to broadcast")
async def broadcast(interaction: discord.Interaction, message: str):
    """Broadcast a message to all configured channels"""
    # Check authorization
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message(
            "❌ **Access Denied** - You're not authorized to use this command!",
            ephemeral=True
        )
        return
    
    config = load_config()
    
    if not config["channels"]:
        await interaction.response.send_message(
            "❌ No channels configured yet! Use `/add_channel` to add targets.",
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    sent_count = 0
    failed_count = 0
    
    for channel_data in config["channels"]:
        try:
            channel = bot.get_channel(channel_data["channel_id"])
            if channel:
                await channel.send(message)
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Error sending to channel: {e}")
    
    await interaction.followup.send(
        f"✅ Message sent to {sent_count} channel(s)!\n"
        f"{'❌ Failed: ' + str(failed_count) if failed_count > 0 else ''}"
    )

@bot.tree.command(name="add_channel", description="Add a channel to broadcast to")
@discord.app_commands.describe(channel="The channel to add")
async def add_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Add a channel to the broadcast list"""
    config = load_config()
    
    # Check if channel already exists
    if any(c["channel_id"] == channel.id for c in config["channels"]):
        await interaction.response.send_message(
            f"⚠️ {channel.mention} is already in the broadcast list!",
            ephemeral=True
        )
        return
    
    config["channels"].append({
        "channel_id": channel.id,
        "server_name": channel.guild.name,
        "channel_name": channel.name
    })
    save_config(config)
    
    await interaction.response.send_message(
        f"✅ Added {channel.mention} from **{channel.guild.name}** to broadcast list!"
    )

@bot.tree.command(name="remove_channel", description="Remove a channel from broadcast list")
@discord.app_commands.describe(channel="The channel to remove")
async def remove_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Remove a channel from the broadcast list"""
    config = load_config()
    
    initial_count = len(config["channels"])
    config["channels"] = [c for c in config["channels"] if c["channel_id"] != channel.id]
    
    if len(config["channels"]) < initial_count:
        save_config(config)
        await interaction.response.send_message(
            f"✅ Removed {channel.mention} from broadcast list!"
        )
    else:
        await interaction.response.send_message(
            f"⚠️ {channel.mention} was not in the broadcast list.",
            ephemeral=True
        )

@bot.tree.command(name="list_channels", description="Show all configured broadcast channels")
async def list_channels(interaction: discord.Interaction):
    """List all configured channels"""
    config = load_config()
    
    if not config["channels"]:
        await interaction.response.send_message("No channels configured yet!")
        return
    
    channel_list = "\n".join([
        f"• **{c['server_name']}** → #{c['channel_name']}"
        for c in config["channels"]
    ])
    
    await interaction.response.send_message(
        f"📢 **Broadcast Channels** ({len(config['channels'])}):\n{channel_list}"
    )

@bot.tree.command(name="clear_all", description="Remove all channels from broadcast list")
async def clear_all(interaction: discord.Interaction):
    """Clear all configured channels"""
    config = load_config()
    config["channels"] = []
    save_config(config)
    
    await interaction.response.send_message("✅ Cleared all broadcast channels!")

@bot.tree.command(name="authorize", description="Allow a user to use the broadcast command")
@discord.app_commands.describe(user="The user to authorize")
async def authorize(interaction: discord.Interaction, user: discord.User):
    """Authorize a user to use broadcast commands"""
    # Only the bot owner can manage permissions
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message(
            "❌ Only authorized users can manage permissions!",
            ephemeral=True
        )
        return
    
    perms = load_permissions()
    
    if user.id in perms["authorized_users"]:
        await interaction.response.send_message(
            f"⚠️ {user.mention} is already authorized!",
            ephemeral=True
        )
        return
    
    perms["authorized_users"].append(user.id)
    save_permissions(perms)
    
    await interaction.response.send_message(
        f"✅ Authorized {user.mention} to use broadcast commands!"
    )

@bot.tree.command(name="unauthorize", description="Revoke a user's broadcast access")
@discord.app_commands.describe(user="The user to unauthorize")
async def unauthorize(interaction: discord.Interaction, user: discord.User):
    """Revoke a user's broadcast permission"""
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message(
            "❌ Only authorized users can manage permissions!",
            ephemeral=True
        )
        return
    
    perms = load_permissions()
    
    if user.id not in perms["authorized_users"]:
        await interaction.response.send_message(
            f"⚠️ {user.mention} is not authorized!",
            ephemeral=True
        )
        return
    
    perms["authorized_users"].remove(user.id)
    save_permissions(perms)
    
    await interaction.response.send_message(
        f"✅ Revoked {user.mention}'s broadcast access!"
    )

@bot.tree.command(name="authorized_users", description="Show who can use the broadcast command")
async def authorized_users(interaction: discord.Interaction):
    """List all authorized users"""
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message(
            "❌ Only authorized users can view this!",
            ephemeral=True
        )
        return
    
    perms = load_permissions()
    
    if not perms["authorized_users"]:
        await interaction.response.send_message("No authorized users yet!")
        return
    
    user_list = []
    for user_id in perms["authorized_users"]:
        try:
            user = await bot.fetch_user(user_id)
            user_list.append(f"• {user.name} ({user_id})")
        except:
            user_list.append(f"• Unknown User ({user_id})")
    
    await interaction.response.send_message(
        f"📋 **Authorized Users**:\n" + "\n".join(user_list)
    )

# Main bot launch
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found!")
        print("Set the environment variable DISCORD_BOT_TOKEN with your bot token.")
        exit(1)
    
    bot.run(TOKEN)
