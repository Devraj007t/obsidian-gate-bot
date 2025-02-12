from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest, DeleteMessagesRequest
import os
import asyncio
import time

# Load API credentials from environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))  # Ensure it's an integer
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("⚠ API credentials or bot token not set. Please check your environment variables.")

# Store user invite requests with timestamps
user_invites = {}  # {user_id: {group_id: timestamp}}

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to generate a unique invite link
async def generate_invite(group_id, user_id):
    current_time = time.time()

    # If user has requested an invite link for this group before
    if user_id in user_invites and group_id in user_invites[user_id]:
        last_request_time = user_invites[user_id][group_id]
        time_passed = current_time - last_request_time

        if time_passed < 3600:  # 1 hour in seconds
            remaining_time = int(3600 - time_passed)
            return f"⏳ You can generate a new invite link for this group in {remaining_time} seconds."

    try:
        group_id = int(group_id)  # Ensure group_id is an integer
        peer = await client.get_entity(group_id)  # Convert to valid peer
        invite = await client(ExportChatInviteRequest(
            peer=peer,
            usage_limit=1  # One-time use
        ))

        # Store the timestamp of this invite request
        if user_id not in user_invites:
            user_invites[user_id] = {}
        user_invites[user_id][group_id] = current_time

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
        await event.reply(f"🎟 Your invite link:\n{invite_link}\n\n⚠ You can generate an invite link for a group only once per hour. If you need a new invite link sooner, please contact the group admin @amber_66n.")

# Command to clean bot service messages manually
@client.on(events.NewMessage(pattern="^/wipeout$"))
async def clean_service_messages(event):
    if event.is_group:
        async for message in client.iter_messages(event.chat_id, from_user="me"):
            if "✅ Bot added to" in message.text and "📌 Group ID:" in message.text:
                await client(DeleteMessagesRequest(event.chat_id, [message.id]))
                await event.reply("✅ Wiped out all bot service messages!")
                return

# Auto-delete bot service messages
@client.on(events.NewMessage())
async def auto_delete_bot_message(event):
    if event.is_group and event.sender_id == (await client.get_me()).id:
        if "✅ Bot added to" in event.raw_text and "📌 Group ID:" in event.raw_text:
            await asyncio.sleep(1)  # Wait 1 second
            await client.delete_messages(event.chat_id, event.message.id)

print("✅ Bot is running...")
client.run_until_disconnected()
