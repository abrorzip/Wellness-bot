#!/usr/bin/env python3
"""
Botni sinash uchun skript
"""

import sys
import os

# Bot modullarini import qilish
try:
    from course_data import COURSE_LESSONS
    from config import TELEGRAM_BOT_TOKEN
    print("[OK] Modullar muvaffaqiyatli import qilindi!")
except ImportError as e:
    print(f"[ERROR] Import xatoligi: {e}")
    sys.exit(1)

def test_course_data():
    print("\n[KURS] Kurs ma'lumotlarini sinash...")
    
    if not COURSE_LESSONS:
        print("[ERROR] Kurs darslari bosh!")
        return False
    
    for i, lesson in enumerate(COURSE_LESSONS, 1):
        required_keys = ["lesson_number", "title", "video_url", "description", 
                        "question", "options", "correct_answer", "explanation"]
        
        for key in required_keys:
            if key not in lesson:
                print(f"[ERROR] Dars {i}: '{key}' kalit so'zi yo'q!")
                return False
        
        if len(lesson["options"]) != 4:
            print(f"[ERROR] Dars {i}: 4 ta javob varianti kerak!")
            return False
        
        if lesson["correct_answer"] not in ["A", "B", "C", "D"]:
            print(f"[ERROR] Dars {i}: Noto'g'ri to'g'ri javob!")
            return False
    
    print(f"[OK] {len(COURSE_LESSONS)} ta dars topildi!")
    return True

def test_config():
    print("\n[CONFIG] Konfiguratsiyani sinash...")
    
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[ERROR] Bot tokeni o'zgartirilmagan!")
        print("   config.py faylida TELEGRAM_BOT_TOKEN ni o'zgartiring.")
        return False
    
    print("[OK] Bot tokeni o'rnatilgan!")
    return True

def main():
    print("[TEST] Botni sinash...")
    print("=" * 40)
    
    course_ok = test_course_data()
    config_ok = test_config()
    
    print("\n" + "=" * 40)
    
    if course_ok and config_ok:
        print("[OK] Barcha sinovlar muvaffaqiyatli o'tdi!")
        print("\nBotni ishga tushirish uchun:")
        print("python bot.py")
    else:
        print("[ERROR] Ba'zi sinovlar muvaffaqiyatsiz o'tdi!")
        print("   Xatoliklarni tuzating va qayta sinang.")

if __name__ == "__main__":
    main()
