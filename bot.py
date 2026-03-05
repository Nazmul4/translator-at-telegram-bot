import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def translate_text(text):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": "en|bn",
            "de": "translator@gmail.com"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        translated = data["responseData"]["translatedText"]
        return translated
    except Exception as e:
        logger.error(f"অনুবাদ ত্রুটি: {e}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "অনুবাদ বট চালু আছে!\n\nযেকোনো মেসেজ বা চ্যানেল পোস্ট Forward করুন।"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.channel_post
    if not message:
        return
    text = message.text or message.caption
    if not text or not text.strip():
        return
    status_msg = await message.reply_text("অনুবাদ করছি...")
    translated = translate_text(text)
    if translated:
        await status_msg.edit_text(f"বাংলা অনুবাদ:\n\n{translated}")
    else:
        await status_msg.edit_text("অনুবাদ করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.CAPTION & ~filters.COMMAND, handle_message))
    logger.info("বট চালু হচ্ছে... (MyMemory)")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
