# Gmail Account Creator Bot

Telegram bot to generate and store Gmail account credentials.

## Features
- Create multiple Gmail accounts
- Store credentials locally
- Export accounts as JSON
- View created accounts
- Delete all accounts

## Commands
- `/create <first> <last> [count]` - Create accounts
- `/list` - Show all accounts
- `/stats` - Bot statistics
- `/export` - Export as JSON
- `/clear` - Delete all

## Setup
1. Clone repo
2. Install: `pip install -r requirements.txt`
3. Run: `python3 main.py`

## Deployed on Render
Live bot running 24/7

## Tech
- Python 3.11
- python-telegram-bot
- JSON storage
