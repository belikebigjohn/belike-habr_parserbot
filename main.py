import telebot
from telebot import types
import datetime as dt
import json
from habr_parser import get_first_article
from habr_parser import get_article_by_flow
from aiogram.utils.markdown import hlink

TOKEN = "8430093365:AAEt-yI_SA6mvECaZuuol3LNTJlg7FelUr8"

bot = telebot.TeleBot(TOKEN)


# article_and_url = hlink(get_first_article())

@bot.message_handler(commands=['first_article'])
def handle_first_article(message):
    bot.send_message(message.chat.id, get_first_article(), parse_mode='HTML')


@bot.message_handler(commands=['start'])
def handle_start(message):
    now = dt.datetime.now()
    realtime = f"{now.date()} ; {now.hour}:{now.minute}"

    murkup = types.ReplyKeyboardMarkup()
    b1 = types.KeyboardButton(f"New article | {realtime}")
    bflow = types.KeyboardButton("По потокам")
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

    article_text = get_article_by_flow(flow)

    if article_text:
        bot.send_message(call.message.chat.id, article_text, parse_mode="HTML")
    else:
        bot.send_message(call.message.chat.id, "Error/send_article_from_flow()")

    bot.answer_callback_query(call.id)


bot.polling()
