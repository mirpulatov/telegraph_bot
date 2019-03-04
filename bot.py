import os
import time
import telebot

from datetime import datetime
from imgurpython import ImgurClient
from telegraph import Telegraph
from telebot import types

# Telegram Bot token
TOKEN = '653777058:AAHYrdn_E-DIpiNVDCqj8GiNLz3DRBpR940'

# Client data for Imgur API
CLIENT_ID = '86926d4a8343376'
CLIENT_SECRET = 'c819082ba48bb40eb3c5906bdbe6239f08d0c1d8'


client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
bot = telebot.TeleBot(TOKEN, threaded=False)


def telegram_photo_download(msg):
    """
    Download photo from telegram message
    Return file name
    """
    file_name = '{}.jpg'.format(int(time.time() * 1000))
    file_info = bot.get_file(msg.photo[2].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    return file_name


def create_page(msg, content):
    """
    Create telegraph page
    Return URL of this page
    """
    telegraph = Telegraph()
    telegraph.create_account(short_name=str(msg.chat.id))
    response = telegraph.create_page(
        str(datetime.now())[:16],
        html_content=str(content),
        author_name=str(msg.chat.username)
    )
    return response['url']


@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    """
    Start and help commands handler. Send help message
    """
    markup = types.ReplyKeyboardMarkup()
    markup.row('Create Page!')
    markup.row('/help')
    markup.resize_keyboard = True

    bot.send_message(message.chat.id, 'For creating your telegra.ph page, you need to send message here and press '
                                      'button "Create Page!".\nAs a result you will get URL of your page.\n'
                                      'Reserved words: "Create Page!". Use them in []', reply_markup=markup)


@bot.message_handler(regexp="(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]|\(([^\s()<>]+|(\("
                            "[^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?\xab"
                            "\xbb\u201c\u201d\u2018\u2019])")
def handle_url(message):
    """
    URL handler. Add link into our page
    """
    tmp_file = open('{0}tmp.txt'.format(message.from_user.id), 'a')
    if not message.forward_from:
        tmp_file.write('<p><a href="{0}">{0}</a></p>\n'.format(message.text))
    else:
        tmp_file.write('<p><a href="{0}">{0} sent from -> {1}</a></p>\n'.format(message.text,
                                                                                message.forward_from.username))
    tmp_file.close()


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """
    Text message handler. Write them into tmp file and create page from it
    """
    tmp_file = open('{0}tmp.txt'.format(message.from_user.id), 'a+')
    if message.text != 'Create Page!':
        if message.text != '[Create Page!]':

            if not message.forward_from:
                msg_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message.date))
                tmp_file.write('<p><b>@{0} {2}</b></p>\n<p>{1}</p><hr></hr>\n'.format(message.chat.username,
                                                                                      message.text.encode('utf8'),
                                                                                      msg_date))
            else:
                forward_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message.forward_date))
                tmp_file.write('<p><b>@{0} {2}</b></p>\n<p>{1}</p><hr></hr>\n'.format(message.forward_from.username,
                                                                                      message.text.encode('utf8'),
                                                                                      forward_date))
        else:
            tmp_file.write('<p>Create Page!</p>\n')
    else:
        tmp_file = open('{0}tmp.txt'.format(message.from_user.id), 'r+')
        if os.path.getsize('{0}tmp.txt'.format(message.from_user.id)) > 0:
            text = tmp_file.read()[:-9]
            page_url = create_page(message, text)
            bot.send_message(message.chat.id, page_url)
            tmp_file.close()
            os.remove('{0}tmp.txt'.format(message.from_user.id))
        else:
            bot.send_message(message.chat.id, "ERROR: You are creating an empty page!")
    tmp_file.close()


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(15)
