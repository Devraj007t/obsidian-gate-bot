from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest

# API Credentials
API_ID = 25737227 
API_HASH = "08827a15f8d9141591806e51e5614a32"
BOT_TOKEN = "7518120312:AAG0zraxb6q-iv2ZdbdUg1Z9v4ye2aI_URo"
GROUP_ID = -1002332542742  # Replace with your actual Group ID

# Initialize the bot
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dictionary to track users who have already received an invite
used_invites = {}

# Function to generate a unique invite link
async def generate_invite():
    try:
        invite = await client(ExportChatInviteRequest(
            peer=GROUP_ID,
            usage_limit=1  # The link expires after one use
        ))
        return invite.link
    except Exception as e:
        return f"Error: {str(e)}"

# Command to generate an invite link
@client.on(events.NewMessage(pattern="^/invite$"))
async def send_invite(event):
    user_id = event.sender_id

    # Check if user has already received an invite
    if user_id in used_invites:
        await event.reply("⚠️ You have already received an invite link. You can't generate more!")
    else:
        invite_link = await generate_invite()
        if "Error" not in invite_link:
            used_invites[user_id] = invite_link  # Store user ID to prevent multiple invites
            await event.reply(f"🎟 Here is your one-time invite link:\n{invite_link}")
        else:
            await event.reply("⚠️ Failed to generate an invite link. Please try again later.")

print("✅ Bot is running...")
client.run_until_disconnected()
