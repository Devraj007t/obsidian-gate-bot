from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import (
    ChannelParticipantAdmin, 
    ChannelParticipantCreator, 
    MessageActionChatAddUser, 
    MessageActionChatJoinedByLink, 
    MessageActionChatDeleteUser
)
import os

# Load API credentials from environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))  # Ensure it's an integer
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("⚠ API credentials or bot token not set. Please check your environment variables.")

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Store enabled groups for service message deletion
wipeout_enabled_groups = set()

# Function to check if a user is an admin
async def is_admin(group_id, user_id):
    try:
        participant = await client(GetParticipantRequest(group_id, user_id))
        return isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
    except Exception as e:
        print(f"⚠ Error checking admin status: {e}")
        return False

# Command to enable service message deletion
@client.on(events.NewMessage(pattern="^/wipeout$"))
async def enable_wipeout(event):
    chat_id = event.chat_id
    sender_id = event.sender_id

    # Check if the user is an admin
    if not await is_admin(chat_id, sender_id):
        await event.reply("🚫 Only admins can enable service message deletion!")
        return

    wipeout_enabled_groups.add(chat_id)
    await event.reply("🧹 From now on, I'll delete all service messages automatically! 🚀")

# Detect service messages and delete them
@client.on(events.ChatAction)
async def delete_service_messages(event):
    chat_id = event.chat_id

    # Check if wipeout is enabled for this group
    if chat_id not in wipeout_enabled_groups:
        return

    if isinstance(event.action_message.action, (MessageActionChatAddUser, MessageActionChatJoinedByLink, MessageActionChatDeleteUser)):
        try:
            await event.delete()
            print(f"✅ Deleted service message in {chat_id}")
        except Exception as e:
            print(f"⚠ Failed to delete service message in {chat_id}: {str(e)}")

print("✅ Bot is running without crashes...")
client.run_until_disconnected()

