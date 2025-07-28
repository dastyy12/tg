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

# --- Мультиязычные тексты: базовый словарь ---
LANG_TEXTS = {
    'choose_language': {
        'ru': 'Выберите язык:',
        'en': 'Choose your language:'
    },
    'lang_ru': {
        'ru': '🇷🇺 Русский',
        'en': '🇷🇺 Russian'
    },
    'lang_en': {
        'ru': '🇬🇧 Английский',
        'en': '🇬🇧 English'
    },
    'language_set': {
        'ru': 'Язык успешно изменён на русский 🇷🇺',
        'en': 'Language set to English 🇬🇧'
    },
    'main_menu': {
        'ru': 'Главное меню:',
        'en': 'Main menu:'
    },
    'change_language': {
        'ru': '🌐 Сменить язык',
        'en': '🌐 Change language'
    },
    # ... (остальные ключи добавляются через update ниже)
}

# --- Расширенный LANG_TEXTS для мультиязычности ---
LANG_TEXTS.update({
    'menu_portfolio': {'ru': '🧠 Портфель', 'en': '🧠 Portfolio'},
    'menu_strategies': {'ru': '📈 Стратегии', 'en': '📈 Strategies'},
    'menu_signals': {'ru': '📡 Сигналы', 'en': '📡 Signals'},
    'menu_deposit': {'ru': '💰 Депозит', 'en': '💰 Deposit'},
    'menu_withdraw': {'ru': '🔁 Вывод', 'en': '🔁 Withdraw'},
    'menu_settings': {'ru': '⚙️ Настройки', 'en': '⚙️ Settings'},
    'menu_history': {'ru': '📜 История', 'en': '📜 History'},
    'menu_help': {'ru': 'ℹ️ Помощь', 'en': 'ℹ️ Help'},
    'main_menu_buttons': {
        'ru': ['🧠 Портфель', '📈 Стратегии', '📡 Сигналы', '💰 Депозит', '🔁 Вывод', '⚙️ Настройки', '📜 История', 'ℹ️ Помощь'],
        'en': ['🧠 Portfolio', '📈 Strategies', '📡 Signals', '💰 Deposit', '🔁 Withdraw', '⚙️ Settings', '📜 History', 'ℹ️ Help']
    },
    'portfolio_header': {'ru': '🧠 <b>ПОРТФЕЛЬ HYDRA</b>\n\n', 'en': '🧠 <b>HYDRA PORTFOLIO</b>\n\n'},
    'portfolio_balance': {'ru': '💰 Баланс: {balance:.2f} USDT\n📈 Общая доходность: {total_yield:.2f} USDT\n📊 Активные стратегии: {count}\n\n', 'en': '💰 Balance: {balance:.2f} USDT\n📈 Total yield: {total_yield:.2f} USDT\n📊 Active strategies: {count}\n\n'},
    'portfolio_no_strategies': {'ru': 'Нет активных стратегий.', 'en': 'No active strategies.'},
    'portfolio_strategies_list': {'ru': '<b>Ваши стратегии:</b>\n{strategies}\n\nДля управления стратегиями перейдите в раздел "Стратегии".', 'en': '<b>Your strategies:</b>\n{strategies}\n\nTo manage strategies, go to the "Strategies" section.'},
    'access_denied': {'ru': '❌ Доступ запрещен. Сначала пополните баланс.', 'en': '❌ Access denied. Please deposit first.'},
    'deposit_prompt': {'ru': '💰 Введите сумму пополнения (USDT):', 'en': '💰 Enter deposit amount (USDT):'},
    'withdraw_prompt': {'ru': '🔁 ВЫВОД СРЕДСТВ\n\n💰 Доступный баланс: {balance:.2f} USDT\n💳 Кошелек: {wallet}\n\nВведите сумму для вывода (в USDT):', 'en': '🔁 WITHDRAWAL\n\n💰 Available balance: {balance:.2f} USDT\n💳 Wallet: {wallet}\n\nEnter withdrawal amount (USDT):'},
    'withdraw_not_enough': {'ru': '❌ Недостаточно средств для вывода\nПополните баланс в разделе "💰 Депозит"', 'en': '❌ Not enough funds for withdrawal\nPlease deposit first in "💰 Deposit"'},
    'withdraw_success': {'ru': '✅ Запрос на вывод {amount} USDT создан!\n\n⏳ Ожидайте обработки администратором\n📱 Вы получите уведомление после выполнения', 'en': '✅ Withdrawal request for {amount} USDT created!\n\n⏳ Await admin processing\n📱 You will be notified after completion'},
    'withdraw_error': {'ru': '❌ Ошибка при создании запроса на вывод', 'en': '❌ Error creating withdrawal request'},
    'help_sent': {'ru': '✅ <b>Запрос помощи отправлен!</b>\n\n📞 Наша команда поддержки свяжется с вами в ближайшее время.\n⏳ Обычно ответ приходит в течение 5-15 минут.\n\n💡 Пока вы ждёте, можете изучить разделы:\n— <b>Портфель</b>: ваш баланс и стратегии\n— <b>Стратегии</b>: описание инвестиционных возможностей\n— <b>Сигналы</b>: аналитические рекомендации', 'en': '✅ <b>Help request sent!</b>\n\n📞 Our support team will contact you soon.\n⏳ Usually you get a reply within 5-15 minutes.\n\n💡 While you wait, check out:\n— <b>Portfolio</b>: your balance and strategies\n— <b>Strategies</b>: investment opportunities\n— <b>Signals</b>: analytics recommendations'},
    'choose_action': {'ru': 'Выберите действие из главного меню:', 'en': 'Choose an action from the main menu:'},
    # ... (добавьте остальные шаблоны по мере необходимости)
    'change_wallet': {'ru': '💳 Изменить кошелек', 'en': '💳 Change wallet'},
    'wallet_prompt': {'ru': 'Введите новый адрес кошелька USDT (BEP-20):', 'en': 'Enter new USDT (BEP-20) wallet address:'},
    'wallet_success': {'ru': '✅ Кошелек успешно изменён!', 'en': '✅ Wallet updated successfully!'},
    'wallet_invalid': {'ru': '❌ Неверный формат адреса кошелька. Попробуйте снова.', 'en': '❌ Invalid wallet address format. Try again.'},
    'language_changed': {'ru': 'Язык успешно изменён!', 'en': 'Language changed successfully!'},
    'choose_language_full': {
        'ru': 'Какой язык вы хотите использовать?\nWhich language do you want to use?',
        'en': 'Which language do you want to use?\nКакой язык вы хотите использовать?'
    },
    'wallet_prompt_full': {
        'ru': 'Введите новый адрес USDT (BEP-20), на который вы хотите изменить:',
        'en': 'Enter the new USDT (BEP-20) address you want to set:'
    },
    'wallet_changed': {'ru': 'Кошелек успешно изменён!', 'en': 'Wallet updated successfully!'},
    'welcome': {
        'ru': '🏆 <b>HYDRA — закрытый инвестиционный клуб</b>\n\n🔒 <b>Эксклюзивное сообщество</b>\nМы объединяем опытных инвесторов и профессиональных трейдеров в закрытом пространстве для максимальной эффективности.\n\n📈 <b>5 лет в сфере криптовалют</b>\nНаша команда имеет многолетний опыт работы с цифровыми активами и глубокое понимание рыночных механизмов.\n\n🤖 <b>Автоматизированные стратегии</b>\nВсе операции проходят через смарт-контракты и проверенные алгоритмы, исключающие человеческий фактор.\n\n💎 <b>Только для избранных</b>\nДоступ к платформе предоставляется исключительно по приглашениям, что гарантирует качество сообщества.',
        'en': '🏆 <b>HYDRA — Private Investment Club</b>\n\n🔒 <b>Exclusive Community</b>\nWe unite experienced investors and professional traders in a closed space for maximum efficiency.\n\n📈 <b>5 years in crypto</b>\nOur team has years of experience with digital assets and deep market understanding.\n\n🤖 <b>Automated strategies</b>\nAll operations are run by smart contracts and proven algorithms, eliminating human error.\n\n💎 <b>Invitation only</b>\nAccess is granted by invite only, ensuring community quality.'
    },
})

def get_text(user_id, key):
    lang = db.get_language(user_id)
    return LANG_TEXTS.get(key, {}).get(lang, LANG_TEXTS.get(key, {}).get('ru', ''))

def get_language_keyboard():
    return ReplyKeyboardMarkup([
        [LANG_TEXTS['lang_ru']['ru'], LANG_TEXTS['lang_en']['en']]
    ], resize_keyboard=True, one_time_keyboard=True)

def get_main_dashboard_text():
    return (
        "🏆 <b>HYDRA — закрытый инвестиционный клуб</b>\n\n"
        "🔒 <b>Эксклюзивное сообщество</b>\n"
        "Мы объединяем опытных инвесторов и профессиональных трейдеров в закрытом пространстве для максимальной эффективности.\n\n"
        "📈 <b>5 лет в сфере криптовалют</b>\n"
        "Наша команда имеет многолетний опыт работы с цифровыми активами и глубокое понимание рыночных механизмов.\n\n"
        "🤖 <b>Автоматизированные стратегии</b>\n"
        "Все операции проходят через смарт-контракты и проверенные алгоритмы, исключающие человеческий фактор.\n\n"
        "💎 <b>Только для избранных</b>\n"
        "Доступ к платформе предоставляется исключительно по приглашениям, что гарантирует качество сообщества.\n\n"
        "<b>Выберите раздел:</b>"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_data = db.get_user(user_id)
    if not user_data:
        db.add_user(user_id, user.username or user.first_name)
    lang = db.get_language(user_id)
    # Всегда показываем приветствие
    await update.message.reply_text(get_text(user_id, 'welcome'), parse_mode=ParseMode.HTML)
    # Если язык не выбран — спрашиваем язык и блокируем дальнейшие действия
    if not lang or lang not in ('ru', 'en'):
        await update.message.reply_text(get_text(user_id, 'choose_language_full'), reply_markup=get_language_keyboard())
        context.user_data['awaiting_language'] = True
        return
    # Если пользователь не верифицирован — просим инвайт-код
    user_data = db.get_user(user_id)
    if not user_data or not user_data[4]:
        await update.message.reply_text(
            '🔒 Введите инвайт-код для доступа к закрытому клубу HYDRA:'
        )
        user_states[user_id] = UserState.WAITING_INVITE
        return
    # После выбора языка и верификации — главное меню
    await update.message.reply_text(get_text(user_id, 'main_menu'), reply_markup=get_main_menu(user_id))

async def handle_invite_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка инвайт-кода"""
    user = update.effective_user
    user_id = user.id
    invite_code = update.message.text.strip()
    if invite_code in INVITE_CODES:
        # Добавляем пользователя в базу
        db.add_user(user_id, user.username or user.first_name)
        # Атмосферное сообщение о комьюнити
        await update.message.reply_text(
            '🏆 Добро пожаловать в закрытое комьюнити HYDRA!\n\n'
            'Здесь вы получите доступ к эксклюзивным стратегиям, сигналам и поддержке профессионалов.\n\n'
            '🔗 Теперь привяжите ваш кошелек USDT (BEP-20) — введите адрес:'
        )
        user_states[user_id] = UserState.WAITING_WALLET
    else:
        await update.message.reply_text(
            "❌ Неверный инвайт-код\nПопробуйте еще раз или обратитесь к администратору."
        )

async def handle_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка адреса кошелька"""
    user = update.effective_user
    user_id = user.id
    wallet_address = update.message.text.strip()
    
    # Простая валидация адреса (можно улучшить)
    if len(wallet_address) == 42 and wallet_address.startswith('0x'):
        db.set_wallet_address(user_id, wallet_address)
        db.verify_user(user_id)
        await update.message.reply_text(
            "✅ Кошелек привязан!\n\n"
            "Добро пожаловать в личный кабинет HYDRA.\n"
            "Выберите действие:",
            reply_markup=get_main_menu()
        )
        if user_id in user_states:
            del user_states[user_id]
    else:
        await update.message.reply_text(
            "❌ Неверный формат адреса кошелька\n"
            "Введите корректный адрес USDT (BEP-20):"
        )

async def handle_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка суммы депозита"""
    user = update.effective_user
    user_id = user.id
    
    try:
        amount = float(update.message.text)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        context.user_data['deposit_amount'] = amount
        await update.message.reply_text(
            f"💳 <b>Адрес для пополнения (USDT BEP-20):</b>\n<code>{FAKE_DEPOSIT_ADDRESS}</code>\n\n"
            "После отправки USDT пришлите хэш транзакции (TxID) в ответ на это сообщение.",
            parse_mode=ParseMode.HTML,
            reply_markup=get_cancel_keyboard()
        )
        user_states[user_id] = UserState.WAITING_TX_HASH
    except Exception:
        await update.message.reply_text("❌ Введите корректную сумму (число)")

async def handle_tx_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка хэша транзакции"""
    user = update.effective_user
    user_id = user.id
    tx_hash = update.message.text.strip()
    amount = context.user_data.get('deposit_amount', 0)
    
    # Простая валидация хэша (TxID)
    if not (len(tx_hash) >= 20 and all(c.isalnum() for c in tx_hash)):
        await update.message.reply_text("❌ Введите корректный хэш транзакции (TxID)")
        return
    
    # Добавляем депозит в базу
    db.add_deposit(user_id, amount, tx_hash)
    
    # Отправляем уведомление админу
    admin_message = (
        f"💰 <b>НОВЫЙ ДЕПОЗИТ</b>\n\n"
        f"👤 Пользователь: @{user.username or user.first_name} (ID: {user_id})\n"
        f"💳 Кошелек: {db.get_user(user_id)[2]}\n"
        f"💰 Сумма: {amount} USDT\n"
        f"🔗 Хэш: {tx_hash}\n"
        f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_message,
        parse_mode=ParseMode.HTML,
        reply_markup=get_admin_keyboard("deposit", f"{user_id}_{amount}")
    )
    
    await update.message.reply_text(
        "✅ Депозит зарегистрирован!\n\n⏳ Ожидайте подтверждения от администратора.",
        reply_markup=get_main_menu()
    )
    
    # Очищаем состояние
    if user_id in user_states:
        del user_states[user_id]

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_data = db.get_user(user_id)
    if not user_data or not user_data[4]:
        text = get_text(user_id, 'access_denied')
        if update.message:
            await update.message.reply_text(text)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text)
        return
    balance = db.get_balance(user_id)
    total_yield = db.get_total_yield(user_id)
    strategies = db.get_user_strategies(user_id)
    portfolio_text = get_text(user_id, 'portfolio_header')
    portfolio_text += get_text(user_id, 'portfolio_balance').format(balance=balance, total_yield=total_yield, count=len(strategies))
    if strategies:
        strategies_list = ''
        for strategy_id, amount, start_date in strategies:
            strategy_name = STRATEGIES[strategy_id]['name']
            strategies_list += f'• {strategy_name}: активна с {start_date.split()[0]}\n'
        portfolio_text += get_text(user_id, 'portfolio_strategies_list').format(strategies=strategies_list)
        if update.message:
            await update.message.reply_text(
                portfolio_text,
                parse_mode=ParseMode.HTML
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                portfolio_text,
                parse_mode=ParseMode.HTML
            )
    else:
        if update.message:
            await update.message.reply_text(
                portfolio_text + get_text(user_id, 'portfolio_no_strategies'),
                parse_mode=ParseMode.HTML
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                portfolio_text + get_text(user_id, 'portfolio_no_strategies'),
                parse_mode=ParseMode.HTML
            )

async def strategies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_data = db.get_user(user_id)
    if not user_data or not user_data[4]:
        text = get_text(user_id, 'access_denied')
        if update.message:
            await update.message.reply_text(text)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text)
        return
    balance = db.get_balance(user_id)
    user_strategies = db.get_user_strategies(user_id)
    # Стратегия считается активной, если поле active отсутствует или равно True
    active_strategies = set()
    for s in user_strategies:
        # s: (strategy_id, amount, start_date, [active])
        if len(s) < 4 or s[3]:
            active_strategies.add(s[0])
    strategies_text = (
        f"📈 СТРАТЕГИИ HYDRA\n\n"
        f"💰 Ваш баланс: {balance:.2f} USDT\n\n"
        f"Выберите стратегию для подробностей или активации:\n\n"
    )
    keyboard = []
    for strategy_id, strategy in STRATEGIES.items():
        if strategy_id in active_strategies:
            status = "🟢 Активна"
        elif balance >= strategy['min_deposit']:
            status = "✅ Доступна"
        else:
            status = "❌ Недоступна"
        strategies_text += (
            f"🧠 {strategy['name']}\n"
            f"📊 Доходность: до {strategy['max_yield']}%\n"
            f"💰 Мин. депозит: {strategy['min_deposit']} USDT\n"
            f"📝 {strategy['description']}\n"
            f"Статус: {status}\n\n"
        )
        keyboard.append([InlineKeyboardButton(
            f"{strategy['name']} — Подробнее", callback_data=f"strategy_{strategy_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_strategies")])
    if update.message:
        await update.message.reply_text(
            strategies_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            strategies_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сигналы от аналитиков"""
    user = update.effective_user
    user_id = user.id
    
    user_data = db.get_user(user_id)
    if not user_data or not user_data[4]:  # not verified
        await update.message.reply_text("❌ Доступ запрещен. Сначала пополните баланс.")
        return
    
    # Проверяем, активирована ли стратегия сигналов
    user_strategies = db.get_user_strategies(user_id)
    has_signals = any(strategy[0] == 'analyst_signals' for strategy in user_strategies)
    
    if has_signals:
        # Генерируем актуальные сигналы
        signals = signals_simulator.generate_daily_signals(5)
        market_overview = signals_simulator.get_market_overview()
        risk_tips = signals_simulator.get_risk_management_tips()
        
        signals_text = f"📡 СИГНАЛЫ ОТ КОМАНДЫ АНАЛИТИКОВ\n\n{market_overview}\n\n🎯 ПОСЛЕДНИЕ СИГНАЛЫ:\n\n"
        
        for i, signal in enumerate(signals, 1):
            emoji = "🟢" if signal['type'] == 'LONG' else "🔴"
            signals_text += (
                f"{i}. {emoji} {signal['pair']} - {signal['type']}\n"
                f"💰 Цена входа: ${signal['entry_price']}\n"
                f"🎯 Цель: ${signal['target_price']}\n"
                f"🛑 Стоп-лосс: ${signal['stop_loss']}\n"
                f"⏰ Время: {signal['time']}\n"
                f"👨‍💼 Аналитик: {signal['analyst']}\n"
                f"📊 Уверенность: {signal['confidence']}\n"
                f"⚖️ R/R: 1:{signal['risk_reward']}\n"
                f"📝 {signal['description']}\n\n"
            )
        
        signals_text += f"\n{risk_tips}"
    else:
        signals_text = (
            "📡 СИГНАЛЫ ОТ КОМАНДЫ АНАЛИТИКОВ\n\n"
            "🔒 Доступ закрыт\n\n"
            "💰 Для получения сигналов активируйте стратегию:\n"
            "📊 Сигналы от команды аналитиков\n"
            "💵 Минимальный депозит: 500 USDT\n"
            "📈 Доходность: до 10%\n\n"
            "Перейдите в раздел '📈 Стратегии' для активации."
        )
    
    await update.message.reply_text(signals_text)

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_data = db.get_user(user_id)
    if not user_data or not user_data[4]:
        await update.message.reply_text("❌ Доступ запрещен. Сначала пополните баланс.")
        return
    await update.message.reply_text(
        get_text(user_id, 'deposit_prompt'),
        reply_markup=get_cancel_keyboard()
    )
    user_states[user_id] = UserState.WAITING_DEPOSIT_AMOUNT

async def withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывод средств"""
    user = update.effective_user
    user_id = user.id
    
    user_data = db.get_user(user_id)
    if not user_data or not user_data[4]:  # not verified
        await update.message.reply_text("❌ Доступ запрещен. Сначала пополните баланс.")
        return
    
    balance = db.get_balance(user_id)
    wallet_address = user_data[2]
    
    if balance <= 0:
        await update.message.reply_text(
            get_text(user_id, 'withdraw_not_enough')
        )
        return
    
    withdrawal_text = get_text(user_id, 'withdraw_prompt').format(balance=balance, wallet=wallet_address)
    
    user_states[user_id] = UserState.WAITING_WITHDRAWAL_AMOUNT
    await update.message.reply_text(
        withdrawal_text,
        reply_markup=get_cancel_keyboard()
    )

async def handle_withdrawal_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка суммы вывода"""
    user = update.effective_user
    user_id = user.id
    
    try:
        amount = float(update.message.text)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        balance = db.get_balance(user_id)
        if amount > balance:
            await update.message.reply_text(
                f"❌ Недостаточно средств\n"
                f"Доступно: {balance:.2f} USDT"
            )
            return
        
        # Создаем запрос на вывод
        if db.request_withdrawal(user_id, amount):
            # Отправляем уведомление админу
            admin_message = (
                f"🔁 ЗАПРОС НА ВЫВОД\n\n"
                f"👤 Пользователь: @{user.username or user.first_name} (ID: {user_id})\n"
                f"💳 Кошелек: {db.get_user(user_id)[2]}\n"
                f"💰 Сумма: {amount} USDT\n"
                f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_message,
                reply_markup=get_admin_keyboard("withdrawal", f"{user_id}_{amount}")
            )
            
            await update.message.reply_text(
                get_text(user_id, 'withdraw_success').format(amount=amount)
            )
        else:
            await update.message.reply_text(get_text(user_id, 'withdraw_error'))
        
        # Очищаем состояние
        if user_id in user_states:
            del user_states[user_id]
            
    except ValueError:
        await update.message.reply_text(
            "❌ Неверная сумма\n"
            "Введите корректное число:"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_data = db.get_user(user_id)
    if not user_data or not user_data[4]:
        await update.message.reply_text("❌ Доступ запрещен. Сначала пополните баланс.")
        return
    # Отправляем запрос в админ-чат
    admin_message = (
        f"🆘 <b>ЗАПРОС ПОМОЩИ</b>\n\n"
        f"👤 Пользователь: @{user.username or user.first_name} (ID: {user_id})\n"
        f"💳 Кошелек: {user_data[2]}\n"
        f"💰 Баланс: {db.get_balance(user_id):.2f} USDT\n"
        f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"<b>Пользователь запросил помощь.</b>\n"
        f"Ответьте ему напрямую или используйте команды админа."
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_message,
        parse_mode=ParseMode.HTML
    )
    # Уведомляем пользователя
    user_message = get_text(user_id, 'help_sent')
    await update.message.reply_text(user_message, parse_mode=ParseMode.HTML)

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_data = db.get_user(user_id)
    if not user_data or not user_data[4]:
        await update.message.reply_text(get_text(user_id, 'access_denied'))
        return
    wallet_address = user_data[2]
    join_date = user_data[5]
    lang = db.get_language(user_id)
    settings_text = (
        f"⚙️ <b>{'НАСТРОЙКИ HYDRA' if lang == 'ru' else 'HYDRA SETTINGS'}</b>\n\n"
        f"👤 {'Пользователь' if lang == 'ru' else 'User'}: {user.first_name}\n"
        f"🆔 ID: {user_id}\n"
        f"💳 {'Кошелек' if lang == 'ru' else 'Wallet'}: <code>{wallet_address}</code>\n"
        f"📅 {'Дата регистрации' if lang == 'ru' else 'Join date'}: {join_date}\n\n"
        f"🔐 {'Статус' if lang == 'ru' else 'Status'}: {'Подтвержден' if lang == 'ru' else 'Verified'}\n"
        f"✅ {'Доступ' if lang == 'ru' else 'Access'}: {'Активен' if lang == 'ru' else 'Active'}\n\n"
    )
    keyboard = ReplyKeyboardMarkup([
        [get_text(user_id, 'change_language'), get_text(user_id, 'change_wallet')],
        ["🔙 Назад" if lang == 'ru' else '🔙 Back']
    ], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(settings_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

async def show_strategy_details(update, context, strategy_id):
    user = update.effective_user
    user_id = user.id
    strategy = STRATEGIES[strategy_id]
    balance = db.get_balance(user_id)
    user_strategies = db.get_user_strategies(user_id)
    # Стратегия активна, если есть запись с active=1 (или без поля active)
    is_active = False
    for s in user_strategies:
        if s[0] == strategy_id:
            if len(s) < 4 or s[3]:
                is_active = True
    can_activate = (not is_active) and (balance >= strategy['min_deposit'])
    example = {
        'ai_arbitrage': 'Пример: Система автоматически находит разницу цен на биржах и совершает сделки без вашего участия.',
        'liquidity_pools': 'Пример: Вы предоставляете ликвидность и получаете процент от комиссий пула.',
        'analyst_signals': 'Пример: Получаете сигналы от команды аналитиков и следуете их рекомендациям.'
    }[strategy_id]
    text = (
        f"🧠 <b>{strategy['name']}</b>\n\n"
        f"<b>Описание:</b> {strategy['description']}\n\n"
        f"<b>Как работает:</b> {example}\n\n"
        f"<b>Мин. депозит:</b> {strategy['min_deposit']} USDT\n"
        f"<b>Доходность:</b> до {strategy['max_yield']}%\n"
        f"<b>Ваш баланс:</b> {balance:.2f} USDT\n\n"
    )
    if is_active:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отключить стратегию", callback_data=f"deactivate_{strategy_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_strategies")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ])
        text += "Стратегия уже активирована."
    elif can_activate:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Активировать", callback_data=f"activate_{strategy_id}_{strategy['min_deposit']}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_strategies")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_strategies")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ])
        text += f"Недостаточно средств для активации. Минимальный баланс: {strategy['min_deposit']} USDT."
    await update.callback_query.edit_message_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    deposits = db.get_deposits(user_id)
    activations = db.get_strategy_activations(user_id)
    yields = db.get_yields(user_id)
    withdrawals = db.get_withdrawals(user_id)
    trades = db.get_trades(user_id)
    text = '<b>📜 История операций</b>\n\n'
    if deposits:
        text += '<b>Депозиты:</b>\n'
        for a, h, s, t in deposits[:5]:
            text += f'• {a} USDT | {s} | {t.split()[0]}\n'
    if activations:
        text += '\n<b>Активации стратегий:</b>\n'
        for sid, a, d in activations[:5]:
            text += f'• {STRATEGIES[sid]["name"]}: {a} USDT | {d.split()[0]}\n'
    if trades:
        text += '\n<b>Сделки по стратегиям:</b>\n'
        for sid, open_t, close_t, a, profit, percent, status in trades[:5]:
            text += f'• <b>{STRATEGIES[sid]["name"]}</b> | {open_t.split()[0]} - {close_t.split()[0]}\n   Открытие: {a} USDT\n   Результат: {"+" if profit>=0 else "-"}{abs(percent):.2f}% ({"+" if profit>=0 else "-"}{abs(profit):.2f} USDT)\n   Статус: {status.capitalize()}\n\n'
    if yields:
        text += '\n<b>Доходность:</b>\n'
        for sid, a, d in yields[:5]:
            text += f'• {STRATEGIES[sid]["name"]}: +{a:.2f} USDT | {d}\n'
    if withdrawals:
        text += '\n<b>Выводы:</b>\n'
        for a, s, t in withdrawals[:5]:
            text += f'• {a} USDT | {s} | {t.split()[0]}\n'
    if text.strip() == '<b>📜 История операций</b>':
        text += '\nНет операций.'
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=get_history_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback запросов"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    user_id = user.id
    
    if data.startswith("strategy_"):
        strategy_id = data.replace("strategy_", "")
        await show_strategy_details(update, context, strategy_id)
    
    elif data.startswith("activate_"):
        parts = data.split("_")
        strategy_id = f"{parts[1]}_{parts[2]}"
        amount = float(parts[3])
        # Проверяем, не активирована ли уже эта стратегия
        user_strategies = db.get_user_strategies(user_id)
        is_active = False
        for s in user_strategies:
            if s[0] == strategy_id:
                if len(s) < 4 or s[3]:
                    is_active = True
        balance = db.get_balance(user_id)
        min_deposit = STRATEGIES[strategy_id]['min_deposit']
        if is_active:
            await query.edit_message_text(
                "❌ Эта стратегия уже активирована!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_strategies")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
            return
        if balance >= min_deposit:
            db.activate_strategy(user_id, strategy_id, min_deposit)
            await query.edit_message_text(
                f"✅ Стратегия активирована!\n\n"
                f"🧠 {STRATEGIES[strategy_id]['name']}\n"
                f"💰 Порог активации: {min_deposit} USDT\n"
                f"📊 Ожидаемая доходность: до {STRATEGIES[strategy_id]['max_yield']}%\n\n"
                f"📈 Доходность начисляется ежедневно\n"
                f"📱 Следите за обновлениями в разделе '🧠 Портфель'",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_strategies")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
        else:
            await query.edit_message_text(
                f"❌ Недостаточно средств для активации этой стратегии.\n"
                f"Минимальный баланс: {min_deposit} USDT",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_strategies")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
        return
    
    elif data == "back_to_strategies":
        await portfolio(update, context)
    
    elif data == "back_to_main":
        await query.edit_message_text(
            get_main_dashboard_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu()
        )
    
    elif data == "cancel":
        if user_id in user_states:
            del user_states[user_id]
        await query.edit_message_text(
            "❌ Операция отменена",
            reply_markup=None
        )

    elif data.startswith("deactivate_"):
        strategy_id = data.replace("deactivate_", "")
        # Деактивируем стратегию
        conn = db.db_path
        import sqlite3
        con = sqlite3.connect(conn)
        cur = con.cursor()
        cur.execute('UPDATE user_strategies SET active = 0 WHERE user_id = ? AND strategy_id = ?', (user_id, strategy_id))
        con.commit()
        con.close()
        await query.edit_message_text(
            f"❌ Стратегия {STRATEGIES[strategy_id]['name']} отключена.",
            reply_markup=get_back_keyboard("back_to_portfolio")
        )
        return
    elif data == "back_to_portfolio":
        await portfolio(update, context)
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text
    user_data = db.get_user(user_id)
    # Блокирующая обработка смены языка/кошелька
    if text == get_text(user_id, 'change_language'):
        context.user_data['awaiting_language'] = True
        context.user_data['awaiting_wallet'] = False
        await update.message.reply_text(get_text(user_id, 'choose_language_full'), reply_markup=get_language_keyboard())
        return
    if text == get_text(user_id, 'change_wallet'):
        context.user_data['awaiting_wallet'] = True
        context.user_data['awaiting_language'] = False
        await update.message.reply_text(get_text(user_id, 'wallet_prompt_full'))
        return
    if context.user_data.get('awaiting_wallet') or context.user_data.get('awaiting_language'):
        await handle_settings_input(update, context)
        return
    # Если это админ-чат и есть активный state — не обрабатывать здесь
    if str(update.effective_chat.id) == str(ADMIN_CHAT_ID):
        admin_id = user_id
        if admin_states.get(admin_id, {}).get("state"):
            return
    
    # Проверяем состояние пользователя
    if user_id in user_states:
        state = user_states[user_id]
        
        if state == UserState.WAITING_INVITE:
            await handle_invite_code(update, context)
        elif state == UserState.WAITING_WALLET:
            await handle_wallet_address(update, context)
        elif state == UserState.WAITING_DEPOSIT_AMOUNT:
            await handle_deposit_amount(update, context)
        elif state == UserState.WAITING_TX_HASH:
            await handle_tx_hash(update, context)
        elif state == UserState.WAITING_WITHDRAWAL_AMOUNT:
            await handle_withdrawal_amount(update, context)
        return
    
    # Если пользователь не верифицирован — только разрешённые команды
    if not user_data or not user_data[4]:
        if text in ["💰 Депозит", "⚙️ Настройки", "ℹ️ Помощь"]:
            if text == "💰 Депозит":
                await deposit(update, context)
            elif text == "⚙️ Настройки":
                await settings(update, context)
            elif text == "ℹ️ Помощь":
                await help_command(update, context)
        else:
            await update.message.reply_text(
                "Для доступа к функциям HYDRA сначала пополните баланс через раздел '💰 Депозит'.",
                reply_markup=get_limited_menu()
            )
        return
    
    # Обработка главного меню
    if text == "🧠 Портфель":
        await portfolio(update, context)
    elif text == "📈 Стратегии":
        await strategies(update, context)
    elif text == "📡 Сигналы":
        await signals(update, context)
    elif text == "💰 Депозит":
        await deposit(update, context)
    elif text == "🔁 Вывод":
        await withdrawal(update, context)
    elif text == "⚙️ Настройки":
        await settings(update, context)
    elif text == "📜 История":
        await history(update, context)
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
    elif text == "/help":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            get_text(user_id, 'choose_action'),
            reply_markup=get_main_menu()
        )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback запросов админа"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("confirm_deposit_"):
        # Подтверждение депозита
        parts = data.split("_")
        user_id = int(parts[2])
        amount = float(parts[3])
        
        db.confirm_deposit(user_id, amount)
        # Верифицируем пользователя после первого депозита
        db.verify_user(user_id)
        
        # Уведомляем пользователя
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Депозит подтвержден!\n\n💰 Начислено: {amount} USDT\n\n🔐 Доступ к терминалу HYDRA открыт!\n\nГлавное меню:",
            reply_markup=get_main_menu()
        )
        
        await query.edit_message_text(
            f"✅ Депозит {amount} USDT подтвержден для пользователя {user_id}",
            reply_markup=None
        )
    
    elif data.startswith("confirm_withdrawal_"):
        # Подтверждение вывода
        parts = data.split("_")
        user_id = int(parts[2])
        amount = float(parts[3])
        
        # Здесь должна быть логика реального вывода
        # Пока просто подтверждаем
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Вывод выполнен!\n\n💰 Выведено: {amount} USDT\n\n🔗 Транзакция: 0x1234567890abcdef...\n\nСредства поступят в течение 5-10 минут."
        )
        
        await query.edit_message_text(
            f"✅ Вывод {amount} USDT выполнен для пользователя {user_id}",
            reply_markup=None
        )
    
    elif data.startswith("add_yield_"):
        # Начисление доходности
        user_id = int(data.split("_")[2])
        from datetime import datetime
        today = datetime.now().date().isoformat()
        # Симулируем начисление доходности
        strategies = db.get_user_strategies(user_id)
        total_yield = 0
        yield_reports = []
        for strategy_id, amount, start_date in strategies:
            strategy = STRATEGIES[strategy_id]
            daily_yield = amount * (strategy['max_yield'] / 100) / 30  # Примерно 1/30 от годовой доходности
            db.add_yield(user_id, strategy_id, daily_yield, today)
            # Получаем только что добавленную запись доходности
            yields = db.get_yields(user_id)
            # Берём первую подходящую за сегодня и по стратегии
            for sid, yld, d in yields:
                if sid == strategy_id and d == today:
                    yield_reports.append((strategy_id, yld, d))
                    total_yield += yld
                    break
        # Атмосферное уведомление пользователю
        for strategy_id, yld, d in yield_reports:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"💸 HYDRA: Прибыль зачислена!\n"
                    f"Стратегия: {STRATEGIES[strategy_id]['name']}\n"
                    f"+{yld:.2f} USDT на ваш баланс.\n"
                    f"Дата: {d}\n\n"
                    f"🚀 HYDRA работает — ваш капитал растёт. Следите за портфелем!"
                )
            )
        await query.edit_message_text(
            f"✅ Доходность {total_yield:.2f} USDT начислена пользователю {user_id}"
        )

async def daily_yield_task(context: ContextTypes.DEFAULT_TYPE):
    """Ежедневное начисление доходности"""
    # Получаем всех пользователей с активными стратегиями
    # Здесь должна быть логика для получения всех пользователей
    # Пока просто логируем
    logger.info("Daily yield task executed")

async def simulate_trades_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_strategies = db.get_user_strategies(user_id)
    if not user_strategies:
        await update.message.reply_text("У вас нет активных стратегий для симуляции сделок.")
        return
    for sid, amount, _ in user_strategies:
        await simulate_trade(user_id, sid, amount)
    await update.message.reply_text("✅ Сделки по стратегиям сгенерированы! Проверьте историю.")

# --- Имитация сделок по стратегиям (должна быть выше admin_menu_callback) ---
async def simulate_trade(user_id, strategy_id, amount):
    from datetime import datetime, timedelta
    open_time = datetime.now() - timedelta(hours=2)
    close_time = datetime.now()
    import random
    percent = round(random.uniform(1, 5), 2)
    profit = round(amount * percent / 100, 2)
    db.add_trade(user_id, strategy_id, open_time, close_time, amount, profit, percent, "закрыта")
    db.add_yield(user_id, strategy_id, profit, close_time.date())

# --- Админ-панель ---
admin_states = {}

async def hadm1N_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        await update.message.reply_text("⛔️ Только для админ-чата.")
        return
    await update.message.reply_text(
        "<b>🛡 Админ-панель HYDRA</b>\n\nВыберите раздел:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_admin_main_menu()
    )

async def admin_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if str(query.message.chat.id) != str(ADMIN_CHAT_ID):
        await query.answer("⛔️ Только для админ-чата.", show_alert=True)
        return
    data = query.data
    admin_id = query.from_user.id
    # Главное меню
    if data == "admin_users":
        users = db.get_users()
        text = "<b>👤 Список пользователей (последние 10):</b>\n\n"
        for u in users:
            text += f"ID: <code>{u[0]}</code> | @{u[1] or '-'} | Баланс: {u[2]:.2f} | {'✅' if u[3] else '🚫'}\n"
        text += "\nВыберите действие ниже или введите user_id для просмотра профиля."
        admin_states[admin_id] = {"state": "await_user_id"}
        await context.bot.send_message(chat_id=query.message.chat.id, text="🕵️ Введите user_id пользователя, чью тайну хотите раскрыть! HYDRA покажет всё, что знает…", parse_mode=ParseMode.HTML, reply_markup=None)
        return
    elif data == "admin_user_balance":
        admin_states[admin_id] = {"state": "await_user_id_balance"}
        await context.bot.send_message(chat_id=query.message.chat.id, text="💰 Введите user_id — сейчас узнаем, сколько USDT скрыто на его счету!", reply_markup=None)
        return
    elif data == "admin_user_history":
        admin_states[admin_id] = {"state": "await_user_id_history"}
        await context.bot.send_message(chat_id=query.message.chat.id, text="📜 Введите user_id, чтобы увидеть всю историю его приключений в HYDRA.", reply_markup=None)
        return
    elif data == "admin_user_block":
        admin_states[admin_id] = {"state": "await_user_id_block"}
        await context.bot.send_message(chat_id=query.message.chat.id, text="🚫 Введите user_id для блокировки. HYDRA не прощает ошибок…", reply_markup=None)
        return
    elif data == "admin_user_unblock":
        admin_states[admin_id] = {"state": "await_user_id_unblock"}
        await context.bot.send_message(chat_id=query.message.chat.id, text="✅ Введите user_id для разблокировки. Дадим ещё один шанс?", reply_markup=None)
        return
    elif data == "admin_user_message":
        admin_states[admin_id] = {"state": "await_user_id_message"}
        await context.bot.send_message(chat_id=query.message.chat.id, text="✉️ Введите user_id и текст через пробел — ваше послание будет доставлено лично!", reply_markup=None)
        return
    elif data == "admin_mass":
        await context.bot.send_message(chat_id=query.message.chat.id, text=
            "📢 <b>Массовые действия</b>\n\nВыберите действие:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_admin_mass_menu()
        )
        return
    elif data == "admin_mass_yield":
        from datetime import datetime
        today = datetime.now().date().isoformat()
        users = db.get_users(limit=1000)
        for u in users:
            user_id = u[0]
            user_strategies = db.get_user_strategies(user_id)
            for sid, amount, _ in user_strategies:
                strategy = STRATEGIES[sid]
                daily_yield = amount * (strategy['max_yield'] / 100) / 30
                db.add_yield(user_id, sid, daily_yield, today)
                # Получаем только что добавленную запись доходности
                yields = db.get_yields(user_id)
                for s2, yld, d in yields:
                    if s2 == sid and d == today:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=(
                                f"💸 HYDRA: Прибыль зачислена!\n"
                                f"Стратегия: {strategy['name']}\n"
                                f"+{yld:.2f} USDT на ваш баланс.\n"
                                f"Дата: {d}\n\n"
                                f"🚀 HYDRA работает — ваш капитал растёт. Следите за портфелем!"
                            )
                        )
                        break
        await context.bot.send_message(chat_id=query.message.chat.id, text="✅ Доходность начислена всем пользователям!", reply_markup=get_admin_mass_menu())
        return
    elif data == "admin_mass_broadcast":
        admin_states[admin_id] = {"state": "await_broadcast_text"}
        await context.bot.send_message(chat_id=query.message.chat.id, text="🚀 Введите текст для рассылки всем пользователям. Пусть HYDRA загудит от новостей!", reply_markup=None)
        return
    elif data == "admin_mass_users":
        users = db.get_users(limit=20)
        text = "<b>👥 Все пользователи (последние 20):</b>\n\n"
        for u in users:
            text += f"ID: <code>{u[0]}</code> | @{u[1] or '-'} | Баланс: {u[2]:.2f} | {'✅' if u[3] else '🚫'}\n"
        await context.bot.send_message(chat_id=query.message.chat.id, text=text, parse_mode=ParseMode.HTML, reply_markup=get_admin_mass_menu())
        return
    elif data == "admin_events":
        await context.bot.send_message(chat_id=query.message.chat.id, text=
            "🕒 <b>Последние события</b>\n\nВыберите действие:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_admin_events_menu()
        )
        return
    elif data == "admin_events_deposits":
        deposits = db.get_last_deposits()
        text = "<b>💸 Последние депозиты:</b>\n\n"
        for d in deposits:
            text += f"ID: {d[0]} | User: <code>{d[1]}</code> | {d[2]} USDT | {d[3]} | {d[4].split()[0]}\n"
        await context.bot.send_message(chat_id=query.message.chat.id, text=text, parse_mode=ParseMode.HTML, reply_markup=get_admin_events_menu())
        return
    elif data == "admin_events_withdrawals":
        withdrawals = db.get_last_withdrawals()
        text = "<b>🔁 Последние выводы:</b>\n\n"
        for w in withdrawals:
            text += f"ID: {w[0]} | User: <code>{w[1]}</code> | {w[2]} USDT | {w[3]} | {w[4].split()[0]}\n"
        await context.bot.send_message(chat_id=query.message.chat.id, text=text, parse_mode=ParseMode.HTML, reply_markup=get_admin_events_menu())
        return
    elif data == "admin_events_help":
        await context.bot.send_message(chat_id=query.message.chat.id, text="🆘 Последние запросы помощи... (реализуйте при необходимости)", reply_markup=get_admin_events_menu())
        return
    elif data == "admin_back_main":
        await context.bot.send_message(chat_id=query.message.chat.id, text=
            "<b>🛡 Админ-панель HYDRA</b>\n\nВыберите раздел:",
            parse_mode=ParseMode.HTML,
            reply_markup=get_admin_main_menu()
        )
        return
    elif data == "admin_mass_deposit_notify":
        await context.bot.send_message(chat_id=query.message.chat.id, text="Выберите стратегию для оповещения о старте:", reply_markup=get_admin_mass_notify_menu())
        return
    elif data.startswith("admin_mass_notify_"):
        strategy_id = data.replace("admin_mass_notify_", "")
        users = db.get_users(limit=1000)
        count = 0
        # Атмосферные тексты для каждой стратегии
        strategy_notify_texts = {
            'ai_arbitrage': "🚀 HYDRA: AI-арбитраж активирован! Алгоритмы уже ищут лучшие сделки. Следите за прибылью в портфеле!",
            'liquidity_pools': "💧 HYDRA: Пулы ликвидности запущены! Ваш капитал работает на вас 24/7. Прибыль не заставит себя ждать!",
            'analyst_signals': "📡 HYDRA: Сигналы от команды аналитиков теперь доступны! Не пропустите новые идеи для роста и свежие инсайды!"
        }
        notify_text = strategy_notify_texts.get(strategy_id, f"HYDRA: Ваша стратегия {STRATEGIES[strategy_id]['name']} начала работу! Ожидайте начисления прибыли.")
        for u in users:
            user_id = u[0]
            user_strategies = db.get_user_strategies(user_id)
            if any(s[0] == strategy_id and (len(s) < 4 or s[3]) for s in user_strategies):
                try:
                    await context.bot.send_message(chat_id=user_id, text=notify_text)
                    count += 1
                except:
                    pass
        await context.bot.send_message(chat_id=query.message.chat.id, text=f"Оповещение о старте стратегии '{STRATEGIES[strategy_id]['name']}' отправлено {count} пользователям.", reply_markup=get_admin_mass_menu())
        return
    await query.answer()

# Обработка текстовых ответов для админ-панели
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    admin_id = update.effective_user.id
    state = admin_states.get(admin_id, {}).get("state")
    if not state:
        return
    # reply больше не обязателен — главное, что есть state
    text = update.message.text.strip()
    if state == "await_user_id":
        if text.isdigit():
            user = db.get_user_by_id(int(text))
            if user:
                msg = f"🔍 Досье раскрыто! Вот всё, что HYDRA знает о пользователе...\n\n<b>Профиль пользователя {user[0]}</b>\n@{user[1] or '-'}\nБаланс: {user[2]:.2f} USDT\nСтатус: {'✅' if user[3] else '🚫'}"
                await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=get_admin_users_menu())
                admin_states[admin_id] = {}  # Сброс только после успеха
            else:
                await update.message.reply_text("❌ Пользователь не найден. HYDRA не смогла найти следов.\nПопробуйте ещё раз!", reply_markup=None)
        else:
            await update.message.reply_text("Введите корректный user_id (только цифры).", reply_markup=None)
        return
    elif state == "await_user_id_balance":
        if text.isdigit():
            user = db.get_user_by_id(int(text))
            if user:
                await update.message.reply_text(f"💸 Баланс пользователя: {user[2]:.2f} USDT. HYDRA следит за каждым центом!", reply_markup=get_admin_users_menu())
                admin_states[admin_id] = {}
            else:
                await update.message.reply_text("❌ Пользователь не найден. HYDRA не смогла найти следов.\nПопробуйте ещё раз!", reply_markup=None)
        else:
            await update.message.reply_text("Введите корректный user_id (только цифры).", reply_markup=None)
        return
    elif state == "await_user_id_history":
        if text.isdigit():
            user_id = int(text)
            deposits = db.get_deposits(user_id)
            activations = db.get_strategy_activations(user_id)
            yields = db.get_yields(user_id)
            withdrawals = db.get_withdrawals(user_id)
            trades = db.get_trades(user_id)
            msg = f'<b>📜 Вот его путь в HYDRA. Кто знает, что ждёт впереди…</b>\n\n'
            if deposits:
                msg += '<b>Депозиты:</b>\n'
                for a, h, s, t in deposits[:3]:
                    msg += f'• {a} USDT | {s} | {t.split()[0]}\n'
            if activations:
                msg += '\n<b>Активации стратегий:</b>\n'
                for sid, a, d in activations[:3]:
                    msg += f'• {STRATEGIES[sid]["name"]}: {a} USDT | {d.split()[0]}\n'
            if trades:
                msg += '\n<b>Сделки по стратегиям:</b>\n'
                for sid, open_t, close_t, a, profit, percent, status in trades[:3]:
                    msg += f'• <b>{STRATEGIES[sid]["name"]}</b> | {open_t.split()[0]} - {close_t.split()[0]}\n   Открытие: {a} USDT\n   Результат: {"+" if profit>=0 else "-"}{abs(percent):.2f}% ({"+" if profit>=0 else "-"}{abs(profit):.2f} USDT)\n   Статус: {status.capitalize()}\n\n'
            if yields:
                msg += '\n<b>Доходность:</b>\n'
                for sid, a, d in yields[:3]:
                    msg += f'• {STRATEGIES[sid]["name"]}: +{a:.2f} USDT | {d}\n'
            if withdrawals:
                msg += '\n<b>Выводы:</b>\n'
                for a, s, t in withdrawals[:3]:
                    msg += f'• {a} USDT | {s} | {t.split()[0]}\n'
            if msg.strip() == f'<b>📜 Вот его путь в HYDRA. Кто знает, что ждёт впереди…</b>':
                msg += '\nНет операций.'
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=get_admin_users_menu())
            admin_states[admin_id] = {}
        else:
            await update.message.reply_text("Введите корректный user_id (только цифры).", reply_markup=None)
        return
    elif state == "await_user_id_block":
        if text.isdigit():
            user_id = int(text)
            conn = db.db_path
            import sqlite3
            con = sqlite3.connect(conn)
            cur = con.cursor()
            cur.execute('UPDATE users SET is_verified = 0 WHERE user_id = ?', (user_id,))
            con.commit()
            con.close()
            await update.message.reply_text(f"🚫 Пользователь {user_id} заблокирован. HYDRA закрыла доступ.", reply_markup=get_admin_users_menu())
            admin_states[admin_id] = {}
        else:
            await update.message.reply_text("Введите корректный user_id (только цифры).", reply_markup=None)
        return
    elif state == "await_user_id_unblock":
        if text.isdigit():
            user_id = int(text)
            db.verify_user(user_id)
            await update.message.reply_text(f"✅ Пользователь {user_id} снова в игре. HYDRA даёт второй шанс!", reply_markup=get_admin_users_menu())
            admin_states[admin_id] = {}
        else:
            await update.message.reply_text("Введите корректный user_id (только цифры).", reply_markup=None)
        return
    elif state == "await_user_id_message":
        parts = text.split(maxsplit=1)
        if len(parts) == 2 and parts[0].isdigit():
            user_id = int(parts[0])
            msg = parts[1]
            try:
                await context.bot.send_message(chat_id=user_id, text=msg)
                await update.message.reply_text(f"✉️ Сообщение отправлено! HYDRA передала ваш сигнал.", reply_markup=get_admin_users_menu())
                admin_states[admin_id] = {}
            except Exception as e:
                await update.message.reply_text(f"Ошибка отправки: {e}", reply_markup=None)
        else:
            await update.message.reply_text("Введите user_id и текст сообщения через пробел. Пример: 123456789 Привет!", reply_markup=None)
        return
    elif state == "await_broadcast_text":
        if text.strip():
            users = db.get_users(limit=1000)
            count = 0
            for u in users:
                try:
                    await context.bot.send_message(chat_id=u[0], text=text)
                    count += 1
                except:
                    pass
            await update.message.reply_text(f"📢 Рассылка завершена! HYDRA донесла новость до {count} пользователям.", reply_markup=get_admin_mass_menu())
            admin_states[admin_id] = {}
        else:
            await update.message.reply_text("Введите текст для рассылки (сообщение не может быть пустым).", reply_markup=None)
        return

async def handle_settings_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text
    lang = db.get_language(user_id)
    # Назад — главное меню
    if text in ["🔙 Назад", "🔙 Back"]:
        await update.message.reply_text(get_text(user_id, 'main_menu'), reply_markup=get_main_menu(user_id))
        context.user_data['awaiting_language'] = False
        context.user_data['awaiting_wallet'] = False
        return
    # Смена языка
    if text == get_text(user_id, 'change_language'):
        await update.message.reply_text(
            get_text(user_id, 'choose_language_full'),
            reply_markup=get_language_keyboard()
        )
        context.user_data['awaiting_language'] = True
        return
    # Смена кошелька
    if text == get_text(user_id, 'change_wallet'):
        await update.message.reply_text(get_text(user_id, 'wallet_prompt_full'))
        context.user_data['awaiting_wallet'] = True
        return
    # Обработка выбора языка
    if context.user_data.get('awaiting_language'):
        if text in [LANG_TEXTS['lang_ru']['ru'], LANG_TEXTS['lang_ru']['en']]:
            db.set_language(user_id, 'ru')
            await update.message.reply_text(get_text(user_id, 'language_changed'))
            context.user_data['awaiting_language'] = False
            await settings(update, context)
            return
        elif text in [LANG_TEXTS['lang_en']['ru'], LANG_TEXTS['lang_en']['en']]:
            db.set_language(user_id, 'en')
            await update.message.reply_text(get_text(user_id, 'language_changed'))
            context.user_data['awaiting_language'] = False
            await settings(update, context)
            return
        else:
            await update.message.reply_text(
                get_text(user_id, 'choose_language_full'),
                reply_markup=get_language_keyboard()
            )
            return
    # Обработка смены кошелька
    if context.user_data.get('awaiting_wallet'):
        wallet_address = text.strip()
        if len(wallet_address) == 42 and wallet_address.startswith('0x'):
            db.set_wallet_address(user_id, wallet_address)
            await update.message.reply_text(get_text(user_id, 'wallet_changed'))
            context.user_data['awaiting_wallet'] = False
            await settings(update, context)
            return
        else:
            await update.message.reply_text(get_text(user_id, 'wallet_invalid'))
            return
    # Остальное — передать дальше
    return False

# --- Класс UserState (для совместимости с legacy state logic) ---
class UserState:
    WAITING_INVITE = "waiting_invite"
    WAITING_WALLET = "waiting_wallet"
    WAITING_DEPOSIT_AMOUNT = "waiting_deposit_amount"
    WAITING_TX_HASH = "waiting_tx_hash"
    WAITING_WITHDRAWAL_AMOUNT = "waiting_withdrawal_amount"
    WAITING_NEW_WALLET = "waiting_new_wallet"

def main():
    """Запуск бота"""
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
    
    # Добавляем ежедневную задачу (если JobQueue доступен)
    try:
        job_queue = application.job_queue
        if job_queue:
            job_queue.run_daily(daily_yield_task, time=time(hour=9, minute=0))
            logger.info("JobQueue initialized successfully")
        else:
            logger.warning("JobQueue not available - daily yield task disabled")
    except Exception as e:
        logger.warning(f"Failed to initialize JobQueue: {e}")
        logger.info("Bot will run without daily yield task")
    
    # Запускаем бота
    logger.info("Starting HYDRA bot...")
    application.run_polling()

if __name__ == '__main__':
    main() 