import os
import threading
import logging
from flask import Flask

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_bot():
    """Запуск бота в отдельном потоке"""
    try:
        from bot_web import main
        logger.info("Starting Hydra Bot (Web Service mode) in background thread...")
        main()
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        # Попробуем запустить основную версию как fallback
        try:
            from bot import main as main_fallback
            logger.info("Trying fallback bot version...")
            main_fallback()
        except Exception as e2:
            logger.error(f"Fallback bot also failed: {e2}")

if __name__ == '__main__':
    # Проверяем переменные окружения
    bot_token = os.getenv('BOT_TOKEN')
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    
    if not bot_token:
        logger.error("BOT_TOKEN not set in environment variables")
    else:
        logger.info("BOT_TOKEN found in environment")
    
    if not admin_chat_id:
        logger.error("ADMIN_CHAT_ID not set in environment variables")
    else:
        logger.info(f"ADMIN_CHAT_ID: {admin_chat_id}")
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Простой веб-сервер для проверки работоспособности
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return 'Hydra Bot is running!'
    
    @app.route('/health')
    def health():
        return 'OK'
    
    @app.route('/status')
    def status():
        return {
            'status': 'running',
            'bot_token_set': bool(bot_token),
            'admin_chat_id_set': bool(admin_chat_id)
        }
    
    # Запускаем Flask на порту из переменной окружения или 10000
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port) 