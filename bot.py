import logging
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
import random
import os
from config import (
    TELEGRAM_BOT_TOKEN, WELCOME_MESSAGE, START_MESSAGE,
    WRONG_ANSWER_MESSAGES, CORRECT_ANSWER_MESSAGES, FINAL_MESSAGE,
    INSTAGRAM_LINK, COURSE_PRICE, PAYME_MERCHANT_ID, CLICK_MERCHANT_ID,
    WEBHOOK, WEBHOOK_URL
)
from course_data import COURSE_LESSONS
from payment import create_course_payment

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

user_progress = {}


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


def get_keyboard_lesson(lesson_number):
    buttons = []
    for i in range(1, len(COURSE_LESSONS) + 1):
        if i <= lesson_number:
            buttons.append([InlineKeyboardButton(
                f"✅ Dars {i}",
                callback_data=f"lesson_{i}"
            )])
        else:
            buttons.append([InlineKeyboardButton(
                f"🔒 Dars {i}",
                callback_data="locked"
            )])
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = {
        "current_lesson": 1,
        "score": 0,
        "completed": False,
        "attempts": {},
        "paid": False
    }

    payment_text = f"""
Salom! Wellness kursiga xush kelibsiz!

Kurs narxi: {COURSE_PRICE:,} so'm

Kursni boshlash uchun to'lov qilishingiz kerak.
"""

    keyboard = [
        [InlineKeyboardButton("💳 Payme orqali to'lov", callback_data="pay_payme")],
        [InlineKeyboardButton("💳 Click orqali to'lov", callback_data="pay_click")],
        [InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        payment_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    user_id = query.from_user.id
    data = query.data

    if data == "pay_payme" or data == "pay_click":
        user_progress[user_id]["paid"] = True

        keyboard = [
            [InlineKeyboardButton("🚀 Kursni boshlash", callback_data="start_course")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = "To'lov muvaffaqiyatli qabul qilindi!\n\nEndi kursni boshlashingiz mumkin."

        await query.edit_message_text(
            msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )


async def start_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    user_id = query.from_user.id
    if user_id not in user_progress:
        user_progress[user_id] = {
            "current_lesson": 1,
            "score": 0,
            "completed": False,
            "attempts": {},
            "paid": False
        }

    if not user_progress[user_id].get("paid", False):
        keyboard = [
            [InlineKeyboardButton("💳 Payme orqali to'lov", callback_data="pay_payme")],
            [InlineKeyboardButton("💳 Click orqali to'lov", callback_data="pay_click")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = f"Avval to'lov qiling!\n\nKurs narxi: {COURSE_PRICE:,} so'm"

        await query.edit_message_text(
            msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return

    lesson = COURSE_LESSONS[0]
    await send_lesson(query.message, user_id, lesson)


async def send_lesson(message, user_id, lesson):
    lesson_num = lesson["lesson_number"]

    text = f"""
📚 <b>Dars {lesson_num}: {lesson['title']}</b>

{lesson['description']}

🎥 Video havolasi: {lesson['video_url']}

Savolga javob bering:
{lesson['question']}
"""
    buttons = []
    for option in lesson["options"]:
        buttons.append([InlineKeyboardButton(
            option,
            callback_data=f"answer_{lesson_num}_{option[0]}"
        )])

    reply_markup = InlineKeyboardMarkup(buttons)

    await message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    user_id = query.from_user.id
    data = query.data

    if not data.startswith("answer_"):
        return

    parts = data.split("_")
    lesson_num = int(parts[1])
    selected_answer = parts[2]

    lesson = COURSE_LESSONS[lesson_num - 1]
    correct = lesson["correct_answer"]

    if user_id not in user_progress:
        user_progress[user_id] = {
            "current_lesson": 1,
            "score": 0,
            "completed": False,
            "attempts": {},
            "paid": False
        }

    if user_id not in user_progress[user_id]["attempts"]:
        user_progress[user_id]["attempts"][lesson_num] = 0

    user_progress[user_id]["attempts"][lesson_num] += 1

    if selected_answer == correct:
        user_progress[user_id]["score"] += 1

        msg = random.choice(CORRECT_ANSWER_MESSAGES)
        msg += f"\n\n{lesson['explanation']}"

        if lesson_num < len(COURSE_LESSONS):
            user_progress[user_id]["current_lesson"] = lesson_num + 1

            keyboard = [
                [InlineKeyboardButton("▶️ Keyingi video", callback_data=f"lesson_{lesson_num + 1}")],
                [InlineKeyboardButton("📊 Progress", callback_data="progress")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                msg,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        else:
            user_progress[user_id]["completed"] = True

            keyboard = [
                [InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            final_msg = f"{msg}\n\n{FINAL_MESSAGE}"
            await query.edit_message_text(
                final_msg,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
    else:
        attempts = user_progress[user_id]["attempts"][lesson_num]

        if attempts >= 3:
            msg = f"Kechirasiz, siz 3 ta urinishni o'tkazdingiz.\n\n{lesson['explanation']}\n\nVideoni qayta ko'rishni tavsiya qilaman."

            keyboard = [
                [InlineKeyboardButton("🔄 Qayta urinish", callback_data=f"retry_{lesson_num}")],
                [InlineKeyboardButton("▶️ Keyingi video", callback_data=f"lesson_{lesson_num + 1}" if lesson_num < len(COURSE_LESSONS) else "complete")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            msg = random.choice(WRONG_ANSWER_MESSAGES)
            msg += f"\n\nQaytadan urinib ko'ring ({attempts}/3)"

            buttons = []
            for option in lesson["options"]:
                buttons.append([InlineKeyboardButton(
                    option,
                    callback_data=f"answer_{lesson_num}_{option[0]}"
                )])
            buttons.append([InlineKeyboardButton("🔄 Qayta urinish", callback_data=f"retry_{lesson_num}")])
            reply_markup = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(
            msg,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )


async def handle_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    user_id = query.from_user.id
    data = query.data

    if data == "locked":
        try:
            await query.answer("Bu dars hali ochilmagan!", show_alert=True)
        except Exception:
            pass
        return

    if data.startswith("lesson_"):
        lesson_num = int(data.split("_")[1])
        lesson = COURSE_LESSONS[lesson_num - 1]

        if user_id in user_progress and user_progress[user_id]["current_lesson"] >= lesson_num:
            await send_lesson(query.message, user_id, lesson)
        else:
            try:
                await query.answer("Avval oldingi darslarni tugating!", show_alert=True)
            except Exception:
                pass

    elif data.startswith("retry_"):
        lesson_num = int(data.split("_")[1])
        lesson = COURSE_LESSONS[lesson_num - 1]

        if user_id in user_progress:
            user_progress[user_id]["attempts"][lesson_num] = 0

        await send_lesson(query.message, user_id, lesson)

    elif data == "progress":
        if user_id in user_progress:
            progress = user_progress[user_id]
            completed = progress["current_lesson"] - 1
            total = len(COURSE_LESSONS)
            score = progress["score"]

            msg = f"""
📊 <b>Sizning progressingiz:</b>

✅ Tugatilgan darslar: {completed}/{total}
⭐ Ball: {score}
📈 Foiz: {completed/total*100:.0f}%

Davom eting!
"""
            keyboard = [
                [InlineKeyboardButton("▶️ Davom etish", callback_data=f"lesson_{progress['current_lesson']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                msg,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
🤖 <b>Wellness Bot Yordamchisi</b>

Bu bot sizga wellness kursini o'tashda yordam beradi.

<b>Buyruqlar:</b>
/start - Kursni boshlash
/help - Yordam
/progress - Progressni ko'rish

<b>Qanday ishlaydi?</b>
1. Har bir videoni diqqat bilan ko'ring
2. Videodan so'ng savolga javob bering
3. To'g'ri javob = keyingi video
4. Noto'g'ri javob = videoni qayta ko'ring

Savollaringiz bo'lsa, menga yozing!
""",
        parse_mode=ParseMode.HTML
    )


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_progress:
        await update.message.reply_text(
            "Avval kursni boshlang: /start"
        )
        return

    progress = user_progress[user_id]
    completed = progress["current_lesson"] - 1
    total = len(COURSE_LESSONS)
    score = progress["score"]

    msg = f"""
📊 <b>Sizning progressingiz:</b>

✅ Tugatilgan darslar: {completed}/{total}
⭐ Ball: {score}
📈 Foiz: {completed/total*100:.0f}%

Davom eting!
"""
    keyboard = [
        [InlineKeyboardButton("▶️ Davom etish", callback_data=f"lesson_{progress['current_lesson']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        msg,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


def main():
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    print("Health server ishga tushdi...")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("progress", progress_command))

    application.add_handler(CallbackQueryHandler(
        handle_payment,
        pattern="^(pay_|confirm_)"
    ))

    application.add_handler(CallbackQueryHandler(
        start_course,
        pattern="^start_course$"
    ))

    application.add_handler(CallbackQueryHandler(
        handle_answer,
        pattern="^answer_"
    ))

    application.add_handler(CallbackQueryHandler(
        handle_lesson,
        pattern="^(lesson_|locked|retry_|progress)"
    ))

    application.add_handler(CallbackQueryHandler(
        handle_lesson,
        pattern="^complete$"
    ))

    if WEBHOOK and WEBHOOK_URL:
        print(f"Webhook rejimda ishlayapti: {WEBHOOK_URL}")
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            url_path="bot",
            webhook_url=f"{WEBHOOK_URL}/bot"
        )
    else:
        print("Polling rejimda ishlayapti...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
