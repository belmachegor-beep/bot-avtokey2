import telebot
from telebot import types
import json
import os

TOKEN = "8759599601:AAGOQ0h3UJkz14Qur_Gm2oTaSvEAzaOTerk"
ADMIN_ID = 6238864740

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"
user_data = {}

# ================== СОХРАНЕНИЕ ==================
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)

load_data()

# ================== СТАРТ ==================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Начать", callback_data="start_work"))

    text = """
🚗 <b>Аварийная замочная помощь</b>

🔓 Вскрытие авто  
🔑 Дубликаты ключей  
🆘 Восстановление ключей  
⚙️ Иммобилайзеры  

⏱ Работаем <b>24/7</b>

Нажмите кнопку ниже 👇
"""

    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

# ================== НАЧАЛО ==================
@bot.callback_query_handler(func=lambda call: call.data == "start_work")
def start_work(call):
    user_data[str(call.message.chat.id)] = {"status": "new"}
    save_data()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔓 Вскрыть авто")
    markup.row("🔑 Дубликат ключа")
    markup.row("🆘 Восстановление ключей")
    markup.row("⚙️ Иммобилайзер")
    markup.row("❌ Отменить заявку")

    bot.send_message(call.message.chat.id, "Выберите услугу:", reply_markup=markup)

# ================== ОТМЕНА ==================
@bot.message_handler(func=lambda m: m.text == "❌ Отменить заявку")
def cancel(message):
    user_data.pop(str(message.chat.id), None)
    save_data()

    bot.send_message(
        message.chat.id,
        "❌ Заявка отменена",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ================== ВЫБОР УСЛУГИ ==================
@bot.message_handler(func=lambda m: m.text in [
    "🔓 Вскрыть авто",
    "🔑 Дубликат ключа",
    "🆘 Восстановление ключей",
    "⚙️ Иммобилайзер"
])
def service(message):
    user_data[str(message.chat.id)]["service"] = message.text
    save_data()

    bot.send_message(message.chat.id, "Ваше имя?")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[str(message.chat.id)]["name"] = message.text
    save_data()

    bot.send_message(message.chat.id, "Телефон:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    user_data[str(message.chat.id)]["phone"] = message.text
    save_data()

    bot.send_message(message.chat.id, "Авто (марка/модель/год):")
    bot.register_next_step_handler(message, get_car)

def get_car(message):
    user_data[str(message.chat.id)]["car"] = message.text
    save_data()

    bot.send_message(message.chat.id, "Опишите проблему:")
    bot.register_next_step_handler(message, get_problem)

def get_problem(message):
    user_data[str(message.chat.id)]["problem"] = message.text
    save_data()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📍 Геолокация", request_location=True))
    markup.add("✍️ Ввести адрес вручную")
    markup.add("❌ Отменить заявку")

    bot.send_message(message.chat.id, "Отправьте локацию:", reply_markup=markup)

# ================== ГЕО ==================
@bot.message_handler(content_types=['location'])
def location(message):
    lat = message.location.latitude
    lon = message.location.longitude

    link = f"https://yandex.ru/maps/?pt={lon},{lat}"
    send_request(message, link)

# ================== АДРЕС ==================
@bot.message_handler(func=lambda m: m.text == "✍️ Ввести адрес вручную")
def manual(message):
    bot.send_message(message.chat.id, "Введите адрес:")
    bot.register_next_step_handler(message, save_address)

def save_address(message):
    link = f"https://yandex.ru/maps/?text={message.text}"
    send_request(message, link)

# ================== КНОПКИ АДМИНА ==================
def admin_buttons(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🟡 Принять", callback_data=f"accept_{user_id}"),
        types.InlineKeyboardButton("🚗 В пути", callback_data=f"drive_{user_id}"),
        types.InlineKeyboardButton("✅ Завершено", callback_data=f"done_{user_id}")
    )
    return markup

# ================== ОТПРАВКА ==================
def send_request(message, map_link):
    data = user_data.get(str(message.chat.id), {})

    text = f"""
🚗 НОВАЯ ЗАЯВКА

🛠 {data.get('service')}
👤 {data.get('name')}
📞 {data.get('phone')}
🚘 {data.get('car')}
⚠️ {data.get('problem')}

📍 {map_link}

📊 Статус: 🟡 Новая
ID: {message.chat.id}
"""

    bot.send_message(ADMIN_ID, text, reply_markup=admin_buttons(message.chat.id))

    bot.send_message(
        message.chat.id,
        "✅ Заявка отправлена.\nОжидайте подтверждения."
    )

# ================== СТАТУСЫ ==================
@bot.callback_query_handler(func=lambda call: True)
def status_handler(call):
    action, user_id = call.data.split("_")

    if action == "accept":
        user_data[user_id]["status"] = "accepted"
        bot.send_message(user_id, "🟡 Заявка принята. Скоро позвоним.")
    elif action == "drive":
        user_data[user_id]["status"] = "on_way"
        bot.send_message(user_id, "🚗 Мастер уже в пути!")
    elif action == "done":
        user_data[user_id]["status"] = "done"
        bot.send_message(user_id, "✅ Работа завершена. Спасибо!")

    save_data()

# ================== ЗАПУСК ==================
print("Бот запущен...")
bot.infinity_polling()