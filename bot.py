#!/usr/bin/env python3

import requests
import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from datetime import datetime

BOT_TOKEN = "7221834297:AAGjlEp-qhgxwLRjNosFXG-dZHsVBfSyvQY"
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
    basic = data["basic_info"]
    guild = data.get("Guild", {})
    pet = data.get("Pet", {})
    activity = data.get("Account_activity", {})
    leader = guild.get("leader", {})

    reply_text = f"""
🔹 <b>ACCOUNT INFO:</b>

👤 <b>BASIC INFO</b>
├─ <b>Name:</b> {basic["name"]}
├─ <b>UID:</b> <code>{basic["id"]}</code>
├─ <b>Level:</b> {basic["level"]} (Exp: {basic.get("exp", "N/A")})
├─ <b>Region:</b> {basic.get("server", "N/A")}
├─ <b>Likes:</b> {basic.get("likes", "N/A")}
├─ <b>Honor Score:</b> {basic.get("honor_score", "N/A")}
├─ <b>Celebrity Status:</b> {basic.get("is_celeb", "No")}
├─ <b>Evo Access Badge:</b> {basic.get("evo_badge", "Inactive")}
├─ <b>Signature:</b> {basic.get("bio", "No Signature")}
└─ <b>Last Login:</b> {format_date(basic.get("last_login", "N/A"))}

🎮 <b>ACCOUNT ACTIVITY</b>
├─ <b>Fire Pass:</b> {activity.get("fire_pass", "N/A")}
├─ <b>Current BP Badges:</b> {activity.get("bp_badges", "N/A")}
├─ <b>BR Rank:</b> {activity.get("br_rank", "N/A")}
├─ <b>CS Points:</b> {activity.get("cs_rank_points", "N/A")}
└─ <b>Created At:</b> {format_date(basic["account_created"])}

🐾 <b>PET DETAILS</b>
├─ <b>Equipped?:</b> {"Yes" if pet else "No"}
├─ <b>Pet Name:</b> {pet.get("name", "N/A")}
├─ <b>Pet Type:</b> {pet.get("type", "N/A")}
├─ <b>Pet Exp:</b> {pet.get("exp", "N/A")}
└─ <b>Pet Level:</b> {pet.get("level", "N/A")}

🛡️ <b>GUILD INFO</b>
├─ <b>Guild Name:</b> {guild.get("name", "No Guild")}
├─ <b>Guild ID:</b> {guild.get("id", "N/A")}
├─ <b>Guild Level:</b> {guild.get("level", "N/A")}
├─ <b>Live Members:</b> {guild.get("members_count", "N/A")}
└─ <b>Leader Info:</b>
    ├─ <b>Leader Name:</b> {leader.get("name", "N/A")}
    ├─ <b>Leader UID:</b> {leader.get("id", "N/A")}
    ├─ <b>Leader Level:</b> {leader.get("level", "N/A")}
    ├─ <b>Leader Created At:</b> {format_date(leader.get("account_created", "N/A"))}
    └─ <b>Leader Last Login:</b> {format_date(leader.get("last_login", "N/A"))}

🗺️ <b>PUBLIC CRAFTLAND MAPS</b>
<code>{data.get("craftland_maps", "No Maps Available")}</code>

🎁 <b>FF INFORMATION BY -</b>
├─• Telegram: @URxFF
└─• Instagram: @6_hf0
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

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
