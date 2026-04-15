#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram bot that offers free / premium video & location services.
Author:  White Hack Labs
"""

# ──────────────────────────────────────────────────────
# 1️⃣  Imports
# ──────────────────────────────────────────────────────
import json
import os
import random
import datetime
from typing import Dict

import telebot
from telebot import types

# ──────────────────────────────────────────────────────
# 2️⃣  Configuration (replace placeholders!)
# ──────────────────────────────────────────────────────
API_TOKEN      = "8224596860:AAGnZj9hYF9uvuJE7JKnWhduALOaqRP4C8I"          # ← Replace
ADMIN_ID       = 8210146346                      # ← Your Telegram user id
CHANNEL_NAME_1 = "@primiumboss29"                # Video challenge channel
CHANNEL_NAME_2 = "@saniedit9"                # Location challenge channel
REF_LINK_BASE  = "https://t.me/YourBot?start="   # Referral link format

# Limits & prices
DEFAULT_VIDEO_LIMIT = 3
DEFAULT_LOC_LIMIT   = 5
PVM_PRICE           = "৫০০ টাকা"

# Database file
DB_FILE = "bot_data.json"

# ──────────────────────────────────────────────────────
# 3️⃣  Helper: persistence
# ──────────────────────────────────────────────────────
def load_db() -> Dict:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_db(data: Dict) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


user_data = load_db()  # global cache


# ──────────────────────────────────────────────────────
# 4️⃣  User helper
# ──────────────────────────────────────────────────────
def get_user(chat_id: int) -> Dict:
    """
    Return a dictionary that represents the user.
    Creates a new entry if the user does not exist yet.
    """
    key = str(chat_id)
    if key not in user_data:
        today = datetime.date.today().strftime("%Y-%m-%d")
        user_data[key] = {
            "ref_code": f"REF{random.randint(1000, 9999)}",
            "ref_by": None,
            "is_premium": False,
            "last_date_video": today,
            "count_video_today": 0,
            "last_date_loc": today,
            "count_loc_today": 0,
            "total_refs": 0,
        }
        save_db(user_data)
    return user_data[key]


def check_and_reset_daily(chat_id: int) -> None:
    """
    Reset daily counters if a new day has started.
    """
    user = get_user(chat_id)
    today = datetime.date.today().strftime("%Y-%m-%d")

    if user["last_date_video"] != today:
        user["count_video_today"] = 0
        user["last_date_video"] = today

    if user["last_date_loc"] != today:
        user["count_loc_today"] = 0
        user["last_date_loc"] = today

    save_db(user_data)


def get_limit_status(chat_id: int) -> str:
    """
    Return a short status string showing the remaining limits.
    """
    user = get_user(chat_id)
    video_left = (
        100 if user["is_premium"] else DEFAULT_VIDEO_LIMIT
    ) - user["count_video_today"]
    loc_left = (
        100 if user["is_premium"] else DEFAULT_LOC_LIMIT
    ) - user["count_loc_today"]

    # Clamp to zero
    video_left = max(video_left, 0)
    loc_left = max(loc_left, 0)

    return (
        f"📊 লিমিট স্ট্যাটাস\n\n"
        f"✅ ভিডিও বাকি: {video_left}\n"
        f"✅ লোকেশন বাকি: {loc_left}\n"
        f"{'💎 প্রিমিয়াম' if user['is_premium'] else '🔹 সাধারণ'}"
    )


# ──────────────────────────────────────────────────────
# 5️⃣  Bot instance
# ──────────────────────────────────────────────────────
bot = telebot.TeleBot(API_TOKEN)


# ──────────────────────────────────────────────────────
# 6️⃣  Markup helpers
# ──────────────────────────────────────────────────────
def get_main_markup(chat_id: int) -> types.InlineKeyboardMarkup:
    """
    Build the main menu markup.
    """
    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(
        types.InlineKeyboardButton("🎬 কপিরাইট ফ্রি ভিডিও", callback_data="menu_video"),
        types.InlineKeyboardButton("📍 লোকেশন বায়/সার্ভিস", callback_data="menu_loc"),
        types.InlineKeyboardButton("🪩 TikTok ভিডিও", callback_data="menu_tiktok"),
    )

    if chat_id == ADMIN_ID:
        markup.add(
            types.InlineKeyboardButton("👑 অডমিন প্যানেল", callback_data="admin_panel")
        )
    else:
        markup.add(
            types.InlineKeyboardButton("💎 প্রিমিয়াম কিনুন", callback_data="pvm_buy"),
            types.InlineKeyboardButton("👥 রেফারেল শেয়ার", callback_data="ref_menu"),
            types.InlineKeyboardButton("👨‍💼 অডমিনের সাথে কথা", callback_data="admin_chat"),
        )
    return markup


# ──────────────────────────────────────────────────────
# 7️⃣  Challenge helper
# ──────────────────────────────────────────────────────
def show_challenge(chat_id: int, type: str | None = None) -> None:
    """
    Notify the user that the limit has been reached and show the challenge channel.
    """
    channel = CHANNEL_NAME_1 if type == "video" else CHANNEL_NAME_2
    msg = (
        f"🔒 আপনি সীমায় পৌঁছেছেন!\n"
        f"চ্যালেঞ্জে যোগ দিতে হবে।\n\n"
        f"📌 {channel}\n"
        f"সদস্য হলে সীমা বাড়বে।"
    )
    bot.send_message(chat_id, msg)


# ──────────────────────────────────────────────────────
# 8️⃣  Start handler
# ──────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def send_welcome(message: telebot.types.Message) -> None:
    chat_id = message.chat.id
    check_and_reset_daily(chat_id)
    user = get_user(chat_id)

    if chat_id == ADMIN_ID:
        welcome_msg = (
            "👋 অডমিন স্যার/ম্যাডাম!\n"
            "নিচের বাটনগুলো দিয়ে নিয়ন্ত্রণ করুন।"
        )
    else:
        welcome_msg = (
            "👋 হ্যালো! স্বাগতম।\n\n"
            f"{get_limit_status(chat_id)}\n\n"
            "দয়া করে আপনার অপশন নির্বাচন করুন:"
        )

    bot.send_message(
        chat_id, welcome_msg, reply_markup=get_main_markup(chat_id)
    )


# ──────────────────────────────────────────────────────
# 9️⃣  Callback handler
# ──────────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: telebot.types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    user = get_user(chat_id)

    # ---------- Video menu ----------
    if call.data == "menu_video":
        if user["is_premium"] or user["count_video_today"] < DEFAULT_VIDEO_LIMIT:
            bot.send_message(
                chat_id,
                "✅ ভিডিও মেনু\nদয়া করে ইউটিউব লিংক দিন:",
            )
            bot.register_next_step_handler(
                call.message, handle_video_input
            )
        else:
            show_challenge(chat_id, type="video")

    # ---------- Location menu ----------
    elif call.data == "menu_loc":
        if user["is_premium"] or user["count_loc_today"] < DEFAULT_LOC_LIMIT:
            bot.send_message(
                chat_id,
                "✅ লোকেশন মেনু\nদয়া করে লিংক/লোকেশন দিন:",
            )
            bot.register_next_step_handler(
                call.message, handle_loc_input
            )
        else:
            show_challenge(chat_id)

    # ---------- TikTok menu ----------
    elif call.data == "menu_tiktok":
        if user["is_premium"] or user["count_video_today"] < DEFAULT_VIDEO_LIMIT:
            bot.send_message(
                chat_id,
                "✅ TikTok মেনু\nদয়া করে TikTok লিংক দিন:",
            )
            bot.register_next_step_handler(
                call.message, handle_tiktok_input
            )
        else:
            show_challenge(chat_id, type="video")

    # ---------- Premium purchase ----------
    elif call.data == "pvm_buy":
        if user["is_premium"]:
            bot.send_message(chat_id, "✅ আপনি ইতিমধ্যে প্রিমিয়াম সদস্য!")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    f"💰 {PVM_PRICE} দে দিয়ে কিনুন",
                    callback_data="pay_pvm",
                )
            )
            markup.add(
                types.InlineKeyboardButton(
                    "👨‍💼 অডমিনকে মেসেজ", callback_data="admin_chat"
                )
            )
            bot.send_message(
                chat_id,
                f"🚀 প্রিমিয়াম প্যাকেজ\nসীমাহীন ভিডিও + লোকেশন!\n💰 {PVM_PRICE}\n\nনিচের বাটন টিপুন:",
                reply_markup=markup,
            )

    # ---------- Pay for premium ----------
    elif call.data == "pay_pvm":
        user["is_premium"] = True
        save_db(user_data)
        bot.send_message(
            chat_id,
            "🎉 অভিনন্দন! আপনি এখন প্রিমিয়াম সদস্য। সীমানাহীন সুবিধা উপভোগ করুন।",
        )

    # ---------- Referral menu ----------
    elif call.data == "ref_menu":
        ref_code = user["ref_code"]
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "📋 লিংক কপি",
                url=f"{REF_LINK_BASE}{ref_code}",
            )
        )
        bot.send_message(
            chat_id,
            f"🎁 আপনার রেফারেল কোড: {ref_code}\n\nনিচের বাটন টিপে শেয়ার করুন। রেফারেল পেলে সীমা বাড়বে।",
            reply_markup=markup,
        )

    # ---------- Admin chat ----------
    elif call.data == "admin_chat":
        bot.send_message(
            chat_id,
            f"👨‍💼 অডমিনকে মেসেজ দিন\nলিংক: https://t.me/{ADMIN_ID}",
        )

    # ---------- Admin panel ----------
    elif call.data == "admin_panel":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(
                "👥 সব ব্যবহারকারী", callback_data="adm_all_users"
            ),
            types.InlineKeyboardButton(
                "📊 স্ট্যাটাস", callback_data="adm_stats"
            ),
        )
        bot.send_message(
            chat_id,
            "👑 অডমিন কন্ট্রোল প্যানেল\nনিচের বাটন থেকে অপশন বেছে নিন।",
            reply_markup=markup,
        )

    # ---------- All users ----------
    elif call.data == "adm_all_users":
        total_users = len(user_data)
        premium_users = sum(1 for u in user_data.values() if u["is_premium"])
        bot.send_message(
            chat_id,
            f"📊 মোট ব্যবহারকারী: {total_users}\n💎 প্রিমিয়াম সদস্য: {premium_users}",
        )

    # ---------- Stats ----------
    elif call.data == "adm_stats":
        bot.send_message(
            chat_id,
            "📈 সিস্টেম স্ট্যাটাস:\nসমস্ত ফিচার ঠিকঠাক কাজ করছে।",
        )

    else:
        bot.answer_callback_query(call.id, "❓ অজানা অপশন")


# ──────────────────────────────────────────────────────
# 10️⃣  Video download handler
# ──────────────────────────────────────────────────────
def handle_video_input(message: telebot.types.Message) -> None:
    chat_id = message.chat.id
    user = get_user(chat_id)
    link = message.text.strip()

    bot.send_message(chat_id, f"🔄 {link}\nডাউনলোড চলছে…")

    try:
        import yt_dlp

        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": f"dl_{chat_id}.mp4",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)

        bot.send_message(chat_id, "✅ ডাউনলোড সফল!")
        with open(filename, "rb") as f:
            bot.send_video(chat_id, f)

        os.remove(filename)

        if not user["is_premium"]:
            user["count_video_today"] += 1
            save_db(user_data)
            bot.send_message(
                chat_id,
                f"✅ বাকি ভিডিও লিমিট: {DEFAULT_VIDEO_LIMIT - user['count_video_today']}",
            )

    except Exception as e:
        bot.send_message(chat_id, f"❌ ডাউনলোডে সমস্যা: {e}")


# ──────────────────────────────────────────────────────
# 11️⃣  Location request handler
# ──────────────────────────────────────────────────────
def handle_loc_input(message: telebot.types.Message) -> None:
    chat_id = message.chat.id
    user = get_user(chat_id)
    loc_text = message.text.strip()

    bot.send_message(
        chat_id,
        f"✅ লোকেশন অনুরোধ পাঠানো হল!\nআপনার অনুরোধ: {loc_text}\n\nঅ্যাডমিন শীঘ্রই যোগাযোগ করবেন।",
    )

    if not user["is_premium"]:
        user["count_loc_today"] += 1
        save_db(user_data)
        bot.send_message(
            chat_id,
            f"✅ বাকি লোকেশন লিমিট: {DEFAULT_LOC_LIMIT - user['count_loc_today']}",
        )


# ──────────────────────────────────────────────────────
# 12️⃣  TikTok download handler
# ──────────────────────────────────────────────────────
def handle_tiktok_input(message: telebot.types.Message) -> None:
    chat_id = message.chat.id
    user = get_user(chat_id)
    link = message.text.strip()

    if not link.startswith(
        ("https://www.tiktok.com", "https://m.tiktok.com", "https://vm.tiktok.com")
    ):
        bot.send_message(chat_id, "❌ বৈধ TikTok লিংক দিন।")
        return

    bot.send_message(chat_id, f"🔄 TikTok লিংক: {link}\nডাউনলোড চলছে…")

    try:
        import yt_dlp

        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": f"dl_{chat_id}.mp4",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)

        bot.send_message(chat_id, "✅ ডাউনলোড সফল!")
        with open(filename, "rb") as f:
            bot.send_video(chat_id, f)

        os.remove(filename)

        if not user["is_premium"]:
            user["count_video_today"] += 1
            save_db(user_data)
            bot.send_message(
                chat_id,
                f"✅ বাকি ভিডিও লিমিট: {DEFAULT_VIDEO_LIMIT - user['count_video_today']}",
            )

    except Exception as e:
        bot.send_message(chat_id, f"❌ ডাউনলোডে সমস্যা: {e}")


# ──────────────────────────────────────────────────────
# 13️⃣  Main loop
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 বট চালু হচ্ছে…")
    bot.polling(none_stop=True)
