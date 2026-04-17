#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import random
import datetime
import telebot
from telebot import types

# ================= CONFIG =================
API_TOKEN = os.getenv("8224596860:AAGnZj9hYF9uvuJE7JKnWhduALOaqRP4C8I")

if not API_TOKEN:
    raise ValueError("❌ BOT_TOKEN not set!")

# 👉 Multiple channels
CHANNELS = [
    "@primiumboss29",
    "@saniedit9"
]

ADMIN_USERNAME = "@jiolinhacker"

DEFAULT_VIDEO_LIMIT = 3
DEFAULT_LOC_LIMIT = 5

REF_BONUS = 2  # referral এ extra limit

DB_FILE = "bot_data.json"

# ================= DB =================
def load_db():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_data = load_db()

# ================= USER =================
def get_user(chat_id):
    chat_id = str(chat_id)

    if chat_id not in user_data:
        user_data[chat_id] = {
            "ref": f"REF{random.randint(1000,9999)}",
            "ref_by": None,
            "bonus": 0,
            "is_premium": False,
            "video": 0,
            "loc": 0,
            "date": str(datetime.date.today())
        }
        save_db(user_data)

    return user_data[chat_id]

def reset_daily(user):
    today = str(datetime.date.today())
    if user["date"] != today:
        user["video"] = 0
        user["loc"] = 0
        user["date"] = today

# ================= JOIN CHECK =================
def is_joined(chat_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, chat_id)
            if member.status not in ["member", "creator", "administrator"]:
                return False
        except:
            return False
    return True

def join_markup():
    m = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        m.add(types.InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch.replace('@','')}"))
    m.add(types.InlineKeyboardButton("✅ Verify", callback_data="verify"))
    return m

# ================= BOT =================
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    chat_id = msg.chat.id
    args = msg.text.split()

    user = get_user(chat_id)

    # 👉 Referral system
    if len(args) > 1:
        ref_code = args[1]
        if not user["ref_by"]:
            for uid, data in user_data.items():
                if data["ref"] == ref_code and uid != str(chat_id):
                    user["ref_by"] = uid
                    user_data[uid]["bonus"] += REF_BONUS
                    save_db(user_data)
                    break

    if not is_joined(chat_id):
        bot.send_message(chat_id, "❌ Join all channels first!", reply_markup=join_markup())
        return

    reset_daily(user)

    bot.send_message(chat_id, "👋 Welcome!", reply_markup=main_menu())

# ================= MENU =================
def main_menu():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🎬 Video", callback_data="video"))
    m.add(types.InlineKeyboardButton("📍 Location", callback_data="loc"))
    m.add(types.InlineKeyboardButton("👥 Referral", callback_data="ref"))
    return m

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)
    reset_daily(user)

    # 🔁 Auto recheck
    if not is_joined(chat_id):
        bot.send_message(chat_id, "❌ Join required!", reply_markup=join_markup())
        return

    # VERIFY
    if call.data == "verify":
        if is_joined(chat_id):
            bot.send_message(chat_id, "✅ Verified!")
            bot.send_message(chat_id, "🎉 Access granted", reply_markup=main_menu())
        else:
            bot.send_message(chat_id, "❌ এখনও join করেননি!")

    # VIDEO
    elif call.data == "video":
        limit = DEFAULT_VIDEO_LIMIT + user["bonus"]

        if not user["is_premium"] and user["video"] >= limit:
            bot.send_message(chat_id, "❌ Limit finished!")
            return

        msg = bot.send_message(chat_id, "Send video link:")
        bot.register_next_step_handler(msg, process_video)

    # LOCATION
    elif call.data == "loc":
        limit = DEFAULT_LOC_LIMIT + user["bonus"]

        if not user["is_premium"] and user["loc"] >= limit:
            bot.send_message(chat_id, "❌ Limit finished!")
            return

        bot.send_message(chat_id, f"📍 Admin: https://t.me/{ADMIN_USERNAME}")
        user["loc"] += 1
        save_db(user_data)

    # REFERRAL
    elif call.data == "ref":
        link = f"https://t.me/YOUR_BOT_USERNAME?start={user['ref']}"
        bot.send_message(
            chat_id,
            f"👥 Referral Link:\n{link}\n\n🎁 Bonus: {user['bonus']}"
        )

# ================= DOWNLOAD =================
def process_video(msg):
    chat_id = msg.chat.id
    user = get_user(chat_id)

    link = msg.text.strip()

    if not link.startswith("http"):
        bot.send_message(chat_id, "❌ Invalid link")
        return

    bot.send_message(chat_id, "⏳ Downloading...")

    try:
        import yt_dlp

        file = f"{chat_id}.mp4"

        with yt_dlp.YoutubeDL({"outtmpl": file, "quiet": True}) as ydl:
            ydl.download([link])

        with open(file, "rb") as f:
            bot.send_video(chat_id, f)

        os.remove(file)

        if not user["is_premium"]:
            user["video"] += 1
            save_db(user_data)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {e}")

# ================= RUN =================
print("🚀 Bot running...")
bot.infinity_polling(skip_pending=True)
