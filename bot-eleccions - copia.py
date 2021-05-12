#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.
# This program is dedicated to the public domain under the CC0 license.
"""
import text
import logging
import sqlite3 as lite
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
#from emoji import emojize

TOKEN = '460707674:AAE5OGTYTjE0m27Uy9yiscSp3B0eiRF5s4M'

partits = ['ERC','PDCat','PP','Cs','PSC','Cup','Comuns','Vots en blanc','Vots nuls']
meses = {1:{1:['A','B'],2:['A','B'],3:['A','B'],4:['A','B'],5:['A','B']},2:{1:['A','B'],2:['A','B'],3:['A','B'],4:['A','B'],5:['A','B'],6:['A','B'],7:['A','B']},3:{1:['A','B'],2:['U'],3:['A','B'],4:['A','B'],5:['A','B'],6:['A','B'],7:['A','B'],8:['A','B'],9:['A','B'],10:['A','B'],11:['U'],12:['U'],13:['U']},4:{1:['U'],2:['A','B'],3:['A','B'],4:['U'],5:['A','B'],6:['U']},5:{1:['A','B'],2:['A','B'],3:['A','B'],4:['A','B'],5:['A','B'],6:['A','B'],7:['A','B'],8:['A','B'],9:['U']}}

userDict = {0:{"step":"", "laststep":"","districte":"","seccio":"","mesa":"","partit":0, "initialStep":""}}


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def connectDB():
	try:
		con = lite.connect('databases/eleccions.db')
		return con
	except lite.Error, e:
		print "Error %s:" % e.args[0]


def mostrarDades(bot, chat_id, districte, seccio, mesa):
	where = ""
	resultatsHead = ""
	if not (districte is None):
		where = "where districte ='"+str(districte)+"' "
		resultatsHead = "Resultats Districte: "+str(districte)+" - "
		if not(seccio is None):
			where = where + " and seccio='"+str(seccio)+"' "
			resultatsHead = resultatsHead+"Secció: "+str(seccio)+" - "
			if not(mesa is None):
				where = where + " and mesa='"+str(mesa)+"' "
				resultatsHead = resultatsHead+"Mesa: "+str(mesa)+"\r\n "
			else:
				resultatsHead = resultatsHead+"Totes les meses\r\n"
		else:
			resultatsHead = resultatsHead+"Totes les seccions\r\n"
	else:
		resultatsHead = "Resultats globals\r\n"
	query =" select partit, sum(u.vots) as vots, round(sum(u.vots)/cast(a.vots as real)*100,2) as per_vots from ultimsResultatsMEsa u, (select sum(vots) as vots from ultimsResultatsMesa "+where +")a " + where +" group by partit,a.vots ;"
	con = connectDB()
	cur = con.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	
	resultats = ""
	for row in rows:
		resultats = resultats + row[0]+":"+str(row[1])+" - "+str(row[2])+"%\r\n"
	if resultats =="":
		resultats = "Sense resultats"
	bot.send_message(chat_id,text=resultatsHead+resultats, parse_mode=telegram.ParseMode.MARKDOWN)
	con.close()
	return
	

def introduirLlegirResultatsIni(query):
	userDict[query.from_user.id]["initialStep"]=query.data
	userDict[query.from_user.id]["laststep"]="START"
	keyboard = []
	k = []
	a = 0
	if query.data=='CRES':
		k.append(InlineKeyboardButton("Tots els districtes", callback_data='D_T'))
		a+=1
	
	for i in meses.keys():
		k.append(InlineKeyboardButton("Districte: "+str(i), callback_data='D_'+str(i)))
		if a%2 == 1:
			keyboard.append(k)
			k = []
		a+=1
	k.append(InlineKeyboardButton("Enrera", callback_data='BACK'))
	keyboard.append(k)
	reply_markup = InlineKeyboardMarkup(keyboard,n_cols=2)
	query.message.reply_text('Trieu un districte:', reply_markup=reply_markup)	
	
	
def seleccionarSeccio(query, bot):
	userDict[query.from_user.id]["districte"]=query.data[2]
	userDict[query.from_user.id]["laststep"]=userDict[query.from_user.id]["initialStep"]
	#si D_T --> mostrar dades 
	if query.data=="D_T":
		mostrarDades(bot, query.message.chat_id,None, None, None)
		start(bot, query)
	else:
		keyboard = []
		k = []
		a = 0
		if userDict[query.from_user.id]["initialStep"]=='CRES':
			k.append(InlineKeyboardButton("Totes les seccions", callback_data='S_T'))
			a+=1
		for i in meses[int(query.data[2])].keys():
			k.append(InlineKeyboardButton("Secció: "+str(i), callback_data='S_'+str(i)))
			if a%2 == 1:
				keyboard.append(k)
				k = []
			a+=1
		k.append(InlineKeyboardButton("Enrera", callback_data='BACK'))
		keyboard.append(k)
		reply_markup = InlineKeyboardMarkup(keyboard,n_cols=2)
		query.message.reply_text('Trieu una secció del districte '+query.data[2].encode('utf-8')+":", reply_markup=reply_markup)
		
def seleccionarMesa(query, bot):
	userDict[query.from_user.id]["seccio"]=query.data[2:]
	userDict[query.from_user.id]["laststep"]="D_"+userDict[query.from_user.id]["districte"]
	#si S_T --> mostrar dades
	if query.data=="S_T":
		mostrarDades(bot, query.message.chat_id, userDict[query.from_user.id]["districte"], None, None)
		start(bot, query)
	else:
		keyboard = []
		k = []
		a = 0
		if userDict[query.from_user.id]["initialStep"]=='CRES':
			k.append(InlineKeyboardButton("Totes les meses", callback_data='T_T'))
			a+=1
		for i in meses[int(userDict[query.from_user.id]["districte"])][int(query.data[2:])]:
			k.append(InlineKeyboardButton("Mesa: "+str(i), callback_data='T_'+str(i)))
			if a%2 == 1:
				keyboard.append(k)
				k = []
			a+=1
		k.append(InlineKeyboardButton("Enrera", callback_data='BACK'))
		keyboard.append(k)
		reply_markup = InlineKeyboardMarkup(keyboard,n_cols=2)
		query.message.reply_text('Trieu una mesa del districte '+userDict[query.from_user.id]["districte"].encode('utf-8')+" i secció  "+query.data[2:].encode('utf-8')+":", reply_markup=reply_markup)
		
def mesaSeleccionada(query, bot):
	userDict[query.from_user.id]["mesa"]=query.data[2]
	userDict[query.from_user.id]["laststep"]="S_"+userDict[query.from_user.id]["seccio"]
	userDict[query.from_user.id]["partit"]=0
	if userDict[query.from_user.id]["initialStep"]=='CRES':
		#si T_T ---> mostrar dades de totes les meses, sinó de només 1 mesa
		if query.data=="T_T":
			mostrarDades(bot, query.message.chat_id,	userDict[query.from_user.id]["districte"], userDict[query.from_user.id]["seccio"], None)
		else:
			mostrarDades(bot, query.message.chat_id,	userDict[query.from_user.id]["districte"], userDict[query.from_user.id]["seccio"], userDict[query.from_user.id]["mesa"])
		start(bot, query)
	elif userDict[query.from_user.id]["initialStep"]=='IRES':
		bot.send_message(chat_id=query.message.chat_id,	text="Introdueixi el nombre de vots del partit: *"+partits[0]+"*", parse_mode=telegram.ParseMode.MARKDOWN)

def error(bot, update, error):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, error)
	#si falla alguna cosa tornem a l'inici
	#start(bot, update)

	
def start(bot, update):
	userDict[update.message.chat.id]={"step":"Start"}
	print("**** start userDict *****")
	print(userDict)
	print("**** start userDict *****")
	keyboard = [[InlineKeyboardButton("Introduir resultats", callback_data='IRES'),
				 InlineKeyboardButton("Consultar resultats", callback_data='CRES')]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('Trieu una opció:',reply_markup=reply_markup)	

	
def button(bot, update):
	query = update.callback_query
	userDict[query.from_user.id]["step"]=query.data
	print("**** button userDict *****")
	print(userDict)
	print("**** button userDict *****")
	#introduir/llegir resultats
	if query.data=='IRES' or query.data=='CRES':
		"""userDict[query.from_user.id]["initialStep"]=query.data
		userDict[query.from_user.id]["laststep"]="START"
		keyboard = []
		k = []
		a = 0
		if query.data=='CRES':
			k.append(InlineKeyboardButton("Tots els districtes", callback_data='D_T'))
			a+=1
		
		for i in meses.keys():
			k.append(InlineKeyboardButton("Districte: "+str(i), callback_data='D_'+str(i)))
			if a%2 == 1:
				keyboard.append(k)
				k = []
			a+=1
		k.append(InlineKeyboardButton("Enrera", callback_data='BACK'))
		keyboard.append(k)
		reply_markup = InlineKeyboardMarkup(keyboard,n_cols=2)
		query.message.reply_text('Trieu un districte:', reply_markup=reply_markup)
		"""
		introduirLlegirResultatsIni(query)
	#districte seleccionat
	elif query.data[0:2]=="D_":
		"""
		userDict[query.from_user.id]["districte"]=query.data[2]
		userDict[query.from_user.id]["laststep"]=userDict[query.from_user.id]["initialStep"]
		#si D_T --> mostrar dades 
		if query.data=="D_T":
			mostrarDades(bot, query.message.chat_id,None, None, None)
			start(bot, query)
		else:
			keyboard = []
			k = []
			a = 0
			if userDict[query.from_user.id]["initialStep"]=='CRES':
				k.append(InlineKeyboardButton("Totes les seccions", callback_data='S_T'))
				a+=1
			for i in meses[int(query.data[2])].keys():
				k.append(InlineKeyboardButton("Secció: "+str(i), callback_data='S_'+str(i)))
				if a%2 == 1:
					keyboard.append(k)
					k = []
				a+=1
			k.append(InlineKeyboardButton("Enrera", callback_data='BACK'))
			keyboard.append(k)
			reply_markup = InlineKeyboardMarkup(keyboard,n_cols=2)
			query.message.reply_text('Trieu una secció del districte '+query.data[2].encode('utf-8')+":", reply_markup=reply_markup)
			"""
		seleccionarSeccio(query, bot)
	#secció seleccionada
	elif query.data[0:2]=="S_":
		"""
		userDict[query.from_user.id]["seccio"]=query.data[2:]
		userDict[query.from_user.id]["laststep"]="D_"+userDict[query.from_user.id]["districte"]
		#si S_T --> mostrar dades
		if query.data=="S_T":
			mostrarDades(bot, query.message.chat_id, userDict[query.from_user.id]["districte"], None, None)
			start(bot, query)
		else:
			keyboard = []
			k = []
			a = 0
			if userDict[query.from_user.id]["initialStep"]=='CRES':
				k.append(InlineKeyboardButton("Totes les meses", callback_data='T_T'))
				a+=1
			for i in meses[int(userDict[query.from_user.id]["districte"])][int(query.data[2:])]:
				k.append(InlineKeyboardButton("Mesa: "+str(i), callback_data='T_'+str(i)))
				if a%2 == 1:
					keyboard.append(k)
					k = []
				a+=1
			k.append(InlineKeyboardButton("Enrera", callback_data='BACK'))
			keyboard.append(k)
			reply_markup = InlineKeyboardMarkup(keyboard,n_cols=2)
			query.message.reply_text('Trieu una mesa del districte '+userDict[query.from_user.id]["districte"].encode('utf-8')+" i secció  "+query.data[2:].encode('utf-8')+":", reply_markup=reply_markup)
		"""
		seleccionarMesa(query, bot)
	#mesa seleccionada
	elif query.data[0:2]=="T_":
		"""
		userDict[query.from_user.id]["mesa"]=query.data[2]
		userDict[query.from_user.id]["laststep"]="S_"+userDict[query.from_user.id]["seccio"]
		userDict[query.from_user.id]["partit"]=0
		if userDict[query.from_user.id]["initialStep"]=='CRES':
			#si T_T ---> mostrar dades de totes les meses, sinó de només 1 mesa
			if query.data=="T_T":
				mostrarDades(bot, query.message.chat_id,	userDict[query.from_user.id]["districte"], userDict[query.from_user.id]["seccio"], None)
			else:
				mostrarDades(bot, query.message.chat_id,	userDict[query.from_user.id]["districte"], userDict[query.from_user.id]["seccio"], userDict[query.from_user.id]["mesa"])
			start(bot, query)
		elif userDict[query.from_user.id]["initialStep"]=='IRES':
			bot.send_message(chat_id=query.message.chat_id,	text="Introdueixi el nombre de vots del partit: *"+partits[0]+"*", parse_mode=telegram.ParseMode.MARKDOWN)
		"""
		mesaSeleccionada(query, bot)
	elif query.data=="BACK":
		print("BACK")
		update.callback_query.data = userDict[query.from_user.id]["laststep"]
		button(bot, update)
	else:
		start(bot, query)	
	return
	
	
def other(bot, update):
	print("**** other userDict *****")
	print(userDict[update.message.from_user.id])
	print("**** other userDict *****")
	if userDict[update.message.from_user.id]["step"][0:2]=="T_":
		try:
			x = int(update.message.text)
			#guardar el valor a bbdd
			statement="INSERT INTO resultatsMesa select 'actual', '"+str(partits[userDict[update.message.from_user.id]["partit"]])+"', '"+str(userDict[update.message.from_user.id]["districte"])+"', '"+str(userDict[update.message.from_user.id]["seccio"])+"', '"+str(userDict[update.message.from_user.id]["mesa"])+"', '"+str(x)+"','"+str(update.message.from_user.id)+"_"+update.message.from_user.first_name+"', datetime('now') ;"
			
			statementDel="delete from  ultimsResultatsMesa where eleccio='actual' and partit='"+str(partits[userDict[update.message.from_user.id]["partit"]])+"' and districte='"+str(userDict[update.message.from_user.id]["districte"])+"' and seccio='"+str(userDict[update.message.from_user.id]["seccio"])+"' and mesa='"+str(userDict[update.message.from_user.id]["mesa"])+"';"
			
			statementIns="INSERT INTO ultimsResultatsMesa select 'actual', '"+str(partits[userDict[update.message.from_user.id]["partit"]])+"', '"+str(userDict[update.message.from_user.id]["districte"])+"', '"+str(userDict[update.message.from_user.id]["seccio"])+"', '"+str(userDict[update.message.from_user.id]["mesa"])+"', '"+str(x)+"';" 
			
			con = connectDB()
			cur = con.cursor()
			with con:
				cur = con.cursor()
				cur.execute(statement)
				cur.execute(statementDel)
				cur.execute(statementIns)
			con.close()
			update.message.reply_text("Valor introduït correctament")
			if userDict[update.message.from_user.id]["partit"]<len(partits)-1:	
				userDict[update.message.from_user.id]["partit"]=userDict[update.message.from_user.id]["partit"]+1
				bot.send_message(chat_id=update.message.chat_id,	text="Introdueixi el nombre de vots del partit: *"+partits[userDict[update.message.from_user.id]["partit"]]+"*", parse_mode=telegram.ParseMode.MARKDOWN)
			else: 
				bot.send_message(chat_id=update.message.chat_id,	text="*Tots els valors introduïts correctament*", parse_mode=telegram.ParseMode.MARKDOWN)
				start(bot, update)
		except ValueError, TypeError:
			bot.send_message(chat_id=update.message.chat_id,	text="*Ha d'introduir un número enter.* \r\n Introdueixi el nombre de vots del partit: *"+partits[userDict[update.message.from_user.id]["partit"]]+"*", parse_mode=telegram.ParseMode.MARKDOWN)
		except lite.Error:
			update.message.reply_text("Error de BBDD")
	else:
		start(bot, update)
	return
			
			
def main():
	updater = Updater(TOKEN)
	
	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(CallbackQueryHandler(button))
	updater.dispatcher.add_handler(MessageHandler(Filters.text, other))
	updater.dispatcher.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT
	updater.idle()


if __name__ == '__main__':
	main()