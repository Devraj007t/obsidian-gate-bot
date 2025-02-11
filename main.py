from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest

# Your API Credentials
api_id = 25737227
api_hash = "08827a15f8d9141591806e51e5614a32"
bot_token = "7518120312:AAG0zraxb6q-iv2ZdbdUg1Z9v4ye2aI_URo"

# Manually Set Your Private Group ID
PRIVATE_GROUP_ID = -1002332542742  # Replace this with your real group ID

# Initialize the bot
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Dictionary to track users who have already received an invite
user_invites = {}

# Event to handle /invite command
@bot.on(events.NewMessage(pattern='/invite'))
async def invite_handler(event):
    user_id = event.sender_id

    # Check if the user has already received an invite
    if user_id in user_invites:
        await event.respond("⚠️ You have already received an invite link. You can't generate more!")
        return

    try:
        # Generate a single-use invite link for the manually set group ID
        invite = await bot(ExportChatInviteRequest(
            peer=PRIVATE_GROUP_ID,  # Use the manually set group ID
            usage_limit=1,  # Allow only one person to join
            expire_date=None  # No expiration time (optional)
        ))

        invite_link = invite.link

        # Store that the user has received an invite
        user_invites[user_id] = invite_link

        await event.respond(f"🔗 Here is your one-time invite link:\n{invite_link}\n⚠️ This link can only be used once!")

    except Exception as e:
        await event.respond(f"⚠️ Failed to generate invite link. Error: {str(e)}")

# Start the bot
print("🤖 Bot is running...")
bot.run_until_disconnected()
