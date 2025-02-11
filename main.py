from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest
import os

# Load API credentials from environment variables
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))  # Ensure it's an integer
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("⚠ API credentials or bot token not set. Please check your environment variables.")

# Store user invite requests
user_invites = {}  # {user_id: [group_id1, group_id2]}

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to generate a unique invite link
async def generate_invite(group_id, user_id):
    if user_id in user_invites and group_id in user_invites[user_id]:
        return "⚠ You can generate an invite link for a group only once. If you need a new invite link, please contact the group admin @amber_66n."

    try:
        group_id = int(group_id)  # Ensure group_id is an integer
        peer = await client.get_entity(group_id)  # Convert to valid peer
        invite = await client(ExportChatInviteRequest(
            peer=peer,
            usage_limit=1  # One-time use
        ))
        if user_id not in user_invites:
            user_invites[user_id] = []
        user_invites[user_id].append(group_id)
        return invite.link
    except Exception as e:
        print(f"Error generating invite link: {str(e)}")
        return f"⚠️ Failed to generate an invite link: {str(e)}"

# Command to request an invite link in DM
@client.on(events.NewMessage(pattern="^/invite$"))
async def request_group_id(event):
    if event.is_private:  # Ensure it's a private chat
        await event.reply("🔹 Please send me the **group ID** where you want an invite link (Example: `-1001234567890`).")

# Handle the user's group ID response
@client.on(events.NewMessage())
async def send_invite(event):
    if event.is_private and event.text.startswith("-100"):  # Check for valid group ID format
        user_id = event.sender_id
        group_id = event.text.strip()

        invite_link = await generate_invite(group_id, user_id)
        await event.reply(f"🎟 Your invite link:\n{invite_link}\n\n⚠ You can generate an invite link for a group only once. If you need a new invite link, please contact the group admin @amber_66n.")

print("✅ Bot is running...")
client.run_until_disconnected()

