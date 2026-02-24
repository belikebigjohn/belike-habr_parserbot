import telebot
from pyexpat.errors import messages
from telebot import types
import datetime as dt
import json

from habr_parser import get_first_article
from habr_parser import get_article_by_flow
from aiogram.utils.markdown import hlink
from config import TOKEN


#TOKEN = ""

FILENAME = "complaints.json"

bot = telebot.TeleBot(TOKEN)

# article_and_url = hlink(get_first_article())

# ============= ОБРАБОТЧИКИ =============

@bot.message_handler(commands=['first_article'])
def handle_first_article(message):
    bot.send_message(message.chat.id, get_first_article(message), parse_mode='HTML')

now = dt.datetime.now()
realtime = f"{now.date()} ; {now.hour}:{now.minute}"

@bot.message_handler(commands=['start'])
def handle_start(message):
    murkup = types.ReplyKeyboardMarkup()
    b1 = types.KeyboardButton(f"New article | {realtime}")
    bflow = types.KeyboardButton("По потокам") #button flow
    murkup.add(b1, bflow)

    bot.send_message(message.chat.id, "Hi there! I`m a Habr parser bot.\n"
                                      "Enter /first_article for the hottest news from IT`s world", reply_markup=murkup)

flows = ("backend", "frontend", "admin", "information_security",
         "gamedev", "ai_and_ml", "design", "management", "marketing",
         "popsci", "develop")

# доделал нахождение ссылки первой статьи на потоке
@bot.message_handler(regexp=r'^New article \|')
def handle_new_article(message):
    handle_first_article(message)



# ============= СВЯЗКИ =============

@bot.message_handler(func=lambda message: message.text == "По потокам")
def show_flow_buttons(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    for flow in flows:
        # просто берём название потока и делаем первую букву большой
        name = flow.replace("_", " ").title()
        keyboard.add(
            types.InlineKeyboardButton(name, callback_data=f"flow:{flow}")
        )

    bot.send_message(
        message.chat.id,
        "Выберите поток:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("flow:"))
def send_article_from_flow(call):
    flow = call.data.split(":", 1)[1]

    article_text  = get_article_by_flow(flow, call)

    if article_text:
        bot.send_message(call.message.chat.id, article_text, parse_mode="HTML")
    else:
        bot.send_message(call.message.chat.id, "Error/send_article_from_flow()")

    bot.answer_callback_query(call.id)

# ============= ЖАЛОБЫ =============
users = {}

@bot.message_handler(commands=['complaint'])
def start_complaint(message):
    chat_id = message.chat.id
    users[chat_id] = {}
    bot.send_message(
        chat_id,
        "Вы заполняете форму обратной связи / жалобы.\n\nВведите своё имя:"
    )
    bot.register_next_step_handler(message, process_name)


def process_name(message):
    chat_id = message.chat.id
    if chat_id not in users:
        return bot.send_message(chat_id, "Сессия завершена. Начните заново: /complaint")

    users[chat_id]["name"] = message.text.strip()
    bot.send_message(chat_id, f"Отлично, {users[chat_id]['name']}.\nНа каком этапе возникла проблема?")
    bot.register_next_step_handler(message, process_stage)


def process_stage(message):
    chat_id = message.chat.id
    if chat_id not in users: return
    users[chat_id]["stage"] = message.text.strip()
    bot.send_message(chat_id, "Хорошо.\nОпишите проблему подробнее:")
    bot.register_next_step_handler(message, process_description)


def process_description(message):
    chat_id = message.chat.id
    if chat_id not in users: return
    users[chat_id]["description"] = message.text.strip()
    bot.send_message(chat_id, "Почти готово\nУкажите контактные данные (telegram, email и т.п.):")
    bot.register_next_step_handler(message, save_complaint)


def save_complaint(message):
    chat_id = message.chat.id
    if chat_id not in users:
        return bot.send_message(chat_id, "Сессия завершена.")

    contact = message.text.strip()

    complaint = {
        "name": users[chat_id].get("name", ""),
        "stage": users[chat_id].get("stage", ""),
        "description": users[chat_id].get("description", ""),
        "contact": contact,
        "timestamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # чтение
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # добавление в список
    str_chat_id = str(chat_id)
    if str_chat_id not in data:
        data[str_chat_id] = []

    data[str_chat_id].append(complaint)

    # запись
    try:
        with open(FILENAME, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        bot.send_message(chat_id, "Спасибо за информацию. Мы стараемся стать лучше для Вас!")

        # удаляем временные данные
        del users[chat_id]

    except Exception as e:
        bot.send_message(chat_id, f"Не удалось сохранить, {e}")
        print(f"Ошибка сохранения {chat_id}: {e}")


#исправить кривое сохранение в джос

bot.polling()