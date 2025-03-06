import telebot # библиотека telebot
from telebot import types
from config import token # импорт токена

bot = telebot.TeleBot(token) 

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для управления чатом.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id

        # Если пользователь пытается забанить бота
        if user_id == bot.get_me().id:
            bot.reply_to(message, "Меня нельзя забанить!")
            return

        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.ban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите забанить.")

@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.reply_to_message:
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id

        # Если пользователь пытается змутить бота
        if user_id == bot.get_me().id:
            bot.reply_to(message, "Меня нельзя замутить!")
            return

        user_status = bot.get_chat_member(chat_id, user_id).status
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно замутить администратора.")
            return

        bot.restrict_chat_member(chat_id, user_id, can_send_messages=False)

        # Создание кнопки
        markup = types.InlineKeyboardMarkup()
        unmute_button = types.InlineKeyboardButton("Размутить", callback_data=f"unmute:{user_id}")
        markup.add(unmute_button)

        bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был замучен.", reply_markup=markup)

    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите замутить.")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data.startswith("unmute:"):
        user_id = int(call.data.split(":")[1])
        chat_id = call.message.chat.id
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)  # Востановление разрешений пользователю
        bot.edit_message_text(f"Пользователь с ID {user_id} был размучен.", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if "https://" in message.text:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status

        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Администратор отправил ссылку (не будет забанен).")
        else:
            bot.ban_chat_member(chat_id, user_id)
            bot.reply_to(message, f"Пользователь @{message.from_user.username} был забанен за отправку ссылки.")


@bot.message_handler(content_types=['new_chat_members'])
def make_some(message):
    bot.send_message(message.chat.id, 'Добро пожаловать!')
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)


bot.infinity_polling(none_stop=True)
