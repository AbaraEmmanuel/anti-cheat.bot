from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta, time
import asyncio
import logging

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")  
firebase_admin.initialize_app(cred, {"databaseURL": "https://anti-cheat-b-default-rtdb.firebaseio.com"})

# Admin/Moderator Config
MODERATOR_ID = 7461926970
ADMINS_ID = 7461926970  # Can be expanded to a list like [7461926970, 123456789]

# --- Bot Commands ---
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! Use /submit <wallet_address> to claim your win. You can only submit once every 42 hours.")

async def submit_address(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)  
    username = user.username or "NoUsername"
    address = " ".join(context.args)

    if not address:
        await update.message.reply_text("Usage: /submit <wallet_address>")
        return

    current_date = datetime.now()
    ref = db.reference(f"winners/{user_id}")
    user_data = ref.get()

    if user_data:
        if "win_dates" not in user_data:
            user_data["win_dates"] = []

        last_submission = datetime.strptime(user_data.get("last_submission", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
        if current_date - last_submission < timedelta(hours=42):
            await update.message.reply_text("⚠️ You can only submit once every 42 hours.")
            return

        user_data["wins"] += 1
        user_data["addresses"].append(address)
        user_data["win_dates"].append(current_date.strftime("%Y-%m-%d"))
    else:
        user_data = {
            "username": username,
            "wins": 1,
            "addresses": [address],
            "win_dates": [current_date.strftime("%Y-%m-%d")],
            "last_submission": current_date.strftime("%Y-%m-%d %H:%M:%S")
        }

    user_data["last_submission"] = current_date.strftime("%Y-%m-%d %H:%M:%S")
    ref.set(user_data)

    # Notify admin
    mod_message = (
        f"📢 New Submission!\n"
        f"👤 User: {username} (ID: {user_id})\n"
        f"💳 Address: {address}\n"
        f"🏆 Total Wins: {user_data['wins']}"
    )
    await context.bot.send_message(chat_id=MODERATOR_ID, text=mod_message)
    await update.message.reply_text(f"✅ Address received! You've won {user_data['wins']} times.")

async def check_winners(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMINS_ID:
        await update.message.reply_text("❌ Admin-only command.")
        return

    winners = db.reference("winners").get()
    if not winners:
        await update.message.reply_text("No winners yet.")
        return

    message = "🏆 Winners 🏆\n\n"
    for user_id, data in winners.items():
        win_dates = ", ".join(data["win_dates"])
        addresses = ", ".join(data["addresses"])
        message += (
            f"👤 {data['username']} (ID: {user_id})\n"
            f"🏆 Wins: {data['wins']}\n"
            f"📅 Dates: {win_dates}\n"
            f"💳 Addresses: {addresses}\n\n"
        )
    await update.message.reply_text(message)

# --- Automated Cleanup ---
async def cleanup_winners(context: ContextTypes.DEFAULT_TYPE):
    winners = db.reference("winners").get()
    if not winners:
        return

    deleted_users = 0
    for user_id, data in winners.items():
        if "win_dates" not in data:
            continue

        new_win_dates = [
            date for date in data["win_dates"] 
            if datetime.strptime(date, "%Y-%m-%d") > datetime.now() - timedelta(weeks=3)
        ]

        if not new_win_dates:
            db.reference(f"winners/{user_id}").delete()
            deleted_users += 1
        else:
            db.reference(f"winners/{user_id}/win_dates").set(new_win_dates)

    #print(f"Cleanup: Deleted {deleted_users} old records.")  Optional log

# --- Bot Setup ---
def main():
    bot_token = "7618502777:AAF7vV7xiYlCVaRcfBibkrzgMCopNWWvraw"
    application = Application.builder().token(bot_token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("submit", submit_address))
    application.add_handler(CommandHandler("winners", check_winners))

    # Schedule daily cleanup at 3 AM UTC
    job_queue = application.job_queue
    job_queue.run_daily(cleanup_winners, time=time(hour=3, minute=0))

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Now you can add logging in key parts of your code
    logging.debug('Bot is starting...')

    # Start bot
    application.run_polling()
    print("Bot is running with automated cleanup!")

if __name__ == "__main__":
    main()