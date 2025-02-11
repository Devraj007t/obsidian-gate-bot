from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest, DeleteMessagesRequest
import os
import asyncio
from datetime import datetime, timedelta

# Load API credentials from environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))  # Ensure it's an integer
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("⚠ API credentials or bot token not set. Please check your environment variables.")

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Store invite cooldowns (user_id -> {group_id -> next_allowed_time})
user_invite_timers = {}

# Function to generate a unique invite link
async def generate_invite(group_id, user_id):
    now = datetime.utcnow()

    # Check if user has a cooldown for this group
    if user_id in user_invite_timers and group_id in user_invite_timers[user_id]:
        next_allowed_time = user_invite_timers[user_id][group_id]
        if now < next_allowed_time:
            wait_time = int((next_allowed_time - now).total_seconds() / 60)
            return f"⏳ You can generate a new invite link for this group in {wait_time} minutes."

    try:
        peer = await client.get_entity(int(group_id))  # Convert to valid peer
        invite = await client(ExportChatInviteRequest(
            peer=peer,
            usage_limit=1  # One-time use
        ))

        # Update cooldown timer (1 hour)
        if user_id not in user_invite_timers:
            user_invite_timers[user_id] = {}
        user_invite_timers[user_id][group_id] = now + timedelta(hours=1)

        return invite.link
    except Exception as e:
        print(f"Error generating invite link: {str(e)}")
        return f"⚠️ Failed to generate an invite link: {str(e)}"

# Command to request an invite link in DM
@client.on(events.NewMessage(pattern="^/invite$"))
async def request_group_id(event):
    if event.is_private:  # Ensure it's a private chat
        await event.reply("🔹 Please send me the group ID where you want an invite link (Example: -1001234567890).")

# Handle the user's group ID response
@client.on(events.NewMessage())
async def send_invite(event):
    if event.is_private and event.text.startswith("-100"):  # Check for valid group ID format
        user_id = event.sender_id
        group_id = event.text.strip()

        invite_link = await generate_invite(group_id, user_id)
        await event.reply(f"🎟 Your invite link:\n{invite_link}\n\n⚠ You can generate a new invite link for this group after **1 hour**. If you need a new invite link sooner, please contact the group admin @amber_66n.")

# Automatically delete service messages (Bot added, Join/Leave messages)
@client.on(events.ChatAction)
async def delete_service_messages(event):
    if event.user_added or event.user_joined or event.user_left:
        await asyncio.sleep(1)  # Wait 1 second before deleting
        await client(DeleteMessagesRequest(event.chat_id, [event.action_message.id]))

    # If the bot itself was added, delete the message
    elif event.user_id == (await client.get_me()).id:
        await asyncio.sleep(1)  # Wait 1 second
        await client(DeleteMessagesRequest(event.chat_id, [event.action_message.id]))

# Fancy message when using the /wipeout command
@client.on(events.NewMessage(pattern="^/wipeout$"))
async def wipeout_service_messages(event):
    if event.is_group:
        await event.reply("🧹 **From now on, I'll delete all service messages automatically!**\nNo more spam in the chat! 🚀")

# Help command for admins
@client.on(events.NewMessage(pattern="^/adminhelp$"))
async def admin_help(event):
    if event.is_group:
        await event.reply("🛠 **Admin Commands:**\n\n"
                          "🔹 `/wipeout` → **Enable automatic service message deletion**.\n"
                          "🔹 `/invite` → **Generate invite links in DM**.\n\n"
                          "👮 **Only admins should use these commands!**")

print("✅ Bot is running...")
client.run_until_disconnected()

