import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Instagram profile link
INSTAGRAM_LINK = os.getenv("INSTAGRAM_LINK")

# Payment settings
PAYME_MERCHANT_ID = os.getenv("PAYME_MERCHANT_ID")
PAYME_SECRET_KEY = os.getenv("PAYME_SECRET_KEY")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY")
COURSE_PRICE = int(os.getenv("COURSE_PRICE", 50000))

# Webhook settings
WEBHOOK = os.getenv("WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Course settings
WELCOME_MESSAGE = """
Salom! Wellness kursiga xush kelibsiz!

Men sizning shaxsiy wellness yordamchingizman.
Kursimiz sizning sog'lig'ingiz va farovonligingiz uchun yaratilgan.

Instagram profile: {instagram_link}

Boshlash uchun /start_buyruq bosing.
""".format(instagram_link=INSTAGRAM_LINK)

START_MESSAGE = """
Kursni boshlaymiz!

Har bir videoni diqqat bilan ko'ring.
Videodan so'ng sizga savol beriladi.
To'g'ri javob bersangiz, keyingi video o'tadi.
Noto'g'ri javob bersangiz, videoni qayta ko'rish kerak bo'ladi.

Tayyormisiz? Boshlaymiz!
"""

# Emotional messages for wrong answers
WRONG_ANSWER_MESSAGES = [
    "Kechirasiz, noto'g'ri javob. O'z sog'lig'ingizga e'tiborsizlik qilmang, videoni qayta ko'ring!",
    "Xato javob. Sog'ligingiz muhim, iltimos videoni yana bir marta ko'ring!",
    "Noto'g'ri. O'zingiz uchun vaqt ajrating va videoni qayta ko'rib chiqing!",
    "Javobingiz noto'g'ri. Wellness - bu jiddiy masala, videoni qayta boring!",
    "Afsus, noto'g'ri. Sog'liq - bu boylik, videoni qayta ko'rishni unutmang!",
    "Xato. O'z salomatligingiz haqida qayta o'ylang va videoni qayta ko'ring!",
    "Noto'g'ri javob. Wellness yo'lingizda davom eting, videoni qayta boring!",
    "Kechirasiz, bu noto'g'ri. O'zingizni yaxshilash uchun videoni qayta ko'ring!"
]

# Correct answer messages
CORRECT_ANSWER_MESSAGES = [
    "To'g'ri! Ajoyib! Keyingi video bilan davom etamiz!",
    "Zo'r! Siz bilimdon ekansiz! Keyingi videoga o'tamiz!",
    "Barakalla! To'g'ri javob! Keyingi video kutyapti!",
    "Ajoyib! Davom eting! Keyingi video bilan tanishamiz!",
    "Zo'r natija! Siz haqiqiy wellness o'quvchisiz!"
]

# Final message
FINAL_MESSAGE = """
Tabriklaymiz! Kursni muvaffaqiyatli yakunladingiz!

Siz endi wellness haqida ko'p narsa bilasiz.
Esda tuting: sog'liq - bu boylik!

Instagram profile: {instagram_link}

Boshqa kurslar uchun bizni kuzatib boring!
""".format(instagram_link=INSTAGRAM_LINK)
