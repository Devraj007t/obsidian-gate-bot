from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest, DeleteMessagesRequest
import os
import asyncio
import time

# Load API credentials from environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))  
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("⚠ API credentials or bot token not set. Please check your environment variables.")

# Cooldown system (Stores timestamps of last invite request per group)
user_invites = {}  # {user_id: {group_id: timestamp}}

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to generate a unique invite link with cooldown
async def generate_invite(group_id, user_id):
    current_time = time.time()

    # Check cooldown
    if user_id in user_invites and group_id in user_invites[user_id]:
        last_request_time = user_invites[user_id][group_id]
        time_passed = current_time - last_request_time

        if time_passed < 3600:  # 1 hour cooldown
            remaining_time = int(3600 - time_passed)
            return f"⏳ You can generate a new invite link for this group in {remaining_time} seconds."

    try:
        peer = await client.get_entity(group_id)
        invite = await client(ExportChatInviteRequest(peer=peer, usage_limit=1))

        # Store the timestamp of this invite request
        if user_id not in user_invites:
            user_invites[user_id] = {}
        user_invites[user_id][group_id] = current_time

        return invite.link
    except Exception as e:
        return f"⚠️ Failed to generate an invite link: {str(e)}"

# Command to request an invite link in DM
@client.on(events.NewMessage(pattern="^/invite$"))
async def request_group_id(event):
    if event.is_private:
        await event.reply("🔹 Please send me the group ID where you want an invite link (Example: -1001234567890).")

# Handle the user's group ID response
@client.on(events.NewMessage())
async def send_invite(event):
    if event.is_private and event.text.startswith("-100"):
        user_id = event.sender_id
        group_id = event.text.strip()

        invite_link = await generate_invite(group_id, user_id)
        await event.reply(f"🎟 Your invite link:\n{invite_link}\n\n⚠ You can generate an invite link for a group only once per hour. If you need a new invite link sooner, please contact the group admin @amber_66n.")

# Command to enable auto-deleting service messages (Admins & Owner Only)
@client.on(events.NewMessage(pattern="^/wipeout$"))
async def clean_service_messages(event):
    if event.is_group:
        user = await client.get_permissions(event.chat_id, event.sender_id)
        if user.is_admin or user.is_creator:
            async for message in client.iter_messages(event.chat_id, from_user="me"):
                if "✅ Bot added to" in message.text or "📌 Group ID:" in message.text:
                    await client(DeleteMessagesRequest(event.chat_id, [message.id]))

            await event.reply("🧹 **From now on, I'll delete all service messages automatically! 🚀**")
        else:
            await event.reply("⚠ You must be an **Admin** to use this command.")

# Auto-delete bot service messages (like "Bot added to Bb!")
@client.on(events.NewMessage())
async def auto_delete_bot_message(event):
    if event.is_group and event.sender_id == (await client.get_me()).id:
        if "✅ Bot added to" in event.raw_text or "📌 Group ID:" in event.raw_text:
            await asyncio.sleep(1)  
            await client.delete_messages(event.chat_id, event.message.id)

print("✅ Bot is running...")
client.run_until_disconnected()

