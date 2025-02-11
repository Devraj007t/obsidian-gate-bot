from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest
import os
import asyncio
import time

# Load API credentials from environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))  # Ensure it's an integer
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("⚠ API credentials or bot token not set. Please check your environment variables.")

# Store invite request times per group (user_id -> {group_id: timestamp})
user_invites = {}  # {user_id: {group_id: last_request_time}}

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to generate a unique invite link
async def generate_invite(group_id, user_id):
    current_time = time.time()

    # Ensure user has a record in the dictionary
    if user_id not in user_invites:
        user_invites[user_id] = {}

    # Check if the user requested an invite for this group in the last hour
    last_request_time = user_invites[user_id].get(group_id, 0)
    time_left = 3600 - (current_time - last_request_time)  # 3600 seconds = 1 hour
    
    if time_left > 0:
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        return f"⚠ You can generate a new invite link for this group after {minutes}m {seconds}s.\nIf urgent, contact the group admin @amber_66n."

    try:
        peer = await client.get_entity(int(group_id))  # Ensure valid peer
        invite = await client(ExportChatInviteRequest(
            peer=peer,
            usage_limit=1  # One-time use
        ))

        # Update timestamp for this group
        user_invites[user_id][group_id] = current_time

        return invite.link
    except Exception as e:
        print(f"Error generating invite link: {str(e)}")
        return f"⚠️ Failed to generate an invite link: {str(e)}"

# Auto-delete bot's "✅ Bot added" message after 1 second
@client.on(events.ChatAction)
async def on_chat_action(event):
    if event.user_added and event.user_id == (await client.get_me()).id:
        message = await event.reply(f"✅ Bot added to {event.chat.title}!\n📌 Group ID: {event.chat_id}")
        
        # Wait for 1 second before deleting the message
        await asyncio.sleep(1)
        
        # Delete the message
        await client.delete_messages(event.chat_id, message.id)

# Command to request an invite link in DM
@client.on(events.NewMessage(pattern="^/invite$"))
async def request_group_id(event):
    if event.is_private:  # Ensure it's a private chat
        await event.reply("🔹 Please send me the group ID where you want an invite link (Example: -1001234567890).")

# Handle user's group ID response
@client.on(events.NewMessage())
async def send_invite(event):
    if event.is_private and event.text.startswith("-100"):  # Check for valid group ID format
        user_id = event.sender_id
        group_id = event.text.strip()

        invite_link = await generate_invite(group_id, user_id)
        await event.reply(f"🎟 Your invite link:\n{invite_link}\n\n⚠ You can generate a new invite link for this group after 1 hour. If urgent, contact the group admin @amber_66n.")

print("✅ Bot is running...")
client.run_until_disconnected()
