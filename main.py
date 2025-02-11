from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest
import os

# Load API credentials from environment variables
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Convert API_ID to integer
if API_ID:
    API_ID = int(API_ID)  # Convert string to integer

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
        invite = await client(ExportChatInviteRequest(
            peer=int(group_id),  # Ensure group_id is an integer
            usage_limit=1  # One-time use
        ))
        if user_id not in user_invites:
            user_invites[user_id] = []
        user_invites[user_id].append(group_id)
        return invite.link
    except Exception as e:
        print(f"Error generating invite link: {str(e)}")
        return f"⚠️ Failed to generate an invite link: {str(e)}"

# Command to generate an invite link
@client.on(events.NewMessage(pattern="^/invite$"))
async def send_invite(event):
    chat_id = event.chat_id  # Detects which group the command is used in
    user_id = event.sender_id  # Detects which user requested

    invite_link = await generate_invite(chat_id, user_id)
    
    # Sending the invite link along with the restriction message
    await event.reply(f"🎟 Your invite link:\n{invite_link}\n\n⚠ You can generate an invite link for a group only once. If you need a new invite link, please contact the group admin @amber_66n.")

print("✅ Bot is running...")
client.run_until_disconnected()
