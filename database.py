import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                wallet_address TEXT,
                balance REAL DEFAULT 0,
                is_verified BOOLEAN DEFAULT FALSE,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                language TEXT DEFAULT 'ru'
            )
        ''')
        
        # Таблица депозитов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                tx_hash TEXT,
                status TEXT DEFAULT 'pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица стратегий пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                strategy_id TEXT,
                amount REAL,
                active BOOLEAN DEFAULT TRUE,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица доходности
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS yields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                strategy_id TEXT,
                amount REAL,
                date DATE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица запросов на вывод
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                status TEXT DEFAULT 'pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица сделок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                strategy_id TEXT,
                open_time TIMESTAMP,
                close_time TIMESTAMP,
                amount REAL,
                profit REAL,
                result_percent REAL,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username):
        """Добавление нового пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username)
            VALUES (?, ?)
        ''', (user_id, username))
        conn.commit()
        conn.close()
    
    def set_wallet_address(self, user_id, wallet_address):
        """Установка адреса кошелька"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET wallet_address = ? WHERE user_id = ?
        ''', (wallet_address, user_id))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        """Получение данных пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def add_deposit(self, user_id, amount, tx_hash):
        """Добавление депозита"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO deposits (user_id, amount, tx_hash)
            VALUES (?, ?, ?)
        ''', (user_id, amount, tx_hash))
        conn.commit()
        conn.close()
    
    def confirm_deposit(self, user_id, amount):
        """Подтверждение депозита и начисление баланса"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Обновляем статус депозита
        cursor.execute('''
            UPDATE deposits SET status = 'confirmed' 
            WHERE user_id = ? AND amount = ? AND status = 'pending'
        ''', (user_id, amount))
        
        # Начисляем баланс
        cursor.execute('''
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        ''', (amount, user_id))
        
        conn.commit()
        conn.close()
    
    def get_balance(self, user_id):
        """Получение баланса пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def activate_strategy(self, user_id, strategy_id, amount):
        """Активация стратегии"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Просто добавляем стратегию, не списываем средства
        cursor.execute('''
            INSERT INTO user_strategies (user_id, strategy_id, amount)
            VALUES (?, ?, ?)
        ''', (user_id, strategy_id, amount))
        conn.commit()
        conn.close()
    
    def get_user_strategies(self, user_id):
        """Получение активных стратегий пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strategy_id, amount, start_date FROM user_strategies 
            WHERE user_id = ? AND active = TRUE
        ''', (user_id,))
        strategies = cursor.fetchall()
        conn.close()
        return strategies
    
    def add_yield(self, user_id, strategy_id, amount, date):
        """Добавление доходности"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO yields (user_id, strategy_id, amount, date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, strategy_id, amount, date))
        
        # Начисляем доход на баланс
        cursor.execute('''
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        ''', (amount, user_id))
        
        conn.commit()
        conn.close()
    
    def get_total_yield(self, user_id):
        """Получение общей доходности пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(amount) FROM yields WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] else 0
    
    def request_withdrawal(self, user_id, amount):
        """Запрос на вывод средств"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем баланс
        cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        current_balance = cursor.fetchone()[0]
        
        if current_balance >= amount:
            # Списываем средства
            cursor.execute('''
                UPDATE users SET balance = balance - ? WHERE user_id = ?
            ''', (amount, user_id))
            
            # Создаем запрос на вывод
            cursor.execute('''
                INSERT INTO withdrawals (user_id, amount)
                VALUES (?, ?)
            ''', (user_id, amount))
            
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    
    def confirm_withdrawal(self, withdrawal_id):
        """Подтверждение вывода средств"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE withdrawals SET status = 'completed' WHERE id = ?
        ''', (withdrawal_id,))
        conn.commit()
        conn.close()
    
    def get_pending_requests(self):
        """Получение всех ожидающих запросов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Депозиты
        cursor.execute('''
            SELECT 'deposit' as type, d.id, u.user_id, u.username, d.amount, d.tx_hash, d.timestamp
            FROM deposits d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.status = 'pending'
        ''')
        deposits = cursor.fetchall()
        
        # Выводы
        cursor.execute('''
            SELECT 'withdrawal' as type, w.id, u.user_id, u.username, w.amount, NULL as tx_hash, w.timestamp
            FROM withdrawals w
            JOIN users u ON w.user_id = u.user_id
            WHERE w.status = 'pending'
        ''')
        withdrawals = cursor.fetchall()
        
        conn.close()
        return deposits + withdrawals 

    def verify_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close() 

    def get_deposits(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT amount, tx_hash, status, timestamp FROM deposits WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
        deposits = cursor.fetchall()
        conn.close()
        return deposits

    def get_strategy_activations(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT strategy_id, amount, start_date FROM user_strategies WHERE user_id = ? ORDER BY start_date DESC', (user_id,))
        activations = cursor.fetchall()
        conn.close()
        return activations

    def get_yields(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT strategy_id, amount, date FROM yields WHERE user_id = ? ORDER BY date DESC', (user_id,))
        yields = cursor.fetchall()
        conn.close()
        return yields

    def get_withdrawals(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT amount, status, timestamp FROM withdrawals WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
        withdrawals = cursor.fetchall()
        conn.close()
        return withdrawals 

    def add_trade(self, user_id, strategy_id, open_time, close_time, amount, profit, result_percent, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades (user_id, strategy_id, open_time, close_time, amount, profit, result_percent, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, strategy_id, open_time, close_time, amount, profit, result_percent, status))
        conn.commit()
        conn.close()

    def get_trades(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strategy_id, open_time, close_time, amount, profit, result_percent, status
            FROM trades WHERE user_id = ? ORDER BY close_time DESC
        ''', (user_id,))
        trades = cursor.fetchall()
        conn.close()
        return trades 

    def get_users(self, limit=10, offset=0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, balance, is_verified FROM users ORDER BY join_date DESC LIMIT ? OFFSET ?', (limit, offset))
        users = cursor.fetchall()
        conn.close()
        return users

    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, balance, is_verified FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    def get_last_deposits(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_id, amount, status, timestamp FROM deposits ORDER BY timestamp DESC LIMIT ?', (limit,))
        deposits = cursor.fetchall()
        conn.close()
        return deposits

    def get_last_withdrawals(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_id, amount, status, timestamp FROM withdrawals ORDER BY timestamp DESC LIMIT ?', (limit,))
        withdrawals = cursor.fetchall()
        conn.close()
        return withdrawals

    def get_last_help_requests(self, limit=10):
        # Для примера: если есть таблица help_requests, иначе можно реализовать через логи
        return [] 

    def set_language(self, user_id, lang):
        """Установить язык пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (lang, user_id))
        conn.commit()
        conn.close()

    def get_language(self, user_id):
        """Получить язык пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else 'ru' 