from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest, DeleteMessagesRequest
from telethon.tl.types import MessageService
import os
import asyncio
import time

# Load API credentials from environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("⚠ API credentials or bot token not set. Please check your environment variables.")

# Dictionary to track invite requests (user_id: {group_id: last_request_time})
user_invites = {}

# Dictionary to track wipeout-enabled groups
wipeout_enabled = set()

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)


### Function to generate a unique invite link ###
async def generate_invite(group_id, user_id):
    now = time.time()

    # Convert group_id to integer
    try:
        group_id = int(group_id)
    except ValueError:
        return "⚠ Invalid Group ID! Please send a correct group ID (e.g., -1001234567890)."

    # Check if user has already generated an invite link for this group within the last hour
    if user_id in user_invites and group_id in user_invites[user_id]:
        last_request = user_invites[user_id][group_id]
        time_diff = now - last_request
        if time_diff < 3600:
            wait_time = int(3600 - time_diff)
            return f"⚠ You can generate a new invite link for this group after {wait_time} seconds. Please wait."

    try:
        peer = await client.get_entity(group_id)
        invite = await client(ExportChatInviteRequest(peer=peer, usage_limit=1))

        # Update user's invite request time
        if user_id not in user_invites:
            user_invites[user_id] = {}
        user_invites[user_id][group_id] = now

        return f"🎟 Your invite link:\n{invite.link}\n\n⚠ You can generate a new invite link for a group every 1 hour."
    except Exception as e:
        return f"⚠ Failed to generate an invite link: {str(e)}"


### Command to request an invite link in DM ###
@client.on(events.NewMessage(pattern="^/invite$"))
async def request_group_id(event):
    if event.is_private:
        await event.reply("🔹 Please send me the group ID where you want an invite link (Example: -1001234567890).")


### Handle user's group ID response ###
@client.on(events.NewMessage())
async def send_invite(event):
    if event.is_private and event.text.startswith("-100"):
        user_id = event.sender_id
        group_id = event.text.strip()

        invite_link = await generate_invite(group_id, user_id)
        await event.reply(invite_link)


### Command to enable wipeout mode ###
@client.on(events.NewMessage(pattern="^/wipeout$"))
async def enable_wipeout(event):
    chat_id = event.chat_id

    # Check if the user is an admin
    user = await client.get_permissions(chat_id, event.sender_id)
    if not user.is_admin:
        await event.reply("⚠ Only group admins can enable service message deletion.")
        return

    wipeout_enabled.add(chat_id)
    await event.reply("🧹 From now on, I'll delete all service messages automatically! 🚀")


### Delete service messages when wipeout is enabled ###
@client.on(events.NewMessage())
async def auto_delete_service_messages(event):
    chat_id = event.chat_id

    # Check if wipeout is enabled for this group
    if chat_id in wipeout_enabled and isinstance(event.message, MessageService):
        try:
            await client(DeleteMessagesRequest(chat_id, [event.message.id]))
        except Exception as e:
            print(f"Error deleting service message: {str(e)}")


### Start the bot ###
print("✅ Bot is running...")
client.run_until_disconnected()

