# 🔗 Настройка GitHub репозитория

## 📋 Пошаговая инструкция

### 1. Создайте репозиторий на GitHub

1. Перейдите на [github.com](https://github.com)
2. Нажмите "New repository" или "+" → "New repository"
3. Заполните:
   - **Repository name**: `hydra-bot` (или любое другое имя)
   - **Description**: `Hydra Bot for Telegram`
   - **Visibility**: Public или Private (на ваш выбор)
   - **НЕ** ставьте галочки на "Add a README file", "Add .gitignore", "Choose a license"
4. Нажмите "Create repository"

### 2. Подключите локальный репозиторий к GitHub

После создания репозитория, GitHub покажет команды. Выполните их в терминале:

```bash
# Добавьте remote origin (замените YOUR_USERNAME на ваше имя пользователя)
git remote add origin https://github.com/YOUR_USERNAME/hydra-bot.git

# Переименуйте ветку в main
git branch -M main

# Запушьте код
git push -u origin main
```

### 3. Проверьте подключение

```bash
# Проверьте remote
git remote -v

# Должно показать что-то вроде:
# origin  https://github.com/YOUR_USERNAME/hydra-bot.git (fetch)
# origin  https://github.com/YOUR_USERNAME/hydra-bot.git (push)
```

## 🔄 Обновление кода

После внесения изменений:

```bash
# Добавьте изменения
git add .

# Закоммитьте
git commit -m "Описание изменений"

# Запушьте
git push origin main
```

## 🚀 После настройки GitHub

1. **Обновите код в Render**:
   - Render автоматически подхватит изменения из GitHub
   - Сервис пересоберется с исправлениями

2. **Проверьте работу**:
   - Логи в Render Dashboard
   - Веб-интерфейс бота
   - Telegram бот

## 📁 Структура репозитория

После пуша в GitHub у вас должна быть такая структура:

```
hydra-bot/
├── bot.py                 # Основной код бота
├── bot_web.py            # Версия для Web Service
├── bot_worker.py         # Версия для Background Worker
├── app.py                # Flask приложение
├── config.py             # Конфигурация
├── database.py           # База данных
├── keyboards.py          # Клавиатуры
├── signals_simulator.py  # Симулятор сигналов
├── requirements.txt      # Зависимости
├── runtime.txt           # Версия Python
├── render.yaml           # Конфигурация Render (Web Service)
├── render-background.yaml # Конфигурация Render (Background Worker)
├── .gitignore           # Исключения Git
└── README.md            # Документация
```

## 🔧 Если возникли проблемы

### Проблема: "fatal: 'origin' does not appear to be a git repository"
**Решение**: Выполните команду `git remote add origin` из шага 2

### Проблема: "Permission denied"
**Решение**: 
1. Убедитесь, что вы авторизованы в GitHub
2. Проверьте правильность URL репозитория
3. Используйте SSH ключи или токен доступа

### Проблема: "Repository not found"
**Решение**:
1. Проверьте правильность имени пользователя и репозитория
2. Убедитесь, что репозиторий существует
3. Проверьте права доступа

## 📞 Поддержка

- **GitHub Help**: [help.github.com](https://help.github.com)
- **Git документация**: [git-scm.com/doc](https://git-scm.com/doc)

---

**После настройки GitHub, Render автоматически обновится с исправлениями! 🚀** 