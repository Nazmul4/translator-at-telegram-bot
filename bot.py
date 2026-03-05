import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY")
TARGET_LANGUAGE    = "বাংলা"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")

def translate_with_gemini(text):
    try:
        prompt = f"নিচের টেক্সটটি {TARGET_LANGUAGE} ভাষায় অনুবাদ করো। শুধু অনুবাদ দাও।\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini ত্রুটি: {e}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *অনুবাদ বট চালু আছে!*\n\n✅ যেকোনো মেসেজ বা চ্যানেল পোস্ট Forward করুন\n_Gemini AI দ্বারা চালিত_ ✨",
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
    translated = translate_with_gemini(text)
    if translated:
        await status_msg.edit_text(f"🌐 *{TARGET_LANGUAGE} অনুবাদ:*\n\n{translated}", parse_mode="Markdown")
    else:
        await status_msg.edit_text("❌ অনুবাদ করতে সমস্যা হয়েছে।")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.CAPTION & ~filters.COMMAND, handle_message))
    logger.info("🤖 বট চালু হচ্ছে...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
