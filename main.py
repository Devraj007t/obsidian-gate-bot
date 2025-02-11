from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest

# Your API Credentials
api_id = 25737227
api_hash = "08827a15f8d9141591806e51e5614a32"
bot_token = "7518120312:AAG0zraxb6q-iv2ZdbdUg1Z9v4ye2aI_URo"

# Initialize the bot
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Dictionary to track users who have already received an invite
user_invites = {}

# File to store the detected group ID
GROUP_ID_FILE = "group_id.txt"

# Function to save detected group ID
def save_group_id(group_id):
    with open(GROUP_ID_FILE, "w") as f:
        f.write(str(group_id))

# Function to read the stored group ID
def get_saved_group_id():
    try:
        with open(GROUP_ID_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return None

# Auto-detect group ID when bot is added
@bot.on(events.ChatAction)
async def group_handler(event):
    if event.is_group and event.chat_id:
        group_id = event.chat_id
        save_group_id(group_id)
        print(f"✅ Bot added to group: {event.chat.title} (ID: {group_id})")
        await event.respond(f"✅ Bot detected this group!\n📌 Group ID: {group_id}")

# Generate a one-time invite link when user sends /invite
@bot.on(events.NewMessage(pattern='/invite'))
async def invite_handler(event):
    user_id = event.sender_id
    chat_id = get_saved_group_id()

    if not chat_id:
        await event.respond("⚠️ No group detected. Add the bot to a group first!")
        return

    # Check if the user has already received an invite
    if user_id in user_invites:
        await event.respond("⚠️ You have already received an invite link. You can't generate more!")
        return

    try:
        # Generate a one-time invite link
        invite = await bot(ExportChatInviteRequest(
            peer=chat_id,  
            usage_limit=1,  
            expire_date=None  
        ))

        invite_link = invite.link
        user_invites[user_id] = invite_link  

        await event.respond(f"🔗 Here is your one-time invite link:\n{invite_link}\n⚠️ This link can only be used once!")

    except Exception as e:
        await event.respond(f"⚠️ Failed to generate invite link. Make sure the bot is an admin.\nError: {str(e)}")

# Start the bot
print("🤖 Bot is running...")
bot.run_until_disconnected()

