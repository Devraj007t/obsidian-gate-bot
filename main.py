from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest

# API Credentials
API_ID = 25737227
API_HASH = "08827a15f8d9141591806e51e5614a32"
BOT_TOKEN = "7518120312:AAG0zraxb6q-iv2ZdbdUg1Z9v4ye2aI_URo"

# Store user invite requests
user_invites = {}  # {user_id: [group_id1, group_id2]}

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to generate a unique invite link
async def generate_invite(group_id, user_id):
    if user_id in user_invites and group_id in user_invites[user_id]:
        return "⚠ You have already generated an invite link for this group."

    try:
        invite = await client(ExportChatInviteRequest(
            peer=group_id,
            usage_limit=1  # One-time use
        ))
        if user_id not in user_invites:
            user_invites[user_id] = []
        user_invites[user_id].append(group_id)
        return invite.link
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
