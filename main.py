import logging, os, random, sys, time, telebot
from dotenv import load_dotenv

load_dotenv()

bot_key = os.getenv('BOT_KEY')
#chat where bot will publish all messages anonymously
answers_chat = int(os.getenv('CHAT_FOR_ANSWERS'))
#channel or chat where bot will publish questions and answers after your reply on question
channel_to_publish = os.getenv('CHAT_TO_PUBLISH_QA')
#hashtag that will be added in end of the final post
hashtag = os.getenv('HASHTAG')

format_str = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
logFormatter = logging.Formatter(format_str)
logging.basicConfig(filename="log.txt", level=logging.INFO, encoding = "UTF-8", format=format_str)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logging.getLogger().addHandler(consoleHandler)

bot = telebot.TeleBot(bot_key, parse_mode='MARKDOWN')


@bot.message_handler(commands=['start', 'help'], chat_types='private')
def send_welcome(message):
    logging.info(f'\n~ New user! \n   - {message.from_user.username}\n')
    bot.send_message(message.chat.id, 'Привет!')
    time.sleep(1)
    bot.send_message(message.chat.id, 'Тут можно задать ***любой*** вопрос абсолютно ***анонимно*** и при первой же возможности вам __ответят на него в своём канале__! ✨')
    time.sleep(1)
    bot.send_message(message.chat.id, 'Ну как, готовы?) Задавайте вопросики!')


@bot.message_handler(func=lambda message: True, chat_types='private')
def react_on_question(message):
    logging.info(f'\n~ Question come! \n   - {message.from_user.username}\n   - {message.text}\n')
    reply_vars = [
        'Это очень хороший вопрос! Уже отправляю своим хозяевам.',
        'Хм, а это правда интересно! Уже спрашиваю, ждите ответ в дневничке!',
        'Вам обязательно ответят! Внимательно следите за дневничком, ответ появится там.']
    bot.reply_to(message, random.choice(reply_vars))
    bot.send_message(answers_chat, '***Внимание! Новый вопрос:***')
    bot.send_message(answers_chat, message.text)


@bot.message_handler(func=lambda message: True, chat_types='group')
def react_on_answer(message):
    logging.info(f'\n~ Answer publishing! \n   - {message.reply_to_message.text}\n   - {message.text}\n')
    if message.chat.id == answers_chat:
        message = f'***Вопрос:\n • ***{message.reply_to_message.text} \n \n***Ответ:\n •*** {message.text} \n \n{hashtag}'
        bot.send_message(channel_to_publish, message)


bot.infinity_polling()