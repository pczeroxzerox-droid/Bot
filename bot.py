import os, json, datetime, telebot, secrets
from telebot import types
import yt_dlp

API_TOKEN = os.getenv('8224596860:AAGnZj9hYF9uvuJE7JKnWhduALOaqRP4C8I')
ADMIN_ID = int(os.getenv('ADMIN_ID', 8210146346))
ADMIN_USERNAME = "@jiolinhacker"  # এখানে username দাও

CHANNEL_NAME_1 = '@primiumboss29'
CHANNEL_NAME_2 = '@saniesit9'

REF_LINK_BASE = 'https://t.me/YourBot?start='

DEFAULT_VIDEO_LIMIT = 3
DEFAULT_LOC_LIMIT   = 5
PREMIUM_VIDEO_LIMIT = 100
PREMIUM_LOC_LIMIT   = 100

PVM_PRICE = "৫০০ টাকা"
DB_FILE = 'bot_data.json'

# ---------- DB ----------
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

user_data = load_db()

bot = telebot.TeleBot(API_TOKEN)
print("🚀 Bot চালু হয়েছে...")

# ---------- USER ----------
def get_user(chat_id):
    chat_id = str(chat_id)
    if chat_id not in user_data:
        user_data[chat_id] = {
            'ref_code': f"REF{secrets.token_hex(4).upper()}",
            'ref_by': None,
            'is_premium': False,
            'last_date_video': datetime.date.today().strftime('%Y-%m-%d'),
            'count_video_today': 0,
            'last_date_loc': datetime.date.today().strftime('%Y-%m-%d'),
            'count_loc_today': 0,
            'total_refs': 0
        }
        save_db(user_data)
    return user_data[chat_id]

# ---------- RESET ----------
def check_and_reset_daily(chat_id):
    user = get_user(chat_id)
    today = datetime.date.today().strftime('%Y-%m-%d')

    if user['last_date_video'] != today:
        user['count_video_today'] = 0
        user['last_date_video'] = today

    if user['last_date_loc'] != today:
        user['count_loc_today'] = 0
        user['last_date_loc'] = today

    save_db(user_data)

# ---------- LIMIT ----------
def get_limit_status(chat_id):
    user = get_user(chat_id)

    video_limit = PREMIUM_VIDEO_LIMIT if user['is_premium'] else DEFAULT_VIDEO_LIMIT
    loc_limit   = PREMIUM_LOC_LIMIT if user['is_premium'] else DEFAULT_LOC_LIMIT

    video_left = max(0, video_limit - user['count_video_today'])
    loc_left   = max(0, loc_limit - user['count_loc_today'])

    return f"""📊 লিমিট স্ট্যাটাস

🎬 ভিডিও বাকি: {video_left}
📍 লোকেশন বাকি: {loc_left}
{'💎 প্রিমিয়াম' if user['is_premium'] else '🔹 ফ্রি ইউজার'}"""

# ---------- MENU ----------
def get_main_markup(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(
        types.InlineKeyboardButton("🎬 ভিডিও ডাউনলোড", callback_data="menu_video"),
        types.InlineKeyboardButton("📍 লোকেশন সার্ভিস", callback_data="menu_loc")
    )

    if int(chat_id) == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("👑 অ্যাডমিন প্যানেল", callback_data="admin_panel"))
    else:
        markup.add(
            types.InlineKeyboardButton("💎 প্রিমিয়াম নিন", callback_data="pvm_buy"),
            types.InlineKeyboardButton("👥 রেফার করুন", callback_data="ref_menu")
        )
        markup.add(types.InlineKeyboardButton("👨‍💼 অ্যাডমিন", callback_data="admin_chat"))

    return markup

# ---------- CHANNEL CHECK ----------
def check_join(chat_id):
    try:
        u1 = bot.get_chat_member(CHANNEL_NAME_1, chat_id)
        u2 = bot.get_chat_member(CHANNEL_NAME_2, chat_id)

        if u1.status in ['left', 'kicked'] or u2.status in ['left', 'kicked']:
            bot.send_message(chat_id, f"⚠️ আগে এই দুইটি চ্যানেল জয়েন করুন:\n{CHANNEL_NAME_1}\n{CHANNEL_NAME_2}")
            return False
        return True
    except:
        return True

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    check_and_reset_daily(chat_id)

    bot.send_message(
        chat_id,
        f"👋 স্বাগতম!\n\n{get_limit_status(chat_id)}",
        reply_markup=get_main_markup(chat_id)
    )

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    user = get_user(chat_id)

    if call.data == "menu_video":
        if not check_join(chat_id): return

        if user['count_video_today'] >= DEFAULT_VIDEO_LIMIT and not user['is_premium']:
            bot.send_message(chat_id, "⚠️ আজকের ভিডিও লিমিট শেষ!")
            return

        bot.send_message(chat_id, "🎬 ভিডিও লিংক দিন:")
        bot.register_next_step_handler(call.message, handle_video_input)

    elif call.data == "menu_loc":
        if not check_join(chat_id): return

        if user['count_loc_today'] >= DEFAULT_LOC_LIMIT and not user['is_premium']:
            bot.send_message(chat_id, "⚠️ আজকের লোকেশন লিমিট শেষ!")
            return

        bot.send_message(chat_id, "📍 লোকেশন লিখুন:")
        bot.register_next_step_handler(call.message, handle_loc_input)

    elif call.data == "pvm_buy":
        bot.send_message(chat_id, f"💎 প্রিমিয়াম প্যাকেজ\n💰 {PVM_PRICE}")

    elif call.data == "ref_menu":
        ref = user['ref_code']
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📋 লিংক কপি", url=f"{REF_LINK_BASE}{ref}"))
        bot.send_message(chat_id, f"🎁 আপনার কোড: {ref}", reply_markup=markup)

    elif call.data == "admin_chat":
        bot.send_message(chat_id, f"https://t.me/{ADMIN_USERNAME}")

    elif call.data == "admin_panel":
        bot.send_message(chat_id, f"👥 মোট ইউজার: {len(user_data)}")

# ---------- VIDEO ----------
def handle_video_input(message):
    chat_id = message.chat.id
    user = get_user(chat_id)
    link = message.text.strip()

    bot.send_message(chat_id, "⏳ ডাউনলোড হচ্ছে...")

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': f'dl_{chat_id}.mp4',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as f:
            bot.send_video(chat_id, f)

        os.remove(filename)

        if not user['is_premium']:
            user['count_video_today'] += 1
            save_db(user_data)

        bot.send_message(chat_id, "✅ ভিডিও সম্পন্ন!")

    except Exception:
        bot.send_message(chat_id, "❌ ডাউনলোড ব্যর্থ!")

# ---------- LOC ----------
def handle_loc_input(message):
    chat_id = message.chat.id
    user = get_user(chat_id)

    bot.send_message(chat_id, "📍 অনুরোধ গ্রহণ করা হয়েছে!")

    if not user['is_premium']:
        user['count_loc_today'] += 1
        save_db(user_data)

# ---------- RUN ----------
bot.infinity_polling()
