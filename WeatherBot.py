import json

from telebot import TeleBot, types
from pyowm import OWM

bot = TeleBot("YOUR API KEY")
owm = OWM("YOUR API KEY")
mgr = owm.weather_manager()

up = None
left = None

try:
    with open('user_data.json', 'r') as file:
        user_data = json.load(file)
except FileNotFoundError:
    user_data = {}
@bot.message_handler(commands=["start"])
def start_message(message):
    user_id = str(message.chat.id)
    if user_id not in user_data:
        user_data[user_id] = {
            'latitude': None,
            'longitude': None
        }
        save_user_data()

    bot.send_message(message.chat.id, "Приветствую! Укажите вашу геопозицию, нажав на \"Местоположение\"")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Узнать погоду")
    button2 = types.KeyboardButton("Отправить местоположение", request_location=True)
    markup.add(button1, button2)

    bot.send_message(message.chat.id, "Выберите кнопку:", reply_markup=markup)

@bot.message_handler(content_types=["location"])
def handle_location(message):
    user_id = str(message.chat.id)
    user_data[user_id] = {
        'latitude': message.location.latitude,
        'longitude': message.location.longitude
    }
    save_user_data()
    bot.send_message(message.chat.id, "Геопозиция получена!")

@bot.message_handler(func=lambda message: message.text == "Узнать погоду")
def get_weather(message):
    user_id = str(message.chat.id)
    if user_id in user_data and user_data[user_id]['latitude'] is not None and user_data[user_id]['longitude'] is not None:
        latitude = user_data[user_id]['latitude']
        longitude = user_data[user_id]['longitude']
        
        try:
            weather = mgr.weather_at_coords(latitude, longitude).weather
            temperature = weather.temperature('celsius')["temp"]
            bot.send_message(message.chat.id, f"Температура: {temperature:.1f}°C")
        except Exception as error:
            bot.send_message(message.chat.id, "Не удалось получить данные о погоде. Попробуйте позже.")
            print(f"Ошибка: {error}")
    else:
        bot.send_message(message.chat.id, "Неизвестное местоположение или геопозиция не задана.")
def save_user_data():
    with open('user_data.json', 'w') as file:
        json.dump(user_data, file)

bot.polling(none_stop=True, interval=0)