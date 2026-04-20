import telebot

TOKEN = "8759599601:AAGOQ0h3UJkz14Qur_Gm2oTaSvEAzaOTerk"

bot = telebot.TeleBot(TOKEN)

print("БОТ СТАРТАНУЛ")

bot.delete_webhook()

@bot.message_handler(commands=['start'])
def start(message):
    print("ПРИШЕЛ /start")
    bot.send_message(message.chat.id, "БОТ РАБОТАЕТ ✅")

@bot.message_handler(func=lambda message: True)
def test(message):
    print("ПРИШЛО СООБЩЕНИЕ:", message.text)
   
