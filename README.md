# Wellness Telegram Bot

Wellness kursini Telegram orqali o'tash uchun bot.

## O'rnatish

1. Python o'rnatilgan bo'lishi kerak (3.7+)

2. Kerakli kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

3. Bot tokenini olish uchun @BotFather ga murojaat qiling:
   - Telegramda @BotFather ni toping
   - /newboy buyrug'ini yuboring
   - Bot nomini kiriting
   - Token oling

4. config.py faylida quyidagilarni o'zgartiring:
```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
INSTAGRAM_LINK = "https://instagram.com/sizning_profilingiz"

# To'lov tizimi (Payme uchun)
PAYME_MERCHANT_ID = "YOUR_PAYME_MERCHANT_ID"
PAYME_SECRET_KEY = "YOUR_PAYME_SECRET_KEY"

# To'lov tizimi (Click uchun)
CLICK_MERCHANT_ID = "YOUR_CLICK_MERCHANT_ID"
CLICK_SECRET_KEY = "YOUR_CLICK_SECRET_KEY"

# Kurs narxi (so'mda)
COURSE_PRICE = 50000  # 50,000 so'm
```

5. course_data.py faylida video havolalarini o'zgartiring:
   - Har bir dars uchun haqiqiy video havolasini kiriting
   - Savollarni o'zgartiring

6. Botni ishga tushiring:
```bash
python bot.py
```

## Bot Buyruqlari

- `/start` - Kursni boshlash
- `/help` - Yordam
- `/progress` - Progressni ko'rish

## Bot Funksiyalari

1. **Kurs videolari**: Har bir dars uchun video yuboriladi
2. **Savol-javob**: Videodan so'ng savol beriladi
3. **To'g'ri javob**: Keyingi video o'tiladi
4. **Noto'g'ri javob**: Videoni qayta ko'rish kerak
5. **Emotsional xabarlar**: Foydalanuvchini rag'batlantirish
6. **Instagram havolasi**: Instagram profilega o'tish

## Kurs Tuzilishi

10 ta dars mavjud:
1. Wellness nima?
2. Sog'lom ovqatlanish
3. Meditatsiya va stress
4. Jismoniy faollik
5. Sog'lom uyqu
6. Suvi iste'moli
7. Ruhiy salomatlik
8. Yomon odatlarni tashlash
9. Tabiat bilan bog'lanish
10. Kurs yakuni

## Texnik Tafsilotlar

- Python 3.7+
- python-telegram-bot kutubxonasi
- Foydalanuvchi progressini saqlash (xotirada)
- Inline tugmalar bilan interaktivlik
