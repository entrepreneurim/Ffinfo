#!/usr/bin/env python3

import requests
import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackContext, CallbackQueryHandler
)
from datetime import datetime

BOT_TOKEN = os.environ.get("7221834297:AAFg7BL9YgPLKwg7_wN4bkgmVjqIRDAeX7s")  # Koyeb env var
FORCE_JOIN_CHANNEL = "AxomBotz"
ADMIN_ID = 6987158459

USER_FILE = "users.json"

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

def format_date(timestamp):
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %B %Y, %I:%M %p")
    except:
        return timestamp

async def is_member(user_id, bot):
    try:
        chat_member = await bot.get_chat_member(f"@{FORCE_JOIN_CHANNEL}", user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat.id
    first_name = update.message.chat.first_name
    bot = context.bot

    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = first_name
        save_users(users)

    if not await is_member(user_id, bot):
        await update.message.reply_text(
            f"🚨 To use this bot, please join @{FORCE_JOIN_CHANNEL} first!\n\n"
            "🔹 After joining, click /start again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔥 Join Channel 🔥", url=f"https://t.me/{FORCE_JOIN_CHANNEL}")]
            ]),
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Statistics", callback_data="stats")],
    ])

    await update.message.reply_text(
        f"👋 Hello {first_name}, send your <b>Free Fire UID</b> to get details.",
        reply_markup=keyboard, parse_mode="HTML"
    )

async def fetch_ff_details(update: Update, context: CallbackContext):
    uid = update.message.text.strip()

    if not uid.isdigit():
        await update.message.reply_text("❌ Invalid UID! Please send a numeric Free Fire UID.")
        return

    url = f"https://ff-info-drsudo.vercel.app/api/player-info?id={uid}"
    response = requests.get(url).json()

    if response["status"] != "success":
        await update.message.reply_text("⚠️ Player not found. Please check the UID and try again.")
        return

    data = response["data"]
    basic_info = data["basic_info"]
    guild = data.get("Guild", {})

    created_date = format_date(basic_info["account_created"])

    reply_text = f"""
🎮 <b>Free Fire Player Details</b> 🎮

👤 <b>Name:</b> {basic_info["name"]}
🆔 <b>UID:</b> <code>{basic_info["id"]}</code>
🔝 <b>Level:</b> {basic_info["level"]}
❤️ <b>Likes:</b> {basic_info["likes"]}
🌍 <b>Server:</b> {basic_info["server"]}
📅 <b>Account Created:</b> {created_date}

🏆 <b>Booyah Pass Level:</b> {basic_info["booyah_pass_level"]}

🏰 <b>Guild Details</b> 🏰
🔹 <b>Name:</b> {guild.get("name", "No Guild")}
🔹 <b>Level:</b> {guild.get("level", "N/A")}
🔹 <b>Members:</b> {guild.get("members_count", "N/A")}
🔹 <b>Leader:</b> {guild.get("leader", {}).get("name", "N/A")}

📝 <b>Bio:</b> {basic_info.get("bio", "No Bio")}
"""
    await update.message.reply_text(reply_text, parse_mode="HTML")

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "stats":
        users = load_users()
        total_users = len(users)
        await query.answer()
        await query.message.reply_text(f"📊 <b>Bot Statistics</b>\n\n👥 Total Users: <b>{total_users}</b>", parse_mode="HTML")

async def broadcast(update: Update, context: CallbackContext):
    user_id = update.message.chat.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("📢 Send a message to broadcast using: `/broadcast Your Message`")
        return

    message = " ".join(context.args)
    users = load_users()
    failed = 0

    for uid in users.keys():
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 <b>Announcement from Admin:</b>\n\n{message}", parse_mode="HTML")
        except:
            failed += 1

    await update.message.reply_text(f"✅ Broadcast sent to {len(users) - failed} users.\n❌ Failed to deliver to {failed} users.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast, filters=filters.User(ADMIN_ID)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_ff_details))
    app.add_handler(CallbackQueryHandler(button_handler))

    PORT = int(os.environ.get("PORT", 8080))
    WEBHOOK_URL = f"https://{os.environ.get('scared-marj-okbos-e9e754a7')}.koyeb.app/{BOT_TOKEN}"

    print("✅ Starting bot with webhook...")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
