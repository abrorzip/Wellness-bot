#!/usr/bin/env python3
"""
Wellness Bot o'rnatish skripti
"""

import os
import sys
import subprocess

def check_python():
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ kerak!")
        sys.exit(1)
    print("✅ Python versiyasi: {}".format(sys.version))

def install_requirements():
    print("\n📦 Kutubxonalarni o'rnatish...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Kutubxonalar muvaffaqiyatli o'rnatildi!")
    except subprocess.CalledProcessError:
        print("❌ Kutubxonalarni o'rnatishda xatolik!")
        sys.exit(1)

def setup_token():
    print("\n🔑 Bot tokenini kiriting:")
    print("(@BotFather dan olishingiz mumkin)")
    token = input("Token: ").strip()
    
    if not token:
        print("❌ Token bo'sh bo'lishi mumkin emas!")
        return False
    
    with open("config.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("YOUR_BOT_TOKEN_HERE", token)
    
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Token saqlandi!")
    return True

def setup_instagram():
    print("\n📸 Instagram profilingizni kiriting:")
    instagram = input("Instagram username (masalan: wellness_blog): ").strip()
    
    if not instagram:
        print("❌ Instagram username bo'sh bo'lishi mumkin emas!")
        return False
    
    with open("config.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("your_wellness_profile", instagram)
    
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Instagram saqlandi!")
    return True

def main():
    print("🚀 Wellness Bot o'rnatish")
    print("=" * 40)
    
    check_python()
    install_requirements()
    
    if not setup_token():
        return
    
    if not setup_instagram():
        return
    
    print("\n" + "=" * 40)
    print("✅ O'rnatish tugallandi!")
    print("\nBotni ishga tushirish uchun:")
    print("python bot.py")
    print("\nYoki")
    print("python -m wellness_bot.bot")
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()
