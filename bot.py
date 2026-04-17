import os
import json
import datetime
import secrets
import telebot
from telebot import types
import yt_dlp

# ================= CONFIG =================
API_TOKEN = os.getenv("8615288381:AAGwDHusKLlS4zTrf6IOiFuLLf9DICYcOCM")
ADMIN_ID = int(os.getenv("ADMIN_ID", 8210146346))

CHANNEL_1 = "@samiedit9"
CHANNEL_2 = "@primiumboss29"

DB_FILE = "bot_data.json"

VIDEO_LIMIT = 3
LOC_LIMIT = 5

bot = telebot.TeleBot(API_TOKEN)

# ================= DATABASE =================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(user_data, f, indent=2)

user_data = load_db()

# ================= USER =================
def get_user(uid):
    uid = str(uid)

    if uid not in user_data:
        user_data[uid] = {
            "video": 0,
            "loc": 0,
            "date": str(datetime.date.today()),
            "premium": False,
            "ref": f"REF{secrets.token_hex(3)}",
            "referred_by": None,
            "ref_count": 0
        }
        save_db()

    return user_data[uid]

# ================= RESET =================
def reset(uid):
    u = get_user(uid)
    today = str(datetime.date.today())

    if u["date"] != today:
        u["video"] = 0
        u["loc"] = 0
        u["date"] = today
        save_db()

# ================= CHANNEL CHECK =================
def check_join(uid):
    try:
        m1 = bot.get_chat_member(CHANNEL_1, uid)
        m2 = bot.get_chat_member(CHANNEL_2, uid)

        if m1.status in ["left", "kicked"] or m2.status in ["left", "kicked"]:
            bot.send_message(uid, f"⚠️ আগে দুইটা চ্যানেল join করুন:\n{CHANNEL_1}\n{CHANNEL_2}")
            return False
        return True
    except:
        return True

# ================= MENU =================
def menu(uid):
    m = types.InlineKeyboardMarkup(row_width=2)

    m.add(
        types.InlineKeyboardButton("🎬 Video", callback_data="video"),
        types.InlineKeyboardButton("📍 Location", callback_data="loc")
    )

    if int(uid) == ADMIN_ID:
        m.add(types.InlineKeyboardButton("👑 Admin Panel", callback_data="admin"))

    return m

# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.chat.id
    reset(uid)

    u = get_user(uid)

    bot.send_message(
        uid,
        f"""👋 Welcome

🎬 Video Left: {VIDEO_LIMIT - u['video']}
📍 Loc Left: {LOC_LIMIT - u['loc']}
💎 Premium: {'YES' if u['premium'] else 'NO'}""",
        reply_markup=menu(uid)
    )

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.message.chat.id
    u = get_user(uid)

    bot.answer_callback_query(c.id)

    # -------- VIDEO --------
    if c.data == "video":

        if not check_join(uid):
            return

        if u["video"] >= VIDEO_LIMIT and not u["premium"]:
            bot.send_message(uid, "❌ Video limit শেষ!")
            return

        bot.send_message(uid, "🎬 YouTube link পাঠাও:")
        bot.register_next_step_handler(c.message, download_video)

    # -------- LOCATION --------
    elif c.data == "loc":

        if not check_join(uid):
            return

        if u["loc"] >= LOC_LIMIT and not u["premium"]:
            bot.send_message(uid, "❌ Location limit শেষ!")
            return

        bot.send_message(uid, "📍 Location লিখো:")
        bot.register_next_step_handler(c.message, location_request)

    # -------- ADMIN --------
    elif c.data == "admin":
        if uid != ADMIN_ID:
            return

        total = len(user_data)
        premium = sum(1 for x in user_data.values() if x["premium"])

        bot.send_message(uid, f"""👑 ADMIN PANEL

👥 Users: {total}
💎 Premium: {premium}""")

    # -------- PREMIUM GIVE --------
    elif c.data.startswith("make_premium_"):
        if uid != ADMIN_ID:
            return

        target = c.data.split("_")[2]
        if target in user_data:
            user_data[target]["premium"] = True
            save_db()
            bot.send_message(uid, "✅ Premium given!")
        else:
            bot.send_message(uid, "❌ User not found")

# ================= VIDEO =================
def download_video(msg):
    uid = msg.chat.id
    u = get_user(uid)
    link = msg.text.strip()

    bot.send_message(uid, "⏳ Download হচ্ছে...")

    try:
        file = f"{uid}.mp4"

        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": file,
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        with open(file, "rb") as f:
            bot.send_video(uid, f)

        os.remove(file)

        if not u["premium"]:
            u["video"] += 1
            save_db()

        bot.send_message(uid, "✅ Done!")

    except Exception as e:
        bot.send_message(uid, f"❌ Error: {e}")

# ================= LOCATION =================
def location_request(msg):
    uid = msg.chat.id
    u = get_user(uid)

    bot.send_message(uid, f"📍 Request received: {msg.text}")

    if not u["premium"]:
        u["loc"] += 1
        save_db()

# ================= ADMIN GIVE PREMIUM =================
@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID)
def admin_text(msg):
    try:
        uid = msg.text.strip()
        user_data[uid]["premium"] = True
        save_db()
        bot.send_message(msg.chat.id, f"✅ Premium given to {uid}")
    except:
        pass

# ================= RUN =================
print("🚀 PRO BOT RUNNING...")
bot.infinity_polling()
