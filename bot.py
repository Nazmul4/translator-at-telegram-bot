import os
import logging
from deep_translator import GoogleTranslator
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TARGET_LANGUAGE    = "bn"  # বাংলা

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def translate_text(text):
    try:
        return GoogleTranslator(source="auto", target=TARGET_LANGUAGE).translate(text)
    except Exception as e:
        logger.error(f"অনুবাদ ত্রুটি: {e}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *অনুবাদ বট চালু আছে!*\n\n✅ যেকোনো মেসেজ বা চ্যানেল পোস্ট Forward করুন\n_Google Translate দ্বারা চালিত_ ✨",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.channel_post
    if not message:
        return
    text = message.text or message.caption
    if not text or not text.strip():
        return
    status_msg = await message.reply_text("⏳ অনুবাদ করছি...")
    translated = translate_text(text)
    if translated:
        await status_msg.edit_text(f"🌐 *বাংলা অনুবাদ:*\n\n{translated}", parse_mode="Markdown")
    else:
        await status_msg.edit_text("❌ অনুবাদ করতে সমস্যা হয়েছে।")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.CAPTION & ~filters.COMMAND, handle_message))
    logger.info("🤖 বট চালু হচ্ছে... (Google Translate)")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
```

---

এরপর `requirements.txt` ও বদলান:
```
python-telegram-bot==21.6
deep-translator==1.11.4
