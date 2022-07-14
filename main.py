import logging, os, random, time, telebot
import sqlite3
from telebot import types
from dotenv import load_dotenv

load_dotenv()

bot_key = os.getenv('BOT_KEY')
#chat where bot will publish all messages anonymously
answers_chat = int(os.getenv('CHAT_FOR_ANSWERS'))
#channel or chat where bot will publish questions and answers
channel_to_publish = os.getenv('CHANNEL_TO_PUBLISH_QA')
#question and answer will be published with this hashtag
hashtag = os.getenv('HASHTAG')

bot_name = os.getenv('BOT_NAME')
diary_name = os.getenv('DIARY_NAME')
taglist_url = os.getenv('TAGLIST_URL')
channel_url = os.getenv('CHANNEL_URL')
chat_url = os.getenv('CHAT_URL')
shop_url = os.getenv('SHOP_URL')
master_usr_url = os.getenv('MASTER_USR_URL')
master_nick = os.getenv('MASTER_NICK')
little_usr_url = os.getenv('LITTLE_USR_URL')
little_nick = os.getenv('LITTLE_NICK')


format_str = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
logFormatter = logging.Formatter(format_str)
logging.basicConfig(filename="log.txt", level=logging.INFO, encoding = "UTF-8", format=format_str)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logging.getLogger().addHandler(consoleHandler)

bot = telebot.TeleBot(bot_key, parse_mode='HTML')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
qa = types.KeyboardButton('❔ Анонимные вопросы ❔')
tags = types.KeyboardButton('#️⃣ Список тегов сообщества #️⃣')
chat = types.KeyboardButton('💬 Чат 💬')
shop = types.KeyboardButton('🛒 Магазин 🛒')
diary = types.KeyboardButton('🐻 Дневничок 🐻')
contacts = types.KeyboardButton('📓 Контакты 📓')
markup.row(qa), markup.row(tags), markup.row(chat, shop), markup.row(diary, contacts)

mrkp_cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn = types.KeyboardButton('Отмена')
mrkp_cancel.add(btn)


@bot.message_handler(commands=['start', 'help'], chat_types='private')
def send_welcome(message):
    logging.info(f'\n~ New user! \n   - {message.from_user.username}\n')
    bot.send_message(message.chat.id, 'Привет!', reply_markup=markup)
    time.sleep(1)
    bot.send_message(message.chat.id, f'Это официальный бот сообщества <i><b>{diary_name}</b></i>!✨')
    time.sleep(1)
    bot.send_message(message.chat.id, f'Меня зовут {bot_name} и я буду помогать тебе во многом!')


@bot.message_handler(regexp='Анонимные вопросы', chat_types='private')
def ask_question(message):
    bot.send_message(message.chat.id, 'Отправь мне вопрос и я отвечу на него анонимно!', reply_markup=mrkp_cancel)
    bot.register_next_step_handler(message, react_on_question)


def react_on_question(message):
    logging.info(f'\n~ Question come! \n   - {message.from_user.username}\n   - {message.text}\n')
    reply_vars = [
        'Это очень хороший вопрос! Уже отправляю своим хозяевам.',
        'Хм, а это правда интересно! Уже спрашиваю, ждите ответ в дневничке!',
        'Вам обязательно ответят! Внимательно следите за дневничком, ответ появится там.']
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Как скажешь✨', reply_markup=markup)
        return
    bot.send_message(answers_chat, '<b>Внимание! Новый вопрос:</b>', reply_markup=None)
    match message.content_type:
        case 'text':
            bot.send_message(answers_chat, message.text)
        case 'photo':
            photo = message.photo[2]
            bot.send_photo(answers_chat, photo = photo.file_id, caption=message.caption, reply_markup=markup)
        case 'animation':
            bot.send_animation(answers_chat, animation=message.animation.file_id, caption=message.caption, reply_markup=markup)
        case 'video':
            bot.send_video(answers_chat, video=message.video.file_id, caption=message.caption, reply_markup=markup)
        case 'document':
            bot.send_document(answers_chat, document=message.document.file_id, caption=message.caption, reply_markup=markup)
        case 'audio':
            bot.send_audio(answers_chat, audio=message.audio.file_id, caption=message.caption, reply_markup=markup)
        case 'voice':
            bot.send_voice(answers_chat, voice=message.voice.file_id, caption=message.caption, reply_markup=markup)
        case 'sticker':
            bot.send_sticker(answers_chat, sticker=message.sticker.file_id, reply_markup=markup)
    bot.reply_to(message, random.choice(reply_vars), reply_markup=markup)


@bot.message_handler(func=lambda message: True, chat_types='group')
def react_on_answer(message):
    logging.info(f'\n~ Answer publishing! \n   - {message.reply_to_message.text or message.content_type}\n   - {message.text}\n')
    if message.chat.id != answers_chat:
        pass
        
    if message.from_user.username == "edwy_reed":
        message_text = f'<b>Вопросик💜:</b>\n ✨ {message.reply_to_message.text or "А текста нет!"} \n \n<b>Ответик💜:</b>\n 🦁 {message.text} \n \n{hashtag}'
    elif message.from_user.username == "redbeaniy":
        message_text = f'<b>Вопросик💜:</b>\n ✨ {message.reply_to_message.text or "А текста нет!"} \n \n<b>Ответик💜:</b>\n 🐱 {message.text} \n \n{hashtag}'

    match message.reply_to_message.content_type:
        case 'text':
            bot.send_message(channel_to_publish, message_text)
        case 'photo':
            photo = message.reply_to_message.photo[2]
            bot.send_photo(channel_to_publish, photo = photo.file_id, caption=message_text)
        case 'animation':
            bot.send_animation(channel_to_publish, animation=message.reply_to_message.animation.file_id, caption=message_text)
        case 'video':
            bot.send_video(channel_to_publish, video=message.reply_to_message.video.file_id, caption=message_text)
        case 'document':
            bot.send_document(channel_to_publish, document=message.reply_to_message.document.file_id, caption=message_text)
        case 'audio':
            bot.send_audio(channel_to_publish, audio=message.reply_to_message.audio.file_id, caption=message_text)
        case 'voice':
            bot.send_voice(channel_to_publish, voice=message.reply_to_message.voice.file_id, caption=message_text)
        case _:
            bot.send_message(answers_chat, 'Упс. У меня проблемки :( \nПроверьте логи, пожалуйста.')


@bot.message_handler(regexp='Список тегов сообщества', chat_types='private')
def show_tags(message):
    text = '<b>Держи!</b> Тебе достаточно просто нажать кнопочку и ты сможешь выбрать любой из тегов, просто нажав на него.'
    inline_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text = 'Открыть список тегов', url = taglist_url)
    inline_markup.add(btn)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(regexp='Чат', chat_types='private')
def show_chat(message):
    text = 'Прекрасно! Мы с нетерпением ждём тебя в нашем чатике, там очень комфортно и спокойно.'
    inline_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text = 'Перейти в чат', url = chat_url)
    inline_markup.add(btn)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(regexp='Магазин', chat_types='private')
def show_shop(message):
    text = 'Добро пожаловать в милый магазинчик китти-тян✨'
    inline_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text = 'Перейти в магазин', url = shop_url)
    btn2 = types.InlineKeyboardButton(text = 'Быстрый заказ', callback_data = 'carousel_init')
    inline_markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)
    

@bot.callback_query_handler(func=lambda call: True)
def carousel_handler(call):
    conn = sqlite3.connect("shop.sqlite")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    items = cursor.execute("SELECT * FROM accessories").fetchall()
    if call.data == 'carousel_init': 
        item_id = 0
    else: 
        item_id = get_current_item_id(items, call.message.html_caption)
    current_item = items[item_id]

    match call.data:
        case 'carousel_init':
            inline_markup = get_updated_markup(items, item_id, current_item)
            bot.send_photo(call.message.chat.id, photo = open(current_item[0], 'rb'), caption=current_item[1], reply_markup=inline_markup)
        case 'carousel_next':
            if item_id < len(items) - 1:
                item_id += 1
            else: item_id = 0
            current_item = items[item_id]
            photo = types.InputMediaPhoto(open(current_item[0], 'rb'), caption=current_item[1])
            inline_markup = get_updated_markup(items, item_id, current_item)
            bot.edit_message_media(media = photo, chat_id = call.message.chat.id, message_id = call.message.id, reply_markup=inline_markup)
        case 'carousel_prev':
            if item_id > 0:
                item_id -= 1
            else: item_id = len(items) - 1
            current_item = items[item_id]
            photo = types.InputMediaPhoto(open(current_item[0], 'rb'), caption=current_item[1])
            inline_markup = get_updated_markup(items, item_id, current_item)
            bot.edit_message_media(media = photo, chat_id = call.message.chat.id, message_id = call.message.id, reply_markup=inline_markup)
        case 'carousel_buy':
            if call.from_user.username is not None:
                photo = open(current_item[0], 'rb')
                bot.send_photo(chat_id = 664709929, photo = photo, caption = f'Заказ от пользователя @{call.from_user.username}')
            else:
                bot.send_message(call.message.chat.id, f'Мфь. Я не смогла увидеть ваш юзернейм.\nПожалуйста, напишите @redbeaniy для завершения заказа)')
                bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, f'Спасибо за выбор! В ближайшее время Малышка напишет вам, чтобы узнать детали заказа.')
            bot.delete_message(call.message.chat.id, call.message.id)
        case 'carousel_close':
            bot.delete_message(call.message.chat.id, call.message.id)
        case _:
            pass


def get_updated_markup(items, item_id, current_item):
    inline_markup = types.InlineKeyboardMarkup()
    btn0 = types.InlineKeyboardButton(text = '<-', callback_data = 'carousel_prev')
    btn1 = types.InlineKeyboardButton(text = f'{item_id + 1} из {len(items)}', callback_data = 'none')
    btn2 = types.InlineKeyboardButton(text = '->', callback_data = 'carousel_next')
    btn3 = types.InlineKeyboardButton(text = f'Купить за {current_item[2]} руб.', callback_data = 'carousel_buy')
    btn4 = types.InlineKeyboardButton(text = 'Закрыть', callback_data = 'carousel_close')
    inline_markup.row(btn0, btn1, btn2)
    inline_markup.row(btn3, btn4)
    return inline_markup


def get_current_item_id(items, html_caption):
    for i in range(len(items)):
        if items[i][1] == html_caption:
            return i
    return 0


@bot.message_handler(regexp='Дневничок', chat_types='private')
def show_diary(message):
    text = f'А вот и ссылочка на наше главное сообщество!\nТыкай кнопочку и делись ссылкой с друзьями: @beariy_diary'
    inline_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text = 'Перейти в дневник', url = channel_url)
    inline_markup.add(btn)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(regexp='Контакты', chat_types='private')
def show_contacts(message):
    text = 'Если у вас возникли вопросы или предложения, вы можете написать кому-то из нас лично.'
    inline_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text = little_nick, url = little_usr_url)
    btn2 = types.InlineKeyboardButton(text = master_nick, url = master_usr_url)
    inline_markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(func=lambda message: True, chat_types='private')
def unknown_command(message):
    text = 'Охх, прости, я не уверена, что поняла тебя, меня недавно обновили. Попробуй воспользоваться клавиатурой ниже.'
    bot.send_message(message.chat.id, text, reply_markup=markup)

bot.infinity_polling()