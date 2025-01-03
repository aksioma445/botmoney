import telebot
import json
import threading
import time
import requests
from datetime import datetime, timedelta

# Ініціалізація бота
API_TOKEN = '7649320035:AAGxuswMFdR28m413u-2nyPx7DMXW50Hvto'
GROUP_ID = -1002271256030  # Замінити на ID вашої групи
MANAGERS = [7403450527, 6097344709, 7564785089, 7342507058]  # ID адміністраторів/менеджерів
STATIC_INVITE_LINK = "https://t.me/+EVb9DMIQUJcwM2Uy"  # Вставте ваш статичний лінк

bot = telebot.TeleBot(API_TOKEN)

# Файл для зберігання даних
DATA_FILE = "user_data_odin.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Завантаження даних
user_data = load_data()

# Обробник команди /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id

    # Якщо доступ вже був наданий
    if str(user_id) in user_data:
        bot.send_photo(
            user_id,
            photo=open('moneyclubimage.jpg', 'rb'),
            caption=(
                f"Ви вже отримали доступ. \n"
                f"Відкрий двері до світу крипти всього за 1000$ із Money Club 💰\n"
                f"\n"
                f"✏️ Є запитання? Звертайтеся до нашого менеджера: \n"
                f"@Elvis_cryptofathers\n"
                f"\n"
                f"⚠️ Зверніть увагу\n"
                f"Перевіряйте наші офіційні контакти https://t.me/crypt0_fathers/45\n"
                f"\n"
                f"👉 Ваше посилання для доступу до групи: {STATIC_INVITE_LINK}\n"
                f"🚀 Почніть свій шлях зі стратегією CryptoFathers\n"
    )
        )
        return

    # Збереження інформації про доступ
    user_data[str(user_id)] = {
        "start_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
        "notified": False
    }
    save_data(user_data)

    # Надсилання посилання користувачеві
    bot.send_photo(
        user_id,
        photo=open('moneyclubimage.jpg', 'rb'),
        caption=(
            f"Відкрий двері до світу крипти всього за 1000$ із Money Club 💰\n"
            f"\n"
            f"✏️ Є запитання? Звертайтеся до нашого менеджера: \n"
            f"@Elvis_cryptofathers\n"
            f"\n"
            f"⚠️ Зверніть увагу\n"
            f"Перевіряйте наші офіційні контакти https://t.me/crypt0_fathers/45\n"
            f"\n"
            f"👉 Ваше посилання для доступу до групи: {STATIC_INVITE_LINK}\n"
            f"🚀 Почніть свій шлях зі стратегією CryptoFathers\n"
        )
    )

# Автоматичне нагадування про закінчення строку
def check_expiration():
    current_time = datetime.now()
    user_ids = list(user_data.keys())
    for user_id in user_ids:
        info = user_data[user_id]
        end_date = datetime.strptime(info["end_date"], "%Y-%m-%d %H:%M:%S")
        if not info.get("notified") and end_date - current_time <= timedelta(seconds=1000):
            bot.send_message(int(user_id), "Ваш безкоштовний доступ На 30 днів закінчується. \n"
                                           "\n"
                                           "Напишіть менеджеру для продовження доступу.\n"
                                           f"Ціна доступу до vip групи \n"
                                           f"🪙Money club❤️  1000$💵\n"
                                           "\n"
                                           "Менеджер: @Elvis_cryptofathers\n"
                                           "\n"
                                           f"⚠️Будь ласка перевіряйте наши контакти за посиланням https://t.me/crypt0_fathers/45 🔤\n")
            info["notified"] = True
            save_data(user_data)
        elif end_date <= current_time:
            bot.send_message(int(user_id), "Ваш доступ завершено.")
            bot.kick_chat_member(chat_id=GROUP_ID, user_id=int(user_id))  # Видалити користувача з групи
            del user_data[user_id]  # Видалити користувача з даних
            save_data(user_data)

# Команда для менеджерів продовжувати доступ
@bot.message_handler(commands=['add'])
def add_days(message):
    if message.from_user.id not in MANAGERS:
        bot.reply_to(message, "У вас немає прав для використання цієї команди.")
        return

    try:
        _, user_id, minutes = message.text.split()
        user_id = int(user_id)
        minutes = int(minutes)

        if str(user_id) not in user_data:
            bot.reply_to(message, "Цей користувач не отримував посилання.")
            return

        user_data[str(user_id)]["end_date"] = (datetime.strptime(user_data[str(user_id)]["end_date"], "%Y-%m-%d %H:%M:%S") + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        user_data[str(user_id)]["notified"] = False
        save_data(user_data)

        bot.send_message(user_id, f"Ваш доступ було продовжено на {minutes} хвилин. Ось ваше посилання: {STATIC_INVITE_LINK}")
        bot.reply_to(message, "Доступ продовжено.")
    except ValueError:
        bot.reply_to(message, "Неправильний формат. Використовуйте: /add <user_id> <minutes>")

# Запуск циклу перевірки строку дії
def background_task():
    while True:
        check_expiration()
        time.sleep(10)  # Перевіряти кожні 10 секунд для тестування

threading.Thread(target=background_task, daemon=True).start()

# Keep-Alive функція
def keep_alive():
    """Пінгує PythonAnywhere URL, щоб уникнути тайм-ауту."""
    while True:
        try:
            requests.get("https://botsfortg.pythonanywhere.com/")  # Використовуйте свій Flask-лінк
            print("Keep-Alive запит успішний")
        except Exception as e:
            print(f"Помилка Keep-Alive: {e}")
        time.sleep(600)  # Пінг кожні 10 хвилин

# Обробка bot.polling() для уникнення збоїв
def start_bot():
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Помилка в bot.polling(): {e}")
            time.sleep(5)  # Зачекайте перед перезапуском

# Запускаємо Keep-Alive у фоновій нитці
threading.Thread(target=keep_alive, daemon=True).start()

# Запуск бота
start_bot()
