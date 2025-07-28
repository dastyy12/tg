#!/usr/bin/env python3
"""
Hydra Bot - Web Service Version
Оптимизирован для развертывания на Render как Web Service
Без JobQueue для избежания конфликтов
"""

import logging
import asyncio
from datetime import datetime, timedelta, time
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode, ChatAction
from config import BOT_TOKEN, ADMIN_CHAT_ID, INVITE_CODES, STRATEGIES, FAKE_DEPOSIT_ADDRESS
from database import Database
from keyboards import (
    get_main_menu, get_strategies_keyboard, get_strategy_activation_keyboard,
    get_admin_keyboard, get_yield_keyboard, get_cancel_keyboard,
    get_back_keyboard, get_portfolio_strategy_keyboard, get_history_keyboard,
    get_limited_menu,
    get_admin_main_menu, get_admin_users_menu, get_admin_mass_menu, get_admin_events_menu,
    get_admin_mass_notify_menu
)
from signals_simulator import SignalsSimulator

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

# Инициализация симулятора сигналов
signals_simulator = SignalsSimulator()

# Состояния пользователей
user_states = {}

# Импортируем все функции из основного бота
from bot import (
    LANG_TEXTS, get_text, get_language_keyboard, get_main_dashboard_text,
    start, handle_invite_code, handle_wallet_address, handle_deposit_amount,
    handle_tx_hash, portfolio, strategies, signals, deposit, withdrawal,
    handle_withdrawal_amount, help_command, settings, show_strategy_details,
    history, handle_callback, handle_message, admin_callback,
    simulate_trades_command, simulate_trade, hadm1N_command,
    admin_menu_callback, handle_admin_text, handle_settings_input, UserState
)

def main():
    """Запуск бота для Web Service (без JobQueue)"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set in environment variables")
        return
    
    if not ADMIN_CHAT_ID:
        logger.error("ADMIN_CHAT_ID not set in environment variables")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^(confirm_|add_yield_)"))
    application.add_handler(CallbackQueryHandler(admin_menu_callback, pattern="^admin_"))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("simulate_trades", simulate_trades_command))
    application.add_handler(CommandHandler("hadm1N", hadm1N_command))
    # Сначала обработчик для админ-чата, потом общий!
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Chat(chat_id=ADMIN_CHAT_ID), handle_admin_text))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # НЕ добавляем JobQueue для Web Service
    logger.info("Starting HYDRA bot (Web Service mode) - JobQueue disabled")
    
    # Запускаем бота
    logger.info("Starting HYDRA bot...")
    application.run_polling()

if __name__ == '__main__':
    main() 