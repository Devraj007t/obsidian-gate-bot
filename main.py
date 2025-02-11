from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest

# Your API Credentials
api_id = 25737227
api_hash = "08827a15f8d9141591806e51e5614a32"
bot_token = "7518120312:AAG0zraxb6q-iv2ZdbdUg1Z9v4ye2aI_URo"

# Initialize the bot
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Dictionary to store users who have already received an invite
user_invites = {}

# Event to detect new groups and store group IDs
@bot.on(events.ChatAction)
async def handler(event):
    if event.user_added or event.user_joined and event.is_group:
        group_id = event.chat_id
        group_name = event.chat.title or "Unknown Group"
        print(f"✅ Bot added to a new group: {group_name} (ID: {group_id})")

        # Save Group ID
        with open("group_ids.txt", "a") as f:
            f.write(f"{group_id} - {group_name}\n")

        await event.respond(f"✅ Bot successfully added to {group_name}!\n📌 Group ID: {group_id}")

# Event to generate a one-time invite link when someone types /invite
@bot.on(events.NewMessage(pattern='/invite'))
async def invite_handler(event):
    user_id = event.sender_id
    chat_id = event.chat_id

    # Check if the user has already requested an invite
    if user_id in user_invites:
        await event.respond("⚠️ You have already received an invite link. You can't generate more!")
        return

    try:
        # Generate a single-use invite link
        invite = await bot(ExportChatInviteRequest(
            peer=chat_id,
            usage_limit=1,  # Allow only one person to join
            expire_date=None  # No expiration time (optional)
        ))

        invite_link = invite.link

        # Store that the user has received an invite
        user_invites[user_id] = invite_link

        await event.respond(f"🔗 Here is your one-time invite link:\n{invite_link}\n⚠️ This link can only be used once!")

    except Exception as e:
        await event.respond("⚠️ Failed to generate invite link. Make sure the bot is an admin.")

# Start the bot
print("🤖 Bot is running...")
bot.run_until_disconnected()
