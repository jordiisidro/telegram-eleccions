# -*- coding: utf-8 -*-
import telebot
from telebot import types
#git clone https://github.com/eternnoir/pyTelegramBotAPI.git
#cd pyTelegramBotAPI
#python setup.py install
#pip install pyTelegramBotAPI
from emoji import emojize
#https://github.com/carpedm20/emoji
# pip install emoji --upgrade
#https://www.webpagefx.com/tools/emoji-cheat-sheet/
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

TOKEN = '460707674:AAE5OGTYTjE0m27Uy9yiscSp3B0eiRF5s4M'

def listener(mensajes):
    for m in mensajes:
        chat_id = m.chat.id
        texto = m.text
        print('ID: ' + str(chat_id) + ' - MENSAJE: ' + texto)    
 
 
def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu 


bot = telebot.TeleBot(TOKEN)
#print(bot.get_me())
bot.set_update_listener(listener)



# Handle '/start' and '/help'
#@bot.message_handler(commands=['help', 'start'])
#def send_welcome(message):
#    bot.reply_to(message, """\
#Hi there, I am EchoBot.
#I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
#""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    #bot.reply_to(message, message.text)
    bot.reply_to(message, "Hello, world! I am bot."+emojize("yummy :kissing_closed_eyes:", use_aliases=True))
    markup = types.ReplyKeyboardMarkup()
    #markup.add('a', 'v', 'd')
    markup.row(emojize(":kissing_closed_eyes:", use_aliases=True), 'v')
    if message.text=="v":
        markup.row('c', 'd', 'e')
    else:
        markup.row('f', 'g', 'h')
    bot.send_message(message.chat.id, message.text, None, None, markup)
        
@bot.message_handler(commands=['hola'])
def comando_hola(mensaje):
    chat_id = mensaje.chat.id
    bot.send_message(chat_id, 'Te digo Hola desde el UntitBot')

@bot.message_handler(commands=['chao'])
def comando_chao(mensaje):
    chat_id = mensaje.chat.id
    bot.send_message(chat_id, 'Te digo Chao desde el UntitBot')

bot.polling()