#!/usr/bin/env python3
"""
Тестирование основных функций HYDRA бота
"""

import sqlite3
import os
from database import Database
from signals_simulator import SignalsSimulator
from config import STRATEGIES, FAKE_DEPOSIT_ADDRESS

def test_database():
    """Тестирование базы данных"""
    print("🧪 Тестирование базы данных...")
    
    # Создаем временную базу для тестов
    test_db_path = "test_hydra.db"
    
    # Удаляем старую тестовую базу если существует
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Создаем экземпляр базы данных
    db = Database()
    db.db_path = test_db_path
    db.init_database()
    
    # Тест 1: Добавление пользователя
    print("  ✓ Тест 1: Добавление пользователя")
    db.add_user(123456789, "test_user")
    user = db.get_user(123456789)
    assert user is not None, "Пользователь не добавлен"
    print("    Пользователь добавлен успешно")
    
    # Тест 2: Установка адреса кошелька
    print("  ✓ Тест 2: Установка адреса кошелька")
    test_wallet = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    db.set_wallet_address(123456789, test_wallet)
    user = db.get_user(123456789)
    assert user[2] == test_wallet, "Адрес кошелька не установлен"
    print("    Адрес кошелька установлен успешно")
    
    # Тест 3: Добавление депозита
    print("  ✓ Тест 3: Добавление депозита")
    db.add_deposit(123456789, 500.0, "0x1234567890abcdef")
    print("    Депозит добавлен успешно")
    
    # Тест 4: Подтверждение депозита
    print("  ✓ Тест 4: Подтверждение депозита")
    db.confirm_deposit(123456789, 500.0)
    balance = db.get_balance(123456789)
    assert balance == 500.0, f"Баланс не обновлен: {balance}"
    print(f"    Баланс обновлен: {balance} USDT")
    
    # Тест 5: Активация стратегии
    print("  ✓ Тест 5: Активация стратегии")
    success = db.activate_strategy(123456789, "ai_arbitrage", 300.0)
    assert success, "Стратегия не активирована"
    balance = db.get_balance(123456789)
    assert balance == 200.0, f"Баланс не списан: {balance}"
    print("    Стратегия активирована успешно")
    
    # Тест 6: Получение стратегий пользователя
    print("  ✓ Тест 6: Получение стратегий пользователя")
    strategies = db.get_user_strategies(123456789)
    assert len(strategies) == 1, "Стратегия не найдена"
    print(f"    Найдено стратегий: {len(strategies)}")
    
    # Тест 7: Начисление доходности
    print("  ✓ Тест 7: Начисление доходности")
    db.add_yield(123456789, "ai_arbitrage", 8.0, "2024-01-15")
    total_yield = db.get_total_yield(123456789)
    assert total_yield == 8.0, f"Доходность не начислена: {total_yield}"
    print(f"    Доходность начислена: {total_yield} USDT")
    
    # Тест 8: Запрос на вывод
    print("  ✓ Тест 8: Запрос на вывод")
    success = db.request_withdrawal(123456789, 100.0)
    assert success, "Запрос на вывод не создан"
    print("    Запрос на вывод создан успешно")
    
    # Очистка
    os.remove(test_db_path)
    print("  🗑️ Тестовая база данных удалена")
    print("✅ Все тесты базы данных пройдены успешно!\n")

def test_signals_simulator():
    """Тестирование симулятора сигналов"""
    print("🧪 Тестирование симулятора сигналов...")
    
    simulator = SignalsSimulator()
    
    # Тест 1: Генерация одного сигнала
    print("  ✓ Тест 1: Генерация одного сигнала")
    signal = simulator.generate_signal()
    assert 'pair' in signal, "Сигнал не содержит пару"
    assert 'type' in signal, "Сигнал не содержит тип"
    assert 'entry_price' in signal, "Сигнал не содержит цену входа"
    print(f"    Сгенерирован сигнал: {signal['pair']} - {signal['type']}")
    
    # Тест 2: Генерация нескольких сигналов
    print("  ✓ Тест 2: Генерация нескольких сигналов")
    signals = simulator.generate_daily_signals(3)
    assert len(signals) == 3, f"Неверное количество сигналов: {len(signals)}"
    print(f"    Сгенерировано сигналов: {len(signals)}")
    
    # Тест 3: Обзор рынка
    print("  ✓ Тест 3: Обзор рынка")
    overview = simulator.get_market_overview()
    assert len(overview) > 0, "Обзор рынка пустой"
    print("    Обзор рынка сгенерирован")
    
    # Тест 4: Советы по риск-менеджменту
    print("  ✓ Тест 4: Советы по риск-менеджменту")
    tips = simulator.get_risk_management_tips()
    assert len(tips) > 0, "Советы пустые"
    print("    Советы по риск-менеджменту сгенерированы")
    
    print("✅ Все тесты симулятора сигналов пройдены успешно!\n")

def test_config():
    """Тестирование конфигурации"""
    print("🧪 Тестирование конфигурации...")
    
    # Тест 1: Проверка стратегий
    print("  ✓ Тест 1: Проверка стратегий")
    assert len(STRATEGIES) == 3, f"Неверное количество стратегий: {len(STRATEGIES)}"
    
    for strategy_id, strategy in STRATEGIES.items():
        assert 'name' in strategy, f"Стратегия {strategy_id} не содержит название"
        assert 'min_deposit' in strategy, f"Стратегия {strategy_id} не содержит мин. депозит"
        assert 'max_yield' in strategy, f"Стратегия {strategy_id} не содержит доходность"
        print(f"    Стратегия '{strategy['name']}' проверена")
    
    # Тест 2: Проверка адреса депозита
    print("  ✓ Тест 2: Проверка адреса депозита")
    assert len(FAKE_DEPOSIT_ADDRESS) == 42, "Неверная длина адреса"
    assert FAKE_DEPOSIT_ADDRESS.startswith('0x'), "Адрес не начинается с 0x"
    print(f"    Адрес депозита: {FAKE_DEPOSIT_ADDRESS}")
    
    print("✅ Все тесты конфигурации пройдены успешно!\n")

def demo_signals():
    """Демонстрация генерации сигналов"""
    print("🎯 ДЕМОНСТРАЦИЯ СИГНАЛОВ")
    print("=" * 50)
    
    simulator = SignalsSimulator()
    
    # Генерируем сигналы
    signals = simulator.generate_daily_signals(3)
    
    for i, signal in enumerate(signals, 1):
        emoji = "🟢" if signal['type'] == 'LONG' else "🔴"
        print(f"\n{i}. {emoji} {signal['pair']} - {signal['type']}")
        print(f"   💰 Цена входа: ${signal['entry_price']}")
        print(f"   🎯 Цель: ${signal['target_price']}")
        print(f"   🛑 Стоп-лосс: ${signal['stop_loss']}")
        print(f"   ⏰ Время: {signal['time']}")
        print(f"   👨‍💼 Аналитик: {signal['analyst']}")
        print(f"   📊 Уверенность: {signal['confidence']}")
        print(f"   ⚖️ R/R: 1:{signal['risk_reward']}")
        print(f"   📝 {signal['description']}")
    
    print(f"\n{simulator.get_market_overview()}")
    print(f"\n{simulator.get_risk_management_tips()}")
    print("=" * 50)

def main():
    """Основная функция тестирования"""
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ HYDRA БОТА")
    print("=" * 50)
    
    try:
        test_database()
        test_signals_simulator()
        test_config()
        
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 50)
        
        # Демонстрация
        demo_signals()
        
    except Exception as e:
        print(f"❌ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 