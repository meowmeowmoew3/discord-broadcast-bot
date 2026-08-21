import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize bot with only the intents needed for slash commands.
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Config file to store target channels
CONFIG_FILE = "broadcast_config.json"
PERMISSIONS_FILE = "permissions.json"

# Add your user IDs here (and your friend's)
# To get your Discord ID: Right-click your name → Copy User ID
AUTHORIZED_USERS = [
    509770778854555648,  # Your ID here
    688764082840666219,  # Your friend's ID here
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


def is_moderator_or_admin(interaction: discord.Interaction):
    """Check whether a member can manage broadcast channels."""
    if interaction.guild is None:
        return False
    permissions = interaction.user.guild_permissions
    return permissions.administrator or permissions.manage_channels


async def require_channel_manager(interaction: discord.Interaction):
    """Send a permission error and return whether the command may continue."""
    if is_moderator_or_admin(interaction):
        return True

    await interaction.response.send_message(
        "❌ Only moderators with **Manage Channels** or server administrators "
        "can manage broadcast channels.",
        ephemeral=True
    )
    return False


def save_config(config):
    """Save broadcast configuration"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

@bot.event
async def on_ready():
    """Bot startup message"""
    await bot.tree.sync()
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
@discord.app_commands.describe(channel_name="Search for and select a text channel")
async def add_channel(interaction: discord.Interaction, channel_name: str):
    """Add a text channel by name or by an autocomplete-selected channel ID."""
    if not await require_channel_manager(interaction):
        return

    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ This command must be used inside a server.",
            ephemeral=True
        )
        return

    requested_name = channel_name.strip().lstrip("#")
    channel = None

    # Autocomplete choices use the channel ID as their hidden value. This
    # keeps Unicode and punctuation in channel names out of Discord's resolver.
    if requested_name.isdigit():
        channel = interaction.guild.get_channel(int(requested_name))
        if channel is None:
            try:
                channel = await bot.fetch_channel(int(requested_name))
            except (discord.NotFound, discord.Forbidden):
                channel = None
    else:
        channel = next(
            (candidate for candidate in interaction.guild.text_channels
             if candidate.name == requested_name),
            None
        )

    if channel is None:
        await interaction.response.send_message(
            f"❌ I couldn't find a text channel named `{channel_name}` in this server. "
            "Use the exact name, including special characters, or use `/add_channel_id`.",
            ephemeral=True
        )
        return

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


@add_channel.autocomplete("channel_name")
async def add_channel_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> list[discord.app_commands.Choice[str]]:
    """Show matching text channels while the user types."""
    if interaction.guild is None:
        return []

    query = current.casefold().strip().lstrip("#")
    matches = [
        channel for channel in interaction.guild.text_channels
        if not query or query in channel.name.casefold()
    ]

    return [
        discord.app_commands.Choice(name=f"#{channel.name}", value=str(channel.id))
        for channel in matches[:25]
    ]


@bot.tree.command(name="add_channel_id", description="Add a text channel using its numeric Discord ID")
@discord.app_commands.describe(channel_id="The numeric ID of the channel")
async def add_channel_id(interaction: discord.Interaction, channel_id: str):
    """Add a channel by ID, avoiding channel-name and Unicode resolution issues."""
    if not await require_channel_manager(interaction):
        return

    try:
        channel = await bot.fetch_channel(int(channel_id.strip()))
    except (ValueError, discord.NotFound, discord.Forbidden):
        await interaction.response.send_message(
            "❌ I couldn't access that channel ID. Make sure it is numeric and "
            "that the bot can view the channel.",
            ephemeral=True
        )
        return

    if not isinstance(channel, (discord.TextChannel, discord.Thread)):
        await interaction.response.send_message(
            "❌ That ID is not a text channel or thread. Please use a channel "
            "where the bot can send messages.",
            ephemeral=True
        )
        return

    config = load_config()
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
    if not await require_channel_manager(interaction):
        return

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
    if not is_authorized(interaction.user.id):
        await interaction.response.send_message(
            "❌ Only authorized users can view the broadcast channel list.",
            ephemeral=True
        )
        return

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
    if not await require_channel_manager(interaction):
        return

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
