from telethon import TelegramClient, events
from telethon.tl.functions.messages import ExportChatInviteRequest, DeleteMessagesRequest, GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsAdmins
import os
import asyncio

# Load API credentials
API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("⚠ API credentials or bot token not set. Please check your environment variables.")

client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

wipeout_enabled_groups = set()  # Store groups that enabled /wipeout

# ✅ Automatically Delete Service Messages (Join/Leave/Bot Added)
@client.on(events.ChatAction)
async def delete_service_messages(event):
    if event.chat_id in wipeout_enabled_groups and event.action_message:
        try:
            await asyncio.sleep(1)
            await client(DeleteMessagesRequest(event.chat_id, [event.action_message.id]))
        except Exception as e:
            print(f"⚠ Failed to delete service message: {e}")

# ✅ Enable Auto-Delete with /wipeout (Admins & Owner Only)
@client.on(events.NewMessage(pattern="^/wipeout$"))
async def wipeout_service_messages(event):
    if event.is_group and event.sender_id in await get_admins_and_owner(event.chat_id):
        wipeout_enabled_groups.add(event.chat_id)
        await event.reply("🧹 **From now on, I'll delete all service messages automatically!**\nNo more spam in the chat! 🚀")
    else:
        await event.reply("⚠ **Only group admins or the owner can use this command!**")

# ✅ Get Admins & Owner List
async def get_admins_and_owner(chat_id):
    admins = set()
    async for admin in client.iter_participants(chat_id, filter=ChannelParticipantsAdmins):
        admins.add(admin.id)
    return admins

# ✅ Generate Invite Link Feature (Users Can Generate Again After 1 Hour)
user_invites = {}  # Store invite timestamps {user_id: {group_id: timestamp}}

async def generate_invite(group_id, user_id):
    now = asyncio.get_event_loop().time()
    if user_id in user_invites and group_id in user_invites[user_id]:
        last_request = user_invites[user_id][group_id]
        if now - last_request < 3600:  # 1 Hour (3600 Seconds)
            return "⚠ You can generate a new invite link for this group only after 1 hour. Please wait."

    try:
        group_id = int(group_id)
        peer = await client.get_entity(group_id)
        invite = await client(ExportChatInviteRequest(peer=peer, usage_limit=1))

        if user_id not in user_invites:
            user_invites[user_id] = {}
        user_invites[user_id][group_id] = now  # Store timestamp

        return invite.link
    except Exception as e:
        return f"⚠ Failed to generate an invite link: {str(e)}"

# ✅ Command to Request an Invite Link in DM
@client.on(events.NewMessage(pattern="^/invite$"))
async def request_group_id(event):
    if event.is_private:
        await event.reply("🔹 **Send me the group ID where you want an invite link (Example: -1001234567890).**")

# ✅ Handle User's Group ID Response (DM Only)
@client.on(events.NewMessage())
async def send_invite(event):
    if event.is_private and event.text.startswith("-100"):
        user_id = event.sender_id
        group_id = event.text.strip()

        invite_link = await generate_invite(group_id, user_id)
        await event.reply(f"🎟 **Your invite link:**\n{invite_link}\n\n⚠ You can generate a new invite link for this group only after 1 hour.")

print("✅ Bot is running...")
client.run_until_disconnected()

