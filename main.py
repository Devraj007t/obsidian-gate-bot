from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.errors.rpcerrorlist import ChatAdminRequiredError, UserAdminInvalidError
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
        return "⚠ You have already generated an invite link for this group."

    try:
        peer = await client.get_entity(group_id)  # Ensures valid peer
        invite = await client(ExportChatInviteRequest(
            peer=peer,
            usage_limit=1  # One-time use
        ))
        if user_id not in user_invites:
            user_invites[user_id] = []
        user_invites[user_id].append(group_id)
        return invite.link

    except ChatAdminRequiredError:
        return "⚠ The bot must be an admin with invite link permissions to generate an invite."
    except UserAdminInvalidError:
        return "⚠ The bot is not an admin in this group. Please make it an admin and try again."
    except Exception as e:
        return f"⚠️ Failed to generate an invite link: {str(e)}"

# Command to generate an invite link
@client.on(events.NewMessage(pattern="^/invite$"))
async def send_invite(event):
    chat_id = event.chat_id  # Detects which group the command is used in
    user_id = event.sender_id  # Detects which user requested

    invite_link = await generate_invite(chat_id, user_id)
    await event.reply(f"🎟 Your invite link:\n{invite_link}")

print("✅ Bot is running...")
client.run_until_disconnected()

