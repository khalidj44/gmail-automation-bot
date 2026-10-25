#!/usr/bin/env python3
"""
Production Gmail Account Creator Bot
Interactive conversation flow with real account creation
Designed for Render 24/7 deployment
"""

import os
import logging
import re
from datetime import datetime
from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import json
import asyncio
from gmail_creator import GmailCreator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Telegram Bot Token from environment
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8797196776:AAEfR4FqneqR60J3GVMNKESYY_epKkbUVfs")

# Conversation states
class ConversationStates(Enum):
    FIRST_NAME = 1
    LAST_NAME = 2
    DATE_OF_BIRTH = 3
    USERNAME = 4
    PASSWORD = 5
    CONFIRM_PASSWORD = 6
    CREATING = 7

# Store user sessions
USER_SESSIONS = {}
ACCOUNTS_FILE = "accounts.json"

def load_accounts():
    """Load saved accounts from JSON"""
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"accounts": []}
    return {"accounts": []}

def save_accounts(data):
    """Save accounts to JSON"""
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def save_account(email, password, first_name, last_name, dob):
    """Save a newly created account"""
    accounts = load_accounts()
    accounts["accounts"].append({
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "dob": dob,
        "created_at": datetime.now().isoformat()
    })
    save_accounts(accounts)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start command - initiate conversation"""
    user_id = update.effective_user.id
    
    # Initialize user session
    USER_SESSIONS[user_id] = {
        "first_name": None,
        "last_name": None,
        "dob": None,
        "username": None,
        "password": None,
    }
    
    welcome_msg = (
        "🤖 *Welcome to Gmail Account Creator*\n\n"
        "I'll help you create a real Gmail account step by step.\n\n"
        "Let's start! What is your *First Name*?\n\n"
        "_Example: John, Ahmed, Maria_"
    )
    
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")
    return ConversationStates.FIRST_NAME.value

async def first_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle first name input"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Validate: only letters
    if not re.match(r'^[a-zA-Z]+$', text):
        await update.message.reply_text(
            "❌ First name should contain only letters. Try again:",
            parse_mode="Markdown"
        )
        return ConversationStates.FIRST_NAME.value
    
    if len(text) < 2 or len(text) > 30:
        await update.message.reply_text(
            "❌ First name should be between 2-30 characters.",
            parse_mode="Markdown"
        )
        return ConversationStates.FIRST_NAME.value
    
    USER_SESSIONS[user_id]["first_name"] = text
    
    await update.message.reply_text(
        f"✅ Great! Your first name is *{text}*\n\n"
        "Now, what is your *Last Name*?\n\n"
        "_Example: Smith, Khan, Garcia_",
        parse_mode="Markdown"
    )
    
    return ConversationStates.LAST_NAME.value

async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle last name input"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Validate: only letters
    if not re.match(r'^[a-zA-Z]+$', text):
        await update.message.reply_text(
            "❌ Last name should contain only letters. Try again:",
            parse_mode="Markdown"
        )
        return ConversationStates.LAST_NAME.value
    
    if len(text) < 2 or len(text) > 30:
        await update.message.reply_text(
            "❌ Last name should be between 2-30 characters.",
            parse_mode="Markdown"
        )
        return ConversationStates.LAST_NAME.value
    
    USER_SESSIONS[user_id]["last_name"] = text
    
    await update.message.reply_text(
        f"✅ Great! Your last name is *{text}*\n\n"
        "Now, enter your *Date of Birth*:\n\n"
        "_Format: DD/MM/YYYY (example: 25/12/1995)_",
        parse_mode="Markdown"
    )
    
    return ConversationStates.DATE_OF_BIRTH.value

async def date_of_birth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle date of birth input"""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Validate DOB format
    try:
        dob_obj = datetime.strptime(text, "%d/%m/%Y")
        
        # Check if age is between 18-100
        today = datetime.today()
        age = today.year - dob_obj.year - ((today.month, today.day) < (dob_obj.month, dob_obj.day))
        
        if age < 18 or age > 100:
            await update.message.reply_text(
                "❌ You must be between 18-100 years old. Try again:",
                parse_mode="Markdown"
            )
            return ConversationStates.DATE_OF_BIRTH.value
        
        USER_SESSIONS[user_id]["dob"] = text
        
        await update.message.reply_text(
            f"✅ Date of birth: *{text}* (Age: {age})\n\n"
            "Now, choose your *Gmail username*:\n\n"
            "_Don't include @gmail.com - just the username_\n"
            "_Example: john1995smith, arif54rana45_\n\n"
            "_Must be 6-30 characters, letters, numbers, dots, underscores, hyphens_",
            parse_mode="Markdown"
        )
        
        return ConversationStates.USERNAME.value
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid date format. Use DD/MM/YYYY (e.g., 25/12/1995)",
            parse_mode="Markdown"
        )
        return ConversationStates.DATE_OF_BIRTH.value

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle username input and check availability"""
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()
    
    # Validate username format
    if not re.match(r'^[a-z0-9._-]{6,30}$', text):
        await update.message.reply_text(
            "❌ Invalid username format.\n\n"
            "_Must be 6-30 characters: letters, numbers, dots (.), underscores (_), hyphens (-) only_\n"
            "_Example: john.smith_1995_",
            parse_mode="Markdown"
        )
        return ConversationStates.USERNAME.value
    
    # Check username availability with Google
    await update.message.reply_text(
        f"🔍 Checking if *{text}@gmail.com* is available...",
        parse_mode="Markdown"
    )
    
    gmail_creator = GmailCreator()
    is_available = await gmail_creator.check_username_availability(text)
    
    if is_available:
        USER_SESSIONS[user_id]["username"] = text
        
        await update.message.reply_text(
            f"✅ Excellent! *{text}@gmail.com* is available!\n\n"
            "Now, create a *strong password* for your Gmail account:\n\n"
            "_Minimum 8 characters_\n"
            "_Include: uppercase, lowercase, numbers, symbols_\n"
            "_Example: MyPass123!@_",
            parse_mode="Markdown"
        )
        
        return ConversationStates.PASSWORD.value
    else:
        # Suggest alternatives
        alternatives = await gmail_creator.suggest_available_usernames(text)
        
        alt_list = "\n".join([f"• `{alt}@gmail.com`" for alt in alternatives[:5]])
        
        await update.message.reply_text(
            f"❌ *{text}@gmail.com* is already taken.\n\n"
            "Here are some available alternatives:\n\n"
            f"{alt_list}\n\n"
            "_Or enter a different username of your choice:_",
            parse_mode="Markdown"
        )
        
        return ConversationStates.USERNAME.value

async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle password input"""
    user_id = update.effective_user.id
    password = update.message.text.strip()
    
    # Validate password strength
    if len(password) < 8:
        await update.message.reply_text(
            "❌ Password must be at least 8 characters long.",
            parse_mode="Markdown"
        )
        return ConversationStates.PASSWORD.value
    
    if not re.search(r'[a-z]', password):
        await update.message.reply_text(
            "❌ Password must contain lowercase letters.",
            parse_mode="Markdown"
        )
        return ConversationStates.PASSWORD.value
    
    if not re.search(r'[A-Z]', password):
        await update.message.reply_text(
            "❌ Password must contain uppercase letters.",
            parse_mode="Markdown"
        )
        return ConversationStates.PASSWORD.value
    
    if not re.search(r'[0-9]', password):
        await update.message.reply_text(
            "❌ Password must contain numbers.",
            parse_mode="Markdown"
        )
        return ConversationStates.PASSWORD.value
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        await update.message.reply_text(
            "❌ Password must contain special characters (!@#$%^&* etc).",
            parse_mode="Markdown"
        )
        return ConversationStates.PASSWORD.value
    
    USER_SESSIONS[user_id]["password"] = password
    
    await update.message.reply_text(
        "✅ Strong password set!\n\n"
        "Confirm your password by typing it again:",
        parse_mode="Markdown"
    )
    
    return ConversationStates.CONFIRM_PASSWORD.value

async def confirm_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm password matches"""
    user_id = update.effective_user.id
    confirm_pwd = update.message.text.strip()
    original_pwd = USER_SESSIONS[user_id]["password"]
    
    if confirm_pwd != original_pwd:
        await update.message.reply_text(
            "❌ Passwords don't match. Try again:",
            parse_mode="Markdown"
        )
        return ConversationStates.CONFIRM_PASSWORD.value
    
    # All info collected - show summary and create account
    session = USER_SESSIONS[user_id]
    
    summary = (
        f"📋 *Account Summary*\n\n"
        f"First Name: *{session['first_name']}*\n"
        f"Last Name: *{session['last_name']}*\n"
        f"Date of Birth: *{session['dob']}*\n"
        f"Gmail: *{session['username']}@gmail.com*\n"
        f"Password: *{len(session['password'])} characters*\n\n"
        f"Creating your account now... ⏳"
    )
    
    await update.message.reply_text(summary, parse_mode="Markdown")
    
    # Create the actual Gmail account
    return await create_account(update, context)

async def create_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Actually create the Gmail account"""
    user_id = update.effective_user.id
    session = USER_SESSIONS[user_id]
    
    try:
        gmail_creator = GmailCreator()
        
        result = await gmail_creator.create_gmail_account(
            first_name=session['first_name'],
            last_name=session['last_name'],
            email=f"{session['username']}@gmail.com",
            password=session['password'],
            dob=session['dob']
        )
        
        if result['success']:
            # Save the account
            save_account(
                email=f"{session['username']}@gmail.com",
                password=session['password'],
                first_name=session['first_name'],
                last_name=session['last_name'],
                dob=session['dob']
            )
            
            success_msg = (
                f"✅ *Gmail Account Created Successfully!*\n\n"
                f"📧 Email: `{session['username']}@gmail.com`\n"
                f"🔐 Password: `{session['password']}`\n\n"
                f"✨ Your account is ready to use!\n"
                f"Go to gmail.com and login with these credentials.\n\n"
                f"_Command /start to create another account_"
            )
            
            await update.message.reply_text(success_msg, parse_mode="Markdown")
            
            logger.info(f"✅ Account created: {session['username']}@gmail.com")
            
        else:
            error_msg = (
                f"❌ Account creation failed:\n\n"
                f"{result.get('error', 'Unknown error')}\n\n"
                f"_Command /start to try again_"
            )
            await update.message.reply_text(error_msg, parse_mode="Markdown")
            logger.error(f"Account creation failed: {result.get('error')}")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n\n_Command /start to try again_",
            parse_mode="Markdown"
        )
        logger.error(f"Exception during account creation: {str(e)}")
    
    # Clear session
    if user_id in USER_SESSIONS:
        del USER_SESSIONS[user_id]
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation"""
    user_id = update.effective_user.id
    
    if user_id in USER_SESSIONS:
        del USER_SESSIONS[user_id]
    
    await update.message.reply_text(
        "❌ Process cancelled.\n\n_Command /start to create a new account_",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END

async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all created accounts"""
    accounts = load_accounts()
    
    if not accounts["accounts"]:
        await update.message.reply_text("📭 No accounts created yet.")
        return
    
    msg = f"📋 *Created Accounts* ({len(accounts['accounts'])} total)\n\n"
    
    for idx, acc in enumerate(accounts["accounts"][:10], 1):
        msg += f"{idx}. `{acc['email']}`\n"
        msg += f"   Password: `{acc['password']}`\n"
        msg += f"   Created: {acc['created_at'][:10]}\n\n"
    
    if len(accounts["accounts"]) > 10:
        msg += f"_...and {len(accounts['accounts'])-10} more_"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    accounts = load_accounts()
    
    msg = (
        f"📊 *Bot Statistics*\n\n"
        f"Total Accounts Created: `{len(accounts['accounts'])}`\n"
        f"Bot Status: ✅ Active\n"
        f"Deployment: 🚀 Render 24/7"
    )
    
    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    """Start the bot"""
    app = Application.builder().token(API_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ConversationStates.FIRST_NAME.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, first_name)
            ],
            ConversationStates.LAST_NAME.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, last_name)
            ],
            ConversationStates.DATE_OF_BIRTH.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, date_of_birth)
            ],
            ConversationStates.USERNAME.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, username)
            ],
            ConversationStates.PASSWORD.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, password)
            ],
            ConversationStates.CONFIRM_PASSWORD.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_password)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("list", list_accounts))
    app.add_handler(CommandHandler("stats", stats))
    
    logger.info("🚀 Bot started. Polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
