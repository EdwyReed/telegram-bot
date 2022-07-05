import logging, os, random, time, telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

bot_key = os.getenv('BOT_KEY_beta')
#chat where bot will publish all messages anonymously
answers_chat = int(os.getenv('CHAT_FOR_ANSWERS'))
#channel or chat where bot will publish questions and answers after your reply on question
channel_to_publish = os.getenv('CHAT_TO_PUBLISH_QA_beta')
#hashtag that will be added in end of the final post
hashtag = os.getenv('HASHTAG')

format_str = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
logFormatter = logging.Formatter(format_str)
logging.basicConfig(filename="log.txt", level=logging.INFO, encoding = "UTF-8", format=format_str)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logging.getLogger().addHandler(consoleHandler)

bot = telebot.TeleBot(bot_key, parse_mode='MARKDOWN')

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
qa = types.KeyboardButton('Анонимные вопросы')
tags = types.KeyboardButton('Список тегов сообщества')
chat = types.KeyboardButton('Чат')
shop = types.KeyboardButton(' Магазин')
contacts = types.KeyboardButton('Контакты')
markup.row(qa), markup.row(tags), markup.row(chat, shop), markup.row(contacts)

mrkp_cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn = types.KeyboardButton('Отмена')
mrkp_cancel.add(btn)


@bot.message_handler(commands=['start', 'help'], chat_types='private')
def send_welcome(message):
    logging.info(f'\n~ New user! \n   - {message.from_user.username}\n')
    bot.send_message(message.chat.id, 'Привет!', reply_markup=markup)
    time.sleep(1)
    bot.send_message(message.chat.id, 'Это официальный бот сообщества __**Beariy\'s Diary**__!✨')
    time.sleep(1)
    bot.send_message(message.chat.id, 'Меня зовут Бири и я буду помогать тебе во многом!')


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
    else:
        bot.reply_to(message, random.choice(reply_vars), reply_markup=markup)
        bot.send_message(answers_chat, '***Внимание! Новый вопрос:***')
        bot.send_message(answers_chat, message.text)


@bot.message_handler(func=lambda message: True, chat_types='group')
def react_on_answer(message):
    logging.info(f'\n~ Answer publishing! \n   - {message.reply_to_message.text}\n   - {message.text}\n')
    if message.chat.id == answers_chat:
        if message.from_user.username == "edwy_reed":
            message = f'***Вопросик💜:\n ✨ ***{message.reply_to_message.text} \n \n***Ответик💜:\n 🦁 ***{message.text} \n \n{hashtag}'
            bot.send_message(channel_to_publish, message)
        elif message.from_user.username == "redbeaniy":
            message = f'***Вопросик💜:\n ✨ ***{message.reply_to_message.text} \n \n***Ответик💜:\n 🐱 ***{message.text} \n \n{hashtag}'
            bot.send_message(channel_to_publish, message)


@bot.message_handler(regexp='Список тегов сообщества', chat_types='private')
def show_tags(message):
    text = '**Держи!** Тебе достаточно просто нажать кнопочку и ты сможешь выбрать любой из тегов, просто нажав на него.'
    inline_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text = 'Открыть список тэгов', url = 'https://t.me/beariy_diary/392')
    inline_markup.add(btn)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(regexp='Чат', chat_types='private')
def show_chat(message):
    text = 'Прекрасно! Мы с нетерпением ждём тебя в нашем чатике, там очень комфортно и спокойно.'
    inline_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text = 'Перейти в чат', url = 'https://t.me/beariy_chat')
    inline_markup.add(btn)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(regexp='Магазин', chat_types='private')
def show_shop(message):
    text = 'Добро пожаловать в милый магазинчик китти-тян✨'
    inline_markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text = 'Перейти в магазин', url = 'https://t.me/beariy_shop')
    inline_markup.add(btn)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(regexp='Контакты', chat_types='private')
def show_contacts(message):
    text = 'Если у вас возникли вопросы или предложения, вы можете написать кому-то из нас лично.'
    inline_markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text = 'Китти-тяма (Мяпкинс Младшая)', url = 'https://t.me/redbeaniy')
    btn2 = types.InlineKeyboardButton(text = 'Мяпкинс Старший', url = 'https://t.me/edwy_reed')
    inline_markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text, reply_markup=inline_markup)


@bot.message_handler(func=lambda message: True, chat_types='private')
def unknown_command(message):
    text = 'Охх, прости, не совсем тебя понял. Попробуй воспользоваться клавиатурой ниже.'
    bot.send_message(message.chat.id, text, reply_markup=markup)
        

bot.infinity_polling()