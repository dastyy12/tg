#!/usr/bin/env python3
"""
Hydra Bot - Background Worker Version
Оптимизирован для развертывания на Render как Background Worker
"""

import os
import sys
import logging
from bot import main

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def start_bot():
    """Запуск бота с обработкой ошибок"""
    try:
        logger.info("Starting Hydra Bot (Background Worker mode)...")
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed with error: {e}")
        # Перезапуск через 30 секунд
        import time
        time.sleep(30)
        start_bot()

if __name__ == '__main__':
    # Проверяем переменные окружения
    bot_token = os.getenv('BOT_TOKEN')
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    
    if not bot_token:
        logger.error("BOT_TOKEN not set in environment variables")
        sys.exit(1)
    
    if not admin_chat_id:
        logger.error("ADMIN_CHAT_ID not set in environment variables")
        sys.exit(1)
    
    logger.info("Environment variables check passed")
    logger.info(f"Admin Chat ID: {admin_chat_id}")
    
    # Запускаем бота
    start_bot() 