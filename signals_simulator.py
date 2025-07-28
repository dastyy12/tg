import random
from datetime import datetime, timedelta
from typing import List, Dict

class SignalsSimulator:
    """Симулятор торговых сигналов от команды аналитиков"""
    
    def __init__(self):
        self.analysts = [
            "Михаил К.", "Алексей В.", "Дмитрий С.", "Сергей М.", "Андрей П.",
            "Владимир Р.", "Игорь Н.", "Павел Т.", "Роман Б.", "Артем Г.",
            "Николай Л.", "Евгений Д.", "Константин Ж.", "Александр З.", "Максим У."
        ]
        
        self.pairs = [
            "BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT", "DOT/USDT",
            "LINK/USDT", "UNI/USDT", "AVAX/USDT", "MATIC/USDT", "ATOM/USDT",
            "NEAR/USDT", "FTM/USDT", "ALGO/USDT", "VET/USDT", "ICP/USDT"
        ]
        
        self.signal_types = ["LONG", "SHORT"]
        
        # Базовые цены для симуляции
        self.base_prices = {
            "BTC/USDT": 43250,
            "ETH/USDT": 2680,
            "SOL/USDT": 98.50,
            "ADA/USDT": 0.485,
            "DOT/USDT": 7.25,
            "LINK/USDT": 15.80,
            "UNI/USDT": 7.95,
            "AVAX/USDT": 38.50,
            "MATIC/USDT": 0.85,
            "ATOM/USDT": 9.75,
            "NEAR/USDT": 3.45,
            "FTM/USDT": 0.425,
            "ALGO/USDT": 0.185,
            "VET/USDT": 0.032,
            "ICP/USDT": 12.80
        }
    
    def generate_signal(self) -> Dict:
        """Генерирует случайный торговый сигнал"""
        pair = random.choice(self.pairs)
        signal_type = random.choice(self.signal_types)
        analyst = random.choice(self.analysts)
        
        # Получаем базовую цену
        base_price = self.base_prices[pair]
        
        # Генерируем случайную цену входа (±5% от базовой)
        price_variation = random.uniform(-0.05, 0.05)
        entry_price = base_price * (1 + price_variation)
        
        # Генерируем цель (1-8% от цены входа)
        target_percent = random.uniform(0.01, 0.08)
        if signal_type == "LONG":
            target_price = entry_price * (1 + target_percent)
        else:
            target_price = entry_price * (1 - target_percent)
        
        # Генерируем стоп-лосс (1-3% от цены входа)
        stop_percent = random.uniform(0.01, 0.03)
        if signal_type == "LONG":
            stop_loss = entry_price * (1 - stop_percent)
        else:
            stop_loss = entry_price * (1 + stop_percent)
        
        # Генерируем время (в течение последних 24 часов)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        signal_time = datetime.now() - timedelta(hours=hours_ago, minutes=minutes_ago)
        
        # Генерируем уровень уверенности
        confidence = random.choice(["Высокий", "Средний", "Низкий"])
        
        # Генерируем описание
        descriptions = [
            "Сильный импульс на графике, ожидается пробой сопротивления",
            "Технический анализ показывает разворот тренда",
            "Фундаментальные факторы поддерживают движение",
            "Объем торгов растет, что подтверждает сигнал",
            "RSI показывает перепроданность/перекупленность",
            "MACD формирует дивергенцию",
            "Цена тестирует ключевой уровень поддержки/сопротивления",
            "Волновой анализ указывает на продолжение тренда"
        ]
        
        description = random.choice(descriptions)
        
        return {
            "pair": pair,
            "type": signal_type,
            "entry_price": round(entry_price, 2),
            "target_price": round(target_price, 2),
            "stop_loss": round(stop_loss, 2),
            "analyst": analyst,
            "time": signal_time.strftime("%H:%M UTC"),
            "confidence": confidence,
            "description": description,
            "risk_reward": round(abs(target_price - entry_price) / abs(stop_loss - entry_price), 2)
        }
    
    def generate_daily_signals(self, count: int = 5) -> List[Dict]:
        """Генерирует набор сигналов на день"""
        signals = []
        for _ in range(count):
            signals.append(self.generate_signal())
        
        # Сортируем по времени (новые сначала)
        signals.sort(key=lambda x: x["time"], reverse=True)
        return signals
    
    def get_market_overview(self) -> str:
        """Генерирует обзор рынка"""
        overviews = [
            "📊 РЫНОЧНЫЙ ОБЗОР\n\n"
            "🔴 BTC показывает признаки коррекции после достижения $44,000\n"
            "🟢 Altcoins демонстрируют относительную силу\n"
            "📈 Общий объем торгов растет на 15%\n"
            "⚠️ Внимание на макроэкономические события этой недели",
            
            "📊 РЫНОЧНЫЙ ОБЗОР\n\n"
            "🟢 Рынок восстанавливается после волатильности\n"
            "📈 ETH лидирует среди крупных монет\n"
            "🔴 DeFi токены показывают слабость\n"
            "💡 Рекомендуем осторожность при входе в позиции",
            
            "📊 РЫНОЧНЫЙ ОБЗОР\n\n"
            "🟢 Сильный бычий тренд продолжается\n"
            "📈 Институциональный спрос растет\n"
            "🟢 Малые монеты показывают лучшую динамику\n"
            "🎯 Фокус на качественных проектах с сильной командой"
        ]
        
        return random.choice(overviews)
    
    def get_risk_management_tips(self) -> str:
        """Генерирует советы по риск-менеджменту"""
        tips = [
            "⚠️ РИСК-МЕНЕДЖМЕНТ\n\n"
            "• Максимальный риск на сделку: 2% от капитала\n"
            "• Соотношение риск/прибыль: минимум 1:2\n"
            "• Диверсификация: не более 20% в одну монету\n"
            "• Стоп-лосс: обязателен для всех позиций",
            
            "⚠️ РИСК-МЕНЕДЖМЕНТ\n\n"
            "• Используйте трейлинг-стоп для прибыльных позиций\n"
            "• Не добавляйтесь к убыточным позициям\n"
            "• Следите за корреляцией между активами\n"
            "• Регулярно пересматривайте портфель"
        ]
        
        return random.choice(tips)

# Пример использования
if __name__ == "__main__":
    simulator = SignalsSimulator()
    
    print("=== ГЕНЕРАЦИЯ СИГНАЛОВ ===")
    signals = simulator.generate_daily_signals(3)
    
    for i, signal in enumerate(signals, 1):
        print(f"\n{i}. {signal['pair']} - {signal['type']}")
        print(f"   Цена входа: ${signal['entry_price']}")
        print(f"   Цель: ${signal['target_price']}")
        print(f"   Стоп-лосс: ${signal['stop_loss']}")
        print(f"   Аналитик: {signal['analyst']}")
        print(f"   Время: {signal['time']}")
        print(f"   Уверенность: {signal['confidence']}")
        print(f"   R/R: 1:{signal['risk_reward']}")
    
    print(f"\n{simulator.get_market_overview()}")
    print(f"\n{simulator.get_risk_management_tips()}") 