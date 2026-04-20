import telebot
from telebot import types
import os

TOKEN = "8759599601:AAGOQ0h3UJkz14Qur_Gm2oTaSvEAzaOTerk"
ADMIN_ID = 6238864740

bot = telebot.TeleBot(TOKEN)

user_data = {}

print("Бот запущен...")

# 🔥 СБРОС WEBHOOK (ВАЖНО)
bot.delete_webhook()

# 🚀 ПРОВЕРКА (бот отвечает всегда)
@bot.message_handler(func=lambda message: True)
def debug(message):
    if message.text == "/start":
        start(message)
    else:
        bot.send_message(message.chat.id, "Я живой 🚀 Напиши /start")

# 🚀 СТАРТ
def start(message):
    markup = types.InlineKeyboardMarkup()

    btn_start = types.InlineKeyboardButton("🚀 Начать", callback_data="start_work")
    btn_call = types.InlineKeyboardButton("📞 Позвонить сейчас", url="tel:+79999999999")

    markup.add(btn_start)
    markup.add(btn_call)

    text = """
🚗 <b>Аварийная замочная помощь Хабаровск</b>

🔓 Вскрытие авто  
🔑 Дубликаты ключей  
🆘 Восстановление ключей  
⚙️ Иммобилайзеры  

⏱ Среднее время выезда: <b>15–30 минут</b>  
⏰ Работаем <b>24/7</b>  

Нажмите кнопку ниже 👇
"""

    try:
        with open("logo2.png", "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=text,
                parse_mode="HTML",
                reply_markup=markup
            )
    except:
        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=markup
        )

# 👉 кнопка старт
@bot.callback_query_handler(func=lambda call: call.data == "start_work")
def start_work(call):
    user_data[call.message.chat.id] = {}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔓 Вскрыть авто")
    markup.row("🔑 Сделать дубликат ключа")
    markup.row("🆘 Восстановление утерянных ключей")
    markup.row("⚙️ Ремонт системы иммобилайзера")

    bot.send_message(call.message.chat.id, "Выберите услугу:", reply_markup=markup)

# выбор услуги
@bot.message_handler(func=lambda message: message.text in [
    "🔓 Вскрыть авто",
    "🔑 Сделать дубликат ключа",
    "🆘 Восстановление утерянных ключей",
    "⚙️ Ремонт системы иммобилайзера"
])
def choose_service(message):
    user_data[message.chat.id]['service'] = message.text
    bot.send_message(message.chat.id, "Ваше имя:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "Телефон:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_data[message.chat.id]['phone'] = message.text
    bot.send_message(message.chat.id, "Марка, модель и год авто:")
    bot.register_next_step_handler(message, get_car)

def get_car(message):
    user_data[message.chat.id]['car'] = message.text
    bot.send_message(message.chat.id, "Опишите проблему:")
    bot.register_next_step_handler(message, get_problem)

def get_problem(message):
    user_data[message.chat.id]['problem'] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    geo = types.KeyboardButton("📍 Геолокация", request_location=True)

    markup.add(geo)
    markup.add("✍️ Ввести адрес")

    bot.send_message(message.chat.id, "Укажите адрес:", reply_markup=markup)

# гео
@bot.message_handler(content_types=['location'])
def get_location(message):
    data = user_data.get(message.chat.id, {})

    lat = message.location.latitude
    lon = message.location.longitude

    link = f"https://yandex.ru/maps/?pt={lon},{lat}"

    send_request(data, link, message)

# вручную
@bot.message_handler(func=lambda message: message.text == "✍️ Ввести адрес")
def manual(message):
    bot.send_message(message.chat.id, "Введите адрес:")
    bot.register_next_step_handler(message, save_address)

def save_address(message):
    data = user_data.get(message.chat.id, {})

    address = message.text
    link = f"https://yandex.ru/maps/?text={address}"

    send_request(data, link, message)

# отправка
def send_request(data, link, message):
    text = f"""
🚗 НОВАЯ ЗАЯВКА

🛠 {data.get('service')}
👤 {data.get('name')}
📞 {data.get('phone')}
🚘 {data.get('car')}
⚠️ {data.get('problem')}

📍 {link}
"""

    try:
        bot.send_message(ADMIN_ID, text)
    except Exception as e:
        print("Ошибка отправки:", e)

    bot.send_message(
        message.chat.id,
        "✅ Заявка принята!\nСвяжемся с вами через 5–10 минут"
    )

# запуск
bot.infinity_polling(timeout=30, long_polling_timeout=30)
