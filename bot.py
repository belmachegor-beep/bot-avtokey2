import telebot
from telebot import types

TOKEN = "8759599601:AAGOQ0h3UJkz14Qur_Gm2oTaSvEAzaOTerk"
ADMIN_ID = 6238864740

bot = telebot.TeleBot(TOKEN)

user_data = {}

print("Бот запущен...")

bot.delete_webhook()

# 🔥 СТАРТ
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn_start = types.InlineKeyboardButton("🚀 Начать", callback_data="start_work")
    markup.add(btn_start)

    text = """
🚗 <b>Аварийная замочная помощь</b>

🔓 Вскрытие авто  
🔑 Дубликаты ключей  
🆘 Восстановление ключей  
⚙️ Иммобилайзеры  

⏱ Выезд: 15–30 минут  
⏰ Работаем 24/7  

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
    bot.send_message(message.chat.id, "Пожалуйста, укажите ваше имя:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "Ваш номер телефона:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_data[message.chat.id]['phone'] = message.text
    bot.send_message(message.chat.id, "Марка, модель и год автомобиля:")
    bot.register_next_step_handler(message, get_car)

def get_car(message):
    user_data[message.chat.id]['car'] = message.text
    bot.send_message(message.chat.id, "Опишите проблему:")
    bot.register_next_step_handler(message, get_problem)

def get_problem(message):
    user_data[message.chat.id]['problem'] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    geo = types.KeyboardButton("📍 Отправить геолокацию", request_location=True)

    markup.add(geo)
    markup.add("✍️ Ввести адрес вручную")

    bot.send_message(message.chat.id, "Укажите адрес:", reply_markup=markup)

# геолокация
@bot.message_handler(content_types=['location'])
def get_location(message):
    data = user_data.get(message.chat.id, {})

    lat = message.location.latitude
    lon = message.location.longitude

    link = f"https://yandex.ru/maps/?pt={lon},{lat}"

    send_request(data, link, message)

# ввод адреса
@bot.message_handler(func=lambda message: message.text == "✍️ Ввести адрес вручную")
def manual_address(message):
    bot.send_message(message.chat.id, "Введите адрес:")
    bot.register_next_step_handler(message, save_address)

def save_address(message):
    data = user_data.get(message.chat.id, {})

    address = message.text
    link = f"https://yandex.ru/maps/?text={address}"

    send_request(data, link, message)

# отправка заявки
def send_request(data, link, message):
    text = f"""
🚗 <b>НОВАЯ ЗАЯВКА</b>

🛠 Услуга: {data.get('service')}
👤 Имя: {data.get('name')}
📞 Телефон: {data.get('phone')}
🚘 Авто: {data.get('car')}
⚠️ Проблема: {data.get('problem')}

📍 {link}
"""

    try:
        bot.send_message(ADMIN_ID, text, parse_mode="HTML")
    except Exception as e:
        print("Ошибка отправки:", e)

    bot.send_message(
        message.chat.id,
        "✅ Заявка принята! Мы свяжемся с вами в ближайшее время."
    )

# запуск
bot.infinity_polling(timeout=30, long_polling_timeout=30)
