import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes,
)

# ==================== কনফিগারেশন ====================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY")
TARGET_LANGUAGE    = "বাংলা"
# =====================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Gemini সেটআপ
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # ফ্রি ও দ্রুত


def translate_with_gemini(text: str) -> str:
    """Gemini AI দিয়ে টেক্সট অনুবাদ করে"""
    try:
        prompt = (
            f"নিচের টেক্সটটি {TARGET_LANGUAGE} ভাষায় অনুবাদ করো। "
            f"শুধু অনুবাদ দাও, কোনো ব্যাখ্যা বা অতিরিক্ত কথা লিখবে না। "
            f"যদি টেক্সটটি ইতিমধ্যে {TARGET_LANGUAGE} ভাষায় থাকে, তাহলে হুবহু ফেরত দাও।\n\n"
            f"টেক্সট:\n{text}"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini অনুবাদ ত্রুটি: {e}")
        return None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *অনুবাদ বট চালু আছে!*\n\n"
        "✅ যেকোনো চ্যানেল পোস্ট Forward করুন\n"
        "✅ অথবা সরাসরি মেসেজ পাঠান\n"
        f"📌 আমি স্বয়ংক্রিয়ভাবে {TARGET_LANGUAGE} ভাষায় অনুবাদ করব\n\n"
        "_Google Gemini AI দ্বারা চালিত_ ✨",
        parse_mode="Markdown"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.channel_post
    if not message:
        return

    text = message.text or message.caption
    if not text or not text.strip():
        return

    # ফরওয়ার্ড সোর্স শনাক্ত করুন
    source_info = ""
    if message.forward_origin:
        origin = message.forward_origin
        if hasattr(origin, "chat") and origin.chat:
            source_info = f"📢 *সোর্স:* {origin.chat.title}\n"
        elif hasattr(origin, "sender_user") and origin.sender_user:
            source_info = f"👤 *সোর্স:* {origin.sender_user.full_name}\n"

    status_msg = await message.reply_text("⏳ Gemini অনুবাদ করছে...")

    translated = translate_with_gemini(text)

    if translated:
        reply = (
            f"{source_info}"
            f"🌐 *{TARGET_LANGUAGE} অনুবাদ:*\n\n"
            f"{translated}"
        )
        await status_msg.edit_text(reply, parse_mode="Markdown")
    else:
        await status_msg.edit_text(
            "❌ অনুবাদ করতে সমস্যা হয়েছে। একটু পরে আবার চেষ্টা করুন।"
        )


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.CAPTION & ~filters.COMMAND, handle_message))

    logger.info("🤖 বট চালু হচ্ছে... (Gemini AI)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
