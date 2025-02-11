from telethon import TelegramClient, events

# Your API details 
api_id = 25737227 
api_hash = "08827a15f8d9141591806e51e5614a32" 
bot_token = "7518120312:AAG0zraxb6q-iv2ZdbdUg1Z9v4ye2aI_URo" 
# Initialize the bot
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Event to detect new group and store group ID
@bot.on(events.ChatAction)
async def handler(event):
    if event.user_added or event.user_joined and event.is_group:
        group_id = event.chat_id
        group_name = event.chat.title
        print(f"Bot added to a new group: {group_name} (ID: {group_id})")

        # Save the group ID to a file (optional)
        with open("group_ids.txt", "a") as f:
            f.write(f"{group_id} - {group_name}\n")

        await event.respond(f"✅ Bot added to {group_name}!\n📌 Group ID: {group_id}")

print("🤖 Bot is running...")
bot.run_until_disconnected()
