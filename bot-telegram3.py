#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.
# This program is dedicated to the public domain under the CC0 license.
"""
import text
import logging
import sqlite3 as lite
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from emoji import emojize

TOKEN = '460707674:AAE5OGTYTjE0m27Uy9yiscSp3B0eiRF5s4M'

userDict = {}
con =  None

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def connectDB():
	try:
		con = lite.connect('databases/data1.db')
		return con
	except lite.Error, e:
		print "Error %s:" % e.args[0]
		
def start(bot, update):
	userDict[update.message.chat.id]="start"
	print("**** start userDict *****")
	print(userDict)
	print("**** start userDict *****")
	keyboard = [[InlineKeyboardButton("Guardar en BBDD"+emojize(":kissing_closed_eyes:", use_aliases=True), callback_data='WBBDD'),
				 InlineKeyboardButton("Llegir de BBDD", callback_data='RBBDD')],
				  [InlineKeyboardButton("Recuperar text", callback_data='TXT')]
				 ]
	reply_markup = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('Triï una opció:', reply_markup=reply_markup)


def button(bot, update):
	query = update.callback_query
	userDict[query.from_user.id]=query.data
	print("**** button userDict *****")
	print(userDict)
	print("**** button userDict *****")
	#bot.edit_message_text(text="Selected option: {}".format(query.data),
	#					  chat_id=query.message.chat_id,
	#					  message_id=query.message.message_id)
	if query.data=='WBBDD':
		keyboard = [[InlineKeyboardButton("Taula A"+emojize(":kissing_closed_eyes:", use_aliases=True), callback_data='WTA'),
				 InlineKeyboardButton("Taula B", callback_data='WTB')], 
				 [InlineKeyboardButton("Enrera", callback_data='BACK')]]
				 
		reply_markup = InlineKeyboardMarkup(keyboard)
		query.message.reply_text('Triï una taula:', reply_markup=reply_markup)
	elif query.data=='WTA':
		query.message.reply_text("Introdueixi un valor enter:")
	elif query.data=='WTB':
		query.message.reply_text("Introdueixi un text:")
	elif query.data=="BACK":
		start(bot, query)

	elif query.data=="TXT":
		bot.send_message(chat_id=query.message.chat_id,
						text="*"+text.t1+"*",
						 parse_mode=telegram.ParseMode.MARKDOWN)
		bot.send_message(chat_id=query.message.chat_id,
						text="_"+text.t2+"_",
						 parse_mode=telegram.ParseMode.MARKDOWN)
		start(bot, query)
	else:
		pass

		
def other(bot, update):
	print("**** other userDict *****")
	print(userDict[update.message.from_user.id])
	print("**** other userDict *****")
	if userDict[update.message.from_user.id]=="WTA":
		#bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
		#update.message.reply_text("Other")
		try:
			x = int(update.message.text)
			con = connectDB()
			cur = con.cursor()
			with con:
				cur = con.cursor()    
				cur.execute("INSERT INTO taulaInt VALUES("+update.message.text+");")
			con.close()
			update.message.reply_text("Valor introduït correctament")
		except:
			update.message.reply_text("Valor no enter")
		finally:
			start(bot, update)	
	
	if userDict[update.message.from_user.id]=="WTB":
		#bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
		#update.message.reply_text("Other")
		try:
			con = connectDB()
			cur = con.cursor()
			with con:
				cur = con.cursor()    
				cur.execute("INSERT INTO taulaStr VALUES('"+update.message.text+"');")
			con.close()
			update.message.reply_text("Valor introduït correctament")
		except:
			update.message.reply_text("Valor no introduit correctament")
		finally:
			start(bot, update)	

def error(bot, update, error):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, error)


def main():
	#print(text.t1)
	connectDB()
	updater = Updater(TOKEN)
	bot = telegram.Bot(TOKEN)
	# Create the Updater and pass it your bot's token.

	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(CallbackQueryHandler(button))
	# text normal
	updater.dispatcher.add_handler(MessageHandler(Filters.text, other))
	updater.dispatcher.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT
	updater.idle()


if __name__ == '__main__':
	main()
