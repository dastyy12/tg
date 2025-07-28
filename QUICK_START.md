# 🚀 Быстрый старт: Развертывание Hydra Bot на Render

## ⚡ Экспресс-развертывание (5 минут)

### 1. Подготовка
```bash
# Убедитесь, что все файлы в репозитории
git add .
git commit -m "Ready for Render"
git push origin main
```

### 2. Создание Background Worker
1. Перейдите на [dashboard.render.com](https://dashboard.render.com)
2. Нажмите "New +" → "Background Worker"
3. Подключите GitHub репозиторий
4. Настройте:
   - **Name**: `hydra-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot_worker.py`

### 3. Переменные окружения
Добавьте в Environment Variables:
- `BOT_TOKEN` = ваш токен от @BotFather
- `ADMIN_CHAT_ID` = `-4827638107`
- `PYTHON_VERSION` = `3.11.0`

### 4. Запуск
Нажмите "Create Background Worker" и ждите 2-5 минут.

### 5. Проверка
- Статус должен быть "Live" (зеленый)
- Отправьте `/start` боту в Telegram

## 🎯 Рекомендуемый способ: Background Worker

**Почему Background Worker лучше для ботов:**
- ✅ Работает постоянно
- ✅ Проще настройка
- ✅ Меньше ресурсов
- ✅ Дешевле

## 📋 Необходимые файлы

Убедитесь, что в репозитории есть:
- ✅ `bot.py` - основной код бота
- ✅ `requirements.txt` - зависимости
- ✅ `runtime.txt` - версия Python
- ✅ `.gitignore` - исключения

## 🔧 Если что-то не работает

1. **Проверьте логи** в Render Dashboard
2. **Убедитесь в токене** - он должен быть правильным
3. **Проверьте статус** - должен быть "Live"

## 💡 Советы

- Используйте **Background Worker**, а не Web Service
- **Не коммитьте токены** в код
- **Мониторьте логи** для отладки
- **Начните с Free плана**

---

**Готово! Ваш бот работает на Render! 🎉** 