from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    """Главное меню бота"""
    keyboard = [
        [KeyboardButton("🧠 Портфель"), KeyboardButton("📈 Стратегии")],
        [KeyboardButton("📡 Сигналы"), KeyboardButton("💰 Депозит")],
        [KeyboardButton("🔁 Вывод"), KeyboardButton("⚙️ Настройки")],
        [KeyboardButton("📜 История"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_strategies_keyboard():
    """Клавиатура для выбора стратегий"""
    keyboard = [
        [InlineKeyboardButton("🧠 AI-арбитраж", callback_data="strategy_ai_arbitrage")],
        [InlineKeyboardButton("💧 Пулы ликвидности", callback_data="strategy_liquidity_pools")],
        [InlineKeyboardButton("📊 Сигналы аналитиков", callback_data="strategy_analyst_signals")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_strategy_activation_keyboard(strategy_id, amount):
    """Клавиатура для активации стратегии"""
    keyboard = [
        [InlineKeyboardButton(f"✅ Активировать", callback_data=f"activate_{strategy_id}_{amount}")],
        [InlineKeyboardButton("🔙 Назад к стратегиям", callback_data="back_to_strategies")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard(request_type, request_id):
    """Клавиатура для админа"""
    if request_type == "deposit":
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить депозит", 
                                 callback_data=f"confirm_deposit_{request_id}")],
            [InlineKeyboardButton("❌ Отклонить", 
                                 callback_data=f"reject_deposit_{request_id}")]
        ]
    elif request_type == "withdrawal":
        keyboard = [
            [InlineKeyboardButton("✅ Выполнить вывод", 
                                 callback_data=f"confirm_withdrawal_{request_id}")],
            [InlineKeyboardButton("❌ Отклонить", 
                                 callback_data=f"reject_withdrawal_{request_id}")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", 
                                 callback_data=f"confirm_{request_type}_{request_id}")],
            [InlineKeyboardButton("❌ Отклонить", 
                                 callback_data=f"reject_{request_type}_{request_id}")]
        ]
    
    return InlineKeyboardMarkup(keyboard)

def get_yield_keyboard(user_id):
    """Клавиатура для начисления доходности"""
    keyboard = [
        [InlineKeyboardButton("💰 Начислить доходность", 
                             callback_data=f"add_yield_{user_id}")],
        [InlineKeyboardButton("📊 Проверить баланс", 
                             callback_data=f"check_balance_{user_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard) 

def get_back_keyboard(callback="back_to_main"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data=callback)]])

def get_portfolio_strategy_keyboard(strategy_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отключить стратегию", callback_data=f"deactivate_{strategy_id}")],
        [InlineKeyboardButton("🔙 Назад к портфелю", callback_data="back_to_portfolio")]
    ])

def get_history_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад к портфелю", callback_data="back_to_portfolio")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
    ]) 

def get_limited_menu():
    keyboard = [
        [KeyboardButton("💰 Депозит")],
        [KeyboardButton("⚙️ Настройки"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False) 

def get_admin_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Массовые действия", callback_data="admin_mass")],
        [InlineKeyboardButton("🕒 Последние события", callback_data="admin_events")]
    ])

def get_admin_users_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Баланс пользователя", callback_data="admin_user_balance")],
        [InlineKeyboardButton("📜 История пользователя", callback_data="admin_user_history")],
        [InlineKeyboardButton("🚫 Блокировка", callback_data="admin_user_block")],
        [InlineKeyboardButton("✅ Разблокировка", callback_data="admin_user_unblock")],
        [InlineKeyboardButton("✉️ Сообщение пользователю", callback_data="admin_user_message")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_back_main")]
    ])

def get_admin_mass_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Начислить доходность всем", callback_data="admin_mass_yield")],
        [InlineKeyboardButton("📢 Рассылка всем", callback_data="admin_mass_broadcast")],
        [InlineKeyboardButton("🔔 Оповещение о депозите", callback_data="admin_mass_deposit_notify")],
        [InlineKeyboardButton("👥 Все пользователи", callback_data="admin_mass_users")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_back_main")]
    ])

def get_admin_events_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 Последние депозиты", callback_data="admin_events_deposits")],
        [InlineKeyboardButton("🔁 Последние выводы", callback_data="admin_events_withdrawals")],
        [InlineKeyboardButton("🆘 Последние запросы помощи", callback_data="admin_events_help")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_back_main")]
    ]) 

def get_admin_mass_notify_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("AI-арбитраж", callback_data="admin_mass_notify_ai_arbitrage")],
        [InlineKeyboardButton("Пулы ликвидности", callback_data="admin_mass_notify_liquidity_pools")],
        [InlineKeyboardButton("Сигналы аналитиков", callback_data="admin_mass_notify_analyst_signals")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_mass")]
    ]) 