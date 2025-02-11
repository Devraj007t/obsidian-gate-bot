if deleted_count > 0:
            await event.reply("🧹 Cleanup complete! From now on, I'll delete all service messages automatically. 🚀")
        else:
            await event.reply("🤷 No bot service messages found to delete.")

# Auto-delete bot service messages
@client.on(events.NewMessage())
async def auto_delete_bot_message(event):
    if event.is_group and event.sender_id == (await client.get_me()).id:
        if "✅ Bot added to" in event.raw_text and "📌 Group ID:" in event.raw_text:
            await asyncio.sleep(1)  # Wait 1 second
            await client.delete_messages(event.chat_id, event.message.id)

# Help command for new admins
@client.on(events.NewMessage(pattern="^/help$"))
async def help_command(event):
    if event.is_group:
        await event.reply(
            "🔹 Available Commands 🔹\n\n"
            "/invite - Get an invite link for a group (in DM only)\n"
            "/wipeout - 🧹 Delete all bot service messages (Admins Only)\n"
            "/help - Show this command list"
        )

print("✅ Bot is running...")
client.run_until_disconnected()
