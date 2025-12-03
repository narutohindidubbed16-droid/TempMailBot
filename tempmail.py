# ============================================
#  GOD-LEVEL TEMPMAIL V3  (ULTRA-FAST MODE)
#  Ultra-Short Callback Codes (2B)
#  MongoDB Storage + Multi-Mailbox + Admin Panel
#  By Ars 🔥
# ============================================

import re, time, random, string, hashlib, requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, MONGO_URI


# --------------------------------------------
# MONGO DATABASE
# --------------------------------------------
client_db = MongoClient(MONGO_URI)
db = client_db["default"]
users_col = db["users"]     # user mailboxes
mails_col = db["mails"]     # message map


# --------------------------------------------
# BOT SETUP
# --------------------------------------------
app = Client(
    "tempmail_v3_ars",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)

BASE_URL = "https://api.mail.tm"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

CHANNEL_1 = "https://t.me/AbdulBotzOfficial"
CHANNEL_2 = "https://t.me/+9_0NFI-v_U1hNGVl"

MAX_LEN = 3500


# --------------------------------------------
# UTIL FUNCS
# --------------------------------------------
def r_user(n=8):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))

def r_pass(n=12):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def short(n=3):
    return ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(n))

def get_domain():
    try:
        r = requests.get(f"{BASE_URL}/domains", headers=HEADERS).json()
        if isinstance(r, list):
            return r[0]["domain"]
        return r.get("hydra:member", [{}])[0].get("domain")
    except:
        return None

def create_mail(email, pwd):
    r = requests.post(f"{BASE_URL}/accounts", headers=HEADERS, json={"address": email, "password": pwd})
    return r.status_code in [200, 201]

def get_token(email, pwd):
    r = requests.post(f"{BASE_URL}/token", headers=HEADERS, json={"address": email, "password": pwd})
    return r.json().get("token") if r.status_code == 200 else None

def inbox_list_api(token):
    r = requests.get(f"{BASE_URL}/messages", headers={"Authorization": f"Bearer {token}"})
    j = r.json()
    return j if isinstance(j, list) else j.get("hydra:member", [])

def list_msgs(token):
    """Get messages from inbox"""
    return inbox_list_api(token)

def parse_html(html):
    """Clean HTML content"""
    soup = BeautifulSoup("".join(html), "html.parser")
    for a in soup.find_all("a", href=True):
        a.string = f"{a.text} [{a['href']}]"
    return re.sub(r"\s+", " ", soup.get_text()).strip()

def clean(html):
    """Alias for parse_html"""
    return parse_html(html)


# ============================================
# START COMMAND
# ============================================
@app.on_message(filters.command("start"))
async def start_cmd(_, m):

    ui = (
        "👋 **Welcome to God-Level TempMail Bot V3!**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📧 Unlimited Emails\n"
        "⚡ Ultra-Fast Inbox\n"
        "🛡 MongoDB Storage\n"
        "🎯 Multi-Mail Support\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Main Channel", url=CHANNEL_1)],
        [InlineKeyboardButton("🌐 Optional Channel", url=CHANNEL_2)],
        [InlineKeyboardButton("🚀 Continue", callback_data="M0")]
    ])

    await m.reply(ui, reply_markup=btn)


# ============================================
# MAIN MENU
# ============================================
@app.on_callback_query(filters.regex("^M0$"))
async def main_menu(_, q):

    ui = (
        "**🔥 TempMail Menu**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📧 Create Emails\n"
        "📨 Read Inbox\n"
        "🗄 Delete Mailboxes\n"
        "⚙ Admin Tools\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    btns = [
        [InlineKeyboardButton("📧 Generate Mail", callback_data="G1")],
        [InlineKeyboardButton("📨 My Inboxes", callback_data="I1")],
        [InlineKeyboardButton("🗑 Clear Mailbox", callback_data="D1")]
    ]
    
    if q.from_user.id == OWNER_ID:
        btns.append([InlineKeyboardButton("⚙ Admin Panel", callback_data="A1")])
    else:
        btns.append([InlineKeyboardButton("ℹ About", callback_data="ABT")])

    btn = InlineKeyboardMarkup(btns)

    await q.message.reply(ui, reply_markup=btn)


# ============================================
# ABOUT
# ============================================
@app.on_callback_query(filters.regex("^ABT$"))
async def about(_, q):
    txt = (
        "**ℹ About This Bot**\n"
        "━━━━━━━━━━━━━━\n"
        "🔥 God-Level TempMail V3\n"
        "⚡ Ultra-Fast Temporary Email\n"
        "🛡 Secure MongoDB Storage\n"
        "🎯 Multi-Mailbox Support\n\n"
        "Developed by Ars 🔥"
    )
    await q.message.reply(txt)


# ============================================
# GENERATE MAIL
# ============================================
@app.on_callback_query(filters.regex("^G1$"))
async def gen_mail(_, q):

    loading = await q.message.reply("⏳ Creating Mailbox...")

    domain = get_domain()
    if not domain:
        return await loading.edit("❌ Domain error, try again.")

    username = r_user()
    password = r_pass()
    email = f"{username}@{domain}"

    if not create_mail(email, password):
        return await loading.edit("❌ Mail creation failed.")

    token = get_token(email, password)
    if not token:
        return await loading.edit("❌ Token fetch failed.")

    # Save to DB
    users_col.update_one(
        {"user_id": q.from_user.id},
        {"$push": {"emails": email, "tokens": token}},
        upsert=True
    )

    s = short()  # 3-digit ID for callback
    mails_col.insert_one({"sid": s, "token": token})

    txt = (
        "**📧 Mailbox Created!**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📧 **Email:** `{email}`\n"
        f"🔑 **Pass:** `{password}`\n"
        f"🔒 **Token:** `{token}`\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Open Inbox", callback_data=f"IN{s}")]
    ])

    await loading.delete()
    await q.message.reply(txt, reply_markup=btn)


# ============================================
# MAILBOX LIST
# ============================================
@app.on_callback_query(filters.regex("^I1$"))
async def inboxes(_, q):

    u = users_col.find_one({"user_id": q.from_user.id})

    if not u or "emails" not in u or len(u["emails"]) == 0:
        return await q.message.reply("❌ No mailboxes yet!")

    btns = []

    for email, token in zip(u["emails"], u["tokens"]):
        s = short()
        mails_col.insert_one({"sid": s, "token": token})
        btns.append([InlineKeyboardButton(email, callback_data=f"IN{s}")])

    await q.message.reply("📬 **Your Mailboxes**", reply_markup=InlineKeyboardMarkup(btns))


# ============================================
# OPEN INBOX (LIST MESSAGES)
# ============================================
@app.on_callback_query(filters.regex("^IN"))
async def open_inbox(_, q):

    sid = q.data.replace("IN", "")
    rec = mails_col.find_one({"sid": sid})

    if not rec:
        return await q.message.reply("❌ Session expired, try again.")

    token = rec["token"]
    inbox = list_msgs(token)

    if not inbox:
        return await q.message.reply("📭 Inbox is empty!")

    txt = "📬 **Inbox**\n━━━━━━━━━━━━━━\n"
    btns = []

    for i, mail in enumerate(inbox[:10], 1):
        from_addr = mail["from"]["address"]
        subject = mail["subject"]

        # Generate tiny SID for message
        mid = short(3)
        mails_col.update_one(
            {"sid": sid},
            {"$set": {f"msg_{mid}": mail["id"]}},
            upsert=True
        )

        txt += f"**{i}.** `{from_addr}` — *{subject}*\n"
        btns.append([InlineKeyboardButton(str(i), callback_data=f"RD{mid}:{sid}")])

    await q.message.reply(txt, reply_markup=InlineKeyboardMarkup(btns))


# ============================================
# READ SPECIFIC MESSAGE
# ============================================
@app.on_callback_query(filters.regex("^RD"))
async def read_mail(_, q):

    data = q.data.replace("RD", "")  # e.g. "abc:xyz"
    mid, sid = data.split(":")

    rec = mails_col.find_one({"sid": sid})
    if not rec or f"msg_{mid}" not in rec:
        return await q.message.reply("❌ Message expired.")

    msg_id = rec[f"msg_{mid}"]
    token = rec["token"]

    r = requests.get(f"{BASE_URL}/messages/{msg_id}",
                     headers={"Authorization": f"Bearer {token}"})

    if r.status_code != 200:
        return await q.message.reply("❌ Can't load message.")

    d = r.json()

    if "html" in d:
        content = parse_html(d["html"])
    else:
        content = d.get("text", "No text content.")

    if len(content) > MAX_LEN:
        content = content[:MAX_LEN] + "\n…[truncated]"

    txt = (
        f"**From:** `{d['from']['address']}`\n"
        f"**Subject:** `{d['subject']}`\n"
        "━━━━━━━━━━━━━━\n"
        f"{content}"
    )

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Close", callback_data="CL0")]
    ])

    await q.message.reply(txt, disable_web_page_preview=True, reply_markup=btn)


# ============================================
# CLOSE MESSAGE
# ============================================
@app.on_callback_query(filters.regex("^CL0$"))
async def close_msg(_, q):
    try:
        await q.message.delete()
    except:
        pass


# ============================================
# DELETE ALL MAILBOXES
# ============================================
@app.on_callback_query(filters.regex("^D1$"))
async def delete_mailboxes(_, q):

    users_col.update_one(
        {"user_id": q.from_user.id},
        {"$set": {"emails": [], "tokens": []}},
        upsert=True
    )

    await q.message.reply("🗑 **All mailboxes cleared!**")


# ============================================
# ADMIN PANEL
# ============================================
@app.on_callback_query(filters.regex("^A1$"))
async def admin_panel(_, q):

    if q.from_user.id != OWNER_ID:
        return await q.answer("❌ Not Allowed!", show_alert=True)

    txt = (
        "**⚙ ADMIN PANEL**\n"
        "━━━━━━━━━━━━━━\n"
        "Choose an option:"
    )

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast", callback_data="B0")],
        [InlineKeyboardButton("👥 Users Count", callback_data="U0")],
        [InlineKeyboardButton("📄 Logs", callback_data="L0")]
    ])

    await q.message.reply(txt, reply_markup=btn)


# ============================================
# USER COUNT
# ============================================
@app.on_callback_query(filters.regex("^U0$"))
async def user_count(_, q):

    count = users_col.count_documents({})
    await q.message.reply(f"👥 **Total Users:** {count}")


# ============================================
# LOGS
# ============================================
@app.on_callback_query(filters.regex("^L0$"))
async def logs(_, q):
    if q.from_user.id != OWNER_ID:
        return await q.answer("Not allowed", show_alert=True)
    
    await q.message.reply("📄 **Logs feature coming soon!**")


# ============================================
# BROADCAST — Step 1
# ============================================
@app.on_callback_query(filters.regex("^B0$"))
async def broadcast_start(_, q):

    if q.from_user.id != OWNER_ID:
        return await q.answer("Not allowed", show_alert=True)

    await q.message.reply("📢 **Send the broadcast message now. (Reply with /cancel to stop)**")


# ============================================
# BROADCAST — Step 2 (Handle Message)
# ============================================
@app.on_message(filters.text & filters.user(OWNER_ID) & filters.private)
async def broadcast_handler(_, m):
    
    if m.text.startswith('/'):
        return  # Ignore commands
    
    # Check if user recently triggered broadcast
    users = users_col.find({})
    sent = 0
    failed = 0

    status_msg = await m.reply("📢 Broadcasting...")

    for u in users:
        try:
            await app.send_message(u["user_id"], m.text)
            sent += 1
        except:
            failed += 1

    await status_msg.edit(f"✅ Broadcast Complete!\n\n📤 Sent: {sent}\n❌ Failed: {failed}")


# ============================================
# RUN BOT
# ============================================
print("🔥 Bot Starting...")
app.run()