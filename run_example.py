#!/usr/bin/env python3
"""
Пример запуска HYDRA бота с проверкой конфигурации
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Проверка переменных окружения"""
    print("🔍 Проверка конфигурации...")
    
    # Загружаем .env файл
    load_dotenv()
    
    # Проверяем BOT_TOKEN
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не найден в .env файле")
        print("   Создайте файл .env и добавьте:")
        print("   BOT_TOKEN=ваш_токен_бота")
        return False
    else:
        print("✅ BOT_TOKEN найден")
    
    # Проверяем ADMIN_CHAT_ID
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    if not admin_chat_id:
        print("❌ ADMIN_CHAT_ID не найден в .env файле")
        print("   Добавьте в .env файл:")
        print("   ADMIN_CHAT_ID=ваш_chat_id")
        return False
    else:
        print("✅ ADMIN_CHAT_ID найден")
    
    return True

def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    try:
        import telegram
        print("✅ python-telegram-bot установлен")
    except ImportError:
        print("❌ python-telegram-bot не установлен")
        print("   Установите: pip install python-telegram-bot")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv установлен")
    except ImportError:
        print("❌ python-dotenv не установлен")
        print("   Установите: pip install python-dotenv")
        return False
    
    return True

def check_files():
    """Проверка наличия файлов"""
    print("\n📁 Проверка файлов...")
    
    required_files = [
        'bot.py',
        'config.py',
        'database.py',
        'keyboards.py',
        'signals_simulator.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} найден")
        else:
            print(f"❌ {file} не найден")
            return False
    
    return True

def main():
    """Основная функция"""
    print("🚀 HYDRA BOT - ПРОВЕРКА ЗАПУСКА")
    print("=" * 50)
    
    # Проверяем все компоненты
    if not check_environment():
        print("\n❌ Ошибка конфигурации")
        print("   Следуйте инструкциям в SETUP.md")
        return False
    
    if not check_dependencies():
        print("\n❌ Ошибка зависимостей")
        print("   Установите: pip install -r requirements.txt")
        return False
    
    if not check_files():
        print("\n❌ Ошибка файлов")
        print("   Убедитесь, что все файлы на месте")
        return False
    
    print("\n✅ Все проверки пройдены!")
    print("\n🎯 Готов к запуску бота...")
    print("   Для запуска выполните: python bot.py")
    print("\n📖 Подробные инструкции в SETUP.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 