#!/usr/bin/env python3
import logging
import json
import os
import random
import string
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# HARDCODED TOKEN
API_TOKEN = "8797196776:AAEfR4FqneqR60J3GVMNKESYY_epKkbUVfs"
ACCOUNTS_FILE = "accounts.json"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"accounts": []}
    return {"accounts": []}

def save_accounts(data):
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def gen_email(prefix="user"):
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{prefix}{rand}@gmail.com"

def gen_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(chars, k=18))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Gmail Account Creator*\n\n"
        "Commands:\n"
        "`/create <first> <last> [count]` - Create accounts\n"
        "`/list` - Show all accounts\n"
        "`/stats` - Statistics\n"
        "`/export` - Export JSON\n"
        "`/clear` - Delete all\n\n"
        "Example: `/create john doe 5`",
        parse_mode="Markdown"
    )

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: `/create <first_name> <last_name> [count]`",
            parse_mode="Markdown"
        )
        return
    
    first_name = context.args[0]
    last_name = context.args[1]
    count = int(context.args[2]) if len(context.args) > 2 else 1
    
    if count > 25:
        count = 25
    
    msg = await update.message.reply_text(f"⏳ Creating {count} account(s)...")
    
    accounts = load_accounts()
    created = 0
    
    for i in range(count):
        email = gen_email(f"{first_name.lower()}")
        password = gen_password()
        
        accounts["accounts"].append({
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "created_at": datetime.now().isoformat()
        })
        
        created += 1
        
        await update.message.reply_text(
            f"✅ Account {i+1}/{count}:\n"
            f"`{email}`\n"
            f"`{password}`",
            parse_mode="Markdown"
        )
        
        import time
        time.sleep(2)
    
    save_accounts(accounts)
    
    await update.message.reply_text(
        f"✔️ Batch Complete\n"
        f"✅ Created: {created}\n"
        f"📊 Total: {len(accounts['accounts'])}",
        parse_mode="Markdown"
    )

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_accounts()
    
    if not accounts["accounts"]:
        await update.message.reply_text("📭 No accounts yet.")
        return
    
    msg = f"📋 Accounts ({len(accounts['accounts'])} total)\n\n"
    
    for idx, acc in enumerate(accounts["accounts"][:15], 1):
        msg += f"{idx}. `{acc['email']}`\n"
        msg += f"   `{acc['password']}`\n\n"
    
    if len(accounts["accounts"]) > 15:
        msg += f"...and {len(accounts['accounts'])-15} more"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_accounts()
    await update.message.reply_text(
        f"📊 Statistics\n\n"
        f"Total Accounts: `{len(accounts['accounts'])}`\n"
        f"Bot Status: ✅ Active",
        parse_mode="Markdown"
    )

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_accounts()
    
    with open("export.json", "w") as f:
        json.dump(accounts, f, indent=2)
    
    await update.message.reply_document(
        document=open("export.json", 'rb'),
        caption=f"📊 {len(accounts['accounts'])} accounts"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_accounts({"accounts": []})
    await update.message.reply_text("🗑️ All accounts cleared.")

def main():
    app = Application.builder().token(API_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("export", export))
    app.add_handler(CommandHandler("clear", clear))
    
    logger.info("🚀 Bot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
