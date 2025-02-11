from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest
import json
import os

# Your API Credentials
api_id = 25737227
api_hash = "08827a15f8d9141591806e51e5614a32"
bot_token = "7518120312:AAG0zraxb6q-iv2ZdbdUg1Z9v4ye2aI_URo"

# File to store group IDs
GROUP_ID_FILE = "group_ids.json"

# Load stored group IDs
if os.path.exists(GROUP_ID_FILE):
    with open(GROUP_ID_FILE, "r") as f:
        try:
            group_ids = json.load(f)
        except json.JSONDecodeError:
            group_ids = {}
else:
    group_ids = {}

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

        # Save Group ID in JSON file
        group_ids[str(group_id)] = group_name
        with open(GROUP_ID_FILE, "w") as f:
            json.dump(group_ids, f, indent=4)

        print(f"✅ Bot added to a new group: {group_name} (ID: {group_id})")
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

    # Get the group ID from stored data
    group_id = str(chat_id)
    if group_id not in group_ids:
        await event.respond("⚠️ This group is not in my database. Make sure the bot was added properly.")
        return

    try:
        # Generate a single-use invite link for the detected group ID
        invite = await bot(ExportChatInviteRequest(
            peer=int(group_id),  # Convert back to integer
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
