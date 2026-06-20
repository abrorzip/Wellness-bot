import logging
import asyncio
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode
import random
import os
from config import (
    TELEGRAM_BOT_TOKEN, WELCOME_MESSAGE,
    WRONG_ANSWER_MESSAGES, CORRECT_ANSWER_MESSAGES, FINAL_MESSAGE,
    INSTAGRAM_LINK, COURSE_PRICE,
    WEBHOOK, WEBHOOK_URL
)
from course_data import COURSE_LESSONS
from payment import create_course_payment

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_progress = {}


async def health(request):
    return web.Response(text="OK", content_type="text/plain")


async def webhook_handler(request):
    app = request.app["bot_app"]
    update = Update.de_json(await request.json(), app.bot)
    await app.update_queue.put(update)
    return web.Response()


async def on_startup(app):
    await app.bot.initialize()
    await app.bot.start()
    await app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/webhook",
        allowed_updates=Update.ALL_TYPES
    )
    print(f"Webhook o'rnatildi: {WEBHOOK_URL}/webhook")


async def on_shutdown(app):
    await app.bot.stop()
    await app.bot.shutdown()


async def start(update: Update, context):
    user_id = update.effective_user.id
    user_progress[user_id] = {
        "current_lesson": 1,
        "score": 0,
        "completed": False,
        "attempts": {},
        "paid": False
    }

    text = f"Salom! Wellness kursiga xush kelibsiz!\n\nKurs narxi: {COURSE_PRICE:,} so'm\n\nKursni boshlash uchun to'lov qiling."

    keyboard = [
        [InlineKeyboardButton("💳 Payme orqali to'lov", callback_data="pay_payme")],
        [InlineKeyboardButton("💳 Click orqali to'lov", callback_data="pay_click")],
        [InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK)]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def handle_payment(update: Update, context):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass

    user_id = query.from_user.id
    user_progress[user_id]["paid"] = True

    keyboard = [
        [InlineKeyboardButton("🚀 Kursni boshlash", callback_data="start_course")]
    ]

    await query.edit_message_text(
        "To'lov muvaffaqiyatli qabul qilindi!\n\nEndi kursni boshlashingiz mumkin.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


async def start_course(update: Update, context):
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
        await query.edit_message_text(
            f"Avval to'lov qiling!\n\nKurs narxi: {COURSE_PRICE:,} so'm",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.HTML
        )
        return

    lesson = COURSE_LESSONS[0]
    await send_lesson(query.message, user_id, lesson)


async def send_lesson(message, user_id, lesson):
    lesson_num = lesson["lesson_number"]

    text = f"📚 Dars {lesson_num}: {lesson['title']}\n\n{lesson['description']}\n\n🎥 Video: {lesson['video_url']}\n\nSavol: {lesson['question']}"

    buttons = []
    for option in lesson["options"]:
        buttons.append([InlineKeyboardButton(option, callback_data=f"answer_{lesson_num}_{option[0]}")])

    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )


async def handle_answer(update: Update, context):
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
        user_progress[user_id] = {"current_lesson": 1, "score": 0, "completed": False, "attempts": {}, "paid": True}

    if user_id not in user_progress[user_id]["attempts"]:
        user_progress[user_id]["attempts"][lesson_num] = 0

    user_progress[user_id]["attempts"][lesson_num] += 1

    if selected_answer == correct:
        user_progress[user_id]["score"] += 1
        msg = random.choice(CORRECT_ANSWER_MESSAGES) + f"\n\n{lesson['explanation']}"

        if lesson_num < len(COURSE_LESSONS):
            user_progress[user_id]["current_lesson"] = lesson_num + 1
            keyboard = [
                [InlineKeyboardButton("▶️ Keyingi video", callback_data=f"lesson_{lesson_num + 1}")],
                [InlineKeyboardButton("📊 Progress", callback_data="progress")]
            ]
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        else:
            user_progress[user_id]["completed"] = True
            keyboard = [[InlineKeyboardButton("📸 Instagram", url=INSTAGRAM_LINK)]]
            await query.edit_message_text(f"{msg}\n\n{FINAL_MESSAGE}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    else:
        attempts = user_progress[user_id]["attempts"][lesson_num]

        if attempts >= 3:
            msg = f"Kechirasiz, 3 ta urinish o'tkazdingiz.\n\n{lesson['explanation']}\n\nVideoni qayta ko'ring."
            keyboard = [
                [InlineKeyboardButton("🔄 Qayta urinish", callback_data=f"retry_{lesson_num}")],
                [InlineKeyboardButton("▶️ Keyingi video", callback_data=f"lesson_{lesson_num + 1}" if lesson_num < len(COURSE_LESSONS) else "complete")]
            ]
        else:
            msg = random.choice(WRONG_ANSWER_MESSAGES) + f"\n\nQaytadan urinib ko'ring ({attempts}/3)"
            buttons = []
            for option in lesson["options"]:
                buttons.append([InlineKeyboardButton(option, callback_data=f"answer_{lesson_num}_{option[0]}")])
            buttons.append([InlineKeyboardButton("🔄 Qayta urinish", callback_data=f"retry_{lesson_num}")])
            keyboard = buttons

        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)


async def handle_lesson(update: Update, context):
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

    elif data.startswith("retry_"):
        lesson_num = int(data.split("_")[1])
        if user_id in user_progress:
            user_progress[user_id]["attempts"][lesson_num] = 0
        await send_lesson(query.message, user_id, COURSE_LESSONS[lesson_num - 1])

    elif data == "progress":
        if user_id in user_progress:
            progress = user_progress[user_id]
            completed = progress["current_lesson"] - 1
            total = len(COURSE_LESSONS)
            score = progress["score"]
            msg = f"📊 Progress:\n\n✅ Darslar: {completed}/{total}\n⭐ Ball: {score}\n📈 Foiz: {completed/total*100:.0f}%"
            keyboard = [[InlineKeyboardButton("▶️ Davom etish", callback_data=f"lesson_{progress['current_lesson']}")]]
            await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)


async def help_command(update: Update, context):
    await update.message.reply_text(
        "🤖 Wellness Bot\n\nBuyruqlar:\n/start - Boshlash\n/help - Yordam\n/progress - Progress",
        parse_mode=ParseMode.HTML
    )


async def progress_command(update: Update, context):
    user_id = update.effective_user.id
    if user_id not in user_progress:
        await update.message.reply_text("Avval kursni boshlang: /start")
        return

    progress = user_progress[user_id]
    completed = progress["current_lesson"] - 1
    total = len(COURSE_LESSONS)
    score = progress["score"]
    msg = f"📊 Progress:\n\n✅ Darslar: {completed}/{total}\n⭐ Ball: {score}\n📈 Foiz: {completed/total*100:.0f}%"
    keyboard = [[InlineKeyboardButton("▶️ Davom etish", callback_data=f"lesson_{progress['current_lesson']}")]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)


def main():
    if WEBHOOK and WEBHOOK_URL:
        print(f"Webhook rejimda: {WEBHOOK_URL}")

        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("progress", progress_command))
        application.add_handler(CallbackQueryHandler(handle_payment, pattern="^(pay_|confirm_)"))
        application.add_handler(CallbackQueryHandler(start_course, pattern="^start_course$"))
        application.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))
        application.add_handler(CallbackQueryHandler(handle_lesson, pattern="^(lesson_|locked|retry_|progress|complete)$"))

        app = web.Application()
        app["bot_app"] = application
        app.router.add_get("/", health)
        app.router.add_post("/webhook", webhook_handler)
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        port = int(os.getenv("PORT", 8443))
        print(f"Server port: {port}")
        web.run_app(app, host="0.0.0.0", port=port)
    else:
        print("Polling rejimda ishlayapti...")

        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("progress", progress_command))
        application.add_handler(CallbackQueryHandler(handle_payment, pattern="^(pay_|confirm_)"))
        application.add_handler(CallbackQueryHandler(start_course, pattern="^start_course$"))
        application.add_handler(CallbackQueryHandler(handle_answer, pattern="^answer_"))
        application.add_handler(CallbackQueryHandler(handle_lesson, pattern="^(lesson_|locked|retry_|progress|complete)$"))

        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
