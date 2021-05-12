#!/usr/bin/env python
# -*- coding: utf-8 -*-

import text
import logging
import math
import matplotlib.pyplot as plt
import sqlite3 as lite
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from pathlib import Path

#from emoji import emojize

TOKEN = '460707674:AAE5OGTYTjE0m27Uy9yiscSp3B0eiRF5s4M'

partits = ['ERC','PDCat','PP','Cs','PSC','Cup','Comuns','Vots en blanc','Vots nuls']
partitsDict = {'ERC':'orange','PDCat':'darkblue','PP':'blue','Cs':'darkorange','PSC':'red','Cup':'yellow','Comuns':'purple','Vots en blanc':'white','Vots nuls':'silver'}
meses = {1:{1:['A','B'],2:['A','B'],3:['A','B'],4:['A','B'],5:['A','B']},2:{1:['A','B'],2:['A','B'],3:['A','B'],4:['A','B'],5:['A','B'],6:['A','B'],7:['A','B']},3:{1:['A','B'],2:['U'],3:['A','B'],4:['A','B'],5:['A','B'],6:['A','B'],7:['A','B'],8:['A','B'],9:['A','B'],10:['A','B'],11:['U'],12:['U'],13:['U']},4:{1:['U'],2:['A','B'],3:['A','B'],4:['U'],5:['A','B'],6:['U']},5:{1:['A','B'],2:['A','B'],3:['A','B'],4:['A','B'],5:['A','B'],6:['A','B'],7:['A','B'],8:['A','B'],9:['U']}}
mesesTotals=72
userDict = {0:{"step":"", "laststep":"","districte":"","seccio":"","mesa":"","partit":0, "initialStep":"", "chatid":0}}


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Connecta a BBDD
"""
def connectDB():
	try:
		con = lite.connect('databases/eleccions.db')
		return con
	except lite.Error, e:
		print "Error %s:" % e.args[0]

"""
Valos pie % vots
"""
def autopct_percent(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

"""
Valos pie escons
"""
def autopct_number(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:d}'.format(p=pct,v=val)
    return my_autopct


	
"""
Valos pie % vots
"""
import matplotlib.pyplot as plt
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

		
"""
Genera gràfic escons
"""
def generaGraficEscons(labels,values, colors):
	fig1, ax1 = plt.subplots()
	ax1.pie(values,  autopct=autopct_number(values),
			startangle=90, colors=colors)
	ax1.axis('equal')  
	plt.title('Escons')
	plt.tight_layout()
	ax1.legend(labels,loc='center right')
	fig1.savefig('images/escons.png')   
	plt.close(fig1)  



"""
Genera gràfic vots
"""
def generaGraficVots(labels,values, colors,name):
	fig1, ax1 = plt.subplots()
	ax1.pie(values,  autopct=autopct_percent(values),
			startangle=90, colors=colors)
	ax1.axis('equal')  
	plt.title('Vots i % de vots')
	plt.tight_layout()
	ax1.legend(labels,loc='center right')
	fig1.savefig('images/vots_'+name+'.png')   
	plt.close(fig1)  

"""
Gràfics vots
"""		
def generarGraficVots(select,name,con):
	cur = con.cursor()
	cur.execute(select)
	rows = cur.fetchall()
	partits = []
	vots =[]
	colors = []
	for row in rows:
		partits.append(row[0])
		vots.append(int(row[1]))
		colors.append(partitsDict[row[0]])
	generaGraficVots(partits,vots, colors,name)


	
"""
Genera gràfic següent escó
"""
def generaGraficSeguentEsco(labels, values):
	fig2, ax2 = plt.subplots()
	pos = range(len(labels))
	ax2.barh(pos,values,ecolor='r', align='center', label=labels)
	plt.yticks(pos, labels)
	title ='Vots per al seguent esco'
	plt.title(title)
	for i, v in enumerate(values):
		ax2.text( 7 if v-7<=7 else v-7, i , str(v), color='black', fontweight='bold')
	fig2.savefig('images/seguent_esco.png')   
	plt.close(fig2)  


		
"""
Calcula els vots necessaris per obtenir un nou escó
"""
def votsNouEsco(resultats, votsUltimEsco, totalVots5per, partitUltimEsco,escons,res):
	esconsDict = {}		
	for x in resultats:
		esconsCnt = escons.count(x[0])
		if(x[0]!='Vots en blanc' ): 
			esconsDict[x[0]]=[escons.count(x[0]),0,0]
			#print(x[0]+"-"+str(esconsCnt ))

	for i in reversed(range(25,len(res))):
		if(res[i][0]!='Vots en blanc'):
			esconsFinal=esconsDict[res[i][0]][0]
			more5 = math.floor(((votsUltimEsco-res[i][4])*(esconsFinal+1))+1)
			less5 = math.floor(((totalVots5per-res[i][1])/0.95)+1)
			esconsDict[res[i][0]][1]=int(round(0 if res[i][0]==partitUltimEsco else more5 if more5>less5 else less5,0))
			esconsDict[res[i][0]][2]=(1 if res[i][0]==partitUltimEsco else 0)
	return esconsDict

"""
Insert taula escons
"""
def taulaEscons(con,esconsDict):
	statementDel="delete from escons;"	
	statementIns = "insert into escons "
	for x in esconsDict.keys():
		statementIns+=" select 'actual', '"+x+"',"+str(esconsDict[x][0])+","+str(esconsDict[x][1])+","+str(esconsDict[x][2])+" union all"
	with con:
		cur = con.cursor()
		cur.execute(statementDel)
		cur.execute(statementIns[:-9]+";")

"""
Calcula escons per la llei d'Hondt i també el cost d'obtenir un nou escó
"""		
def lleiHondt(resultats, con):
	res = []
	totalVots = 0
	partitUltimEsco=""
	votsUltimEsco = 0
	for x in resultats:
		totalVots+=x[1]
	totalVots5per = (totalVots*1.0)*0.05
		
	for i in range(1,26):
		for x in resultats:
			if x[1]>totalVots5per and x[0]!='Vots en blanc':
				votsComputables = x[1]/(i*1.0)
			else: 
				votsComputables = 0
			res.append((x[0],x[1],i,votsComputables,x[1]/(i*1.0)))
	res =sorted(res, key = lambda a:a[3]*10000000+a[1], reverse=True )
	escons = []
	for i in range(25):
		escons.append(res[i][0])
		if i == 24:
			partitUltimEsco = res[i][0]
			votsUltimEsco = res[i][1]/ (escons.count(res[i][0])*1.0)
	
	esconsDict = votsNouEsco(resultats, votsUltimEsco, totalVots5per, partitUltimEsco, escons,res)
	colors = []
	escons = []
	partitsAmbEscons =[]
	votsSeguentEsco = []
	for x in esconsDict.keys():
		if esconsDict[x][0]>0:
			colors.append(partitsDict[x])
			escons.append(esconsDict[x][0])
			partitsAmbEscons.append(x)
		votsSeguentEsco.append(esconsDict[x][1])
	generaGraficEscons(partitsAmbEscons,escons, colors)
	generaGraficSeguentEsco(esconsDict.keys(),votsSeguentEsco)
	taulaEscons(con,esconsDict)
	
		
"""
Retorna una llista amb els vots per partit
"""				
def muntarResultats(con):
	res = []
	query =" select partit, sum(u.vots) as vots from ultimsResultatsMesa u where partit not in ('Vots nuls') group by partit ;"
	con = connectDB()
	cur = con.cursor()
	cur.execute(query)
	rows = cur.fetchall()
	resultats = ""
	for row in rows:
		res.append ((row[0],row[1]))
	return res
	
"""
Munta where per mostrar resultats
"""
def muntarWhereMostrarDades(districte, seccio, mesa):
	where = "where 1=1 "
	if not (districte is None):
		where = where +"and districte ='"+str(districte)+"' "
		if not(seccio is None):
			where = where + " and seccio='"+str(seccio)+"' "
			if not(mesa is None):
				where = where + " and mesa='"+str(mesa)+"' "
	return where

"""
Munta la capçalera per mostrar resultats
"""
def muntarCapcaleraMostrarDades(districte, seccio, mesa,cur):
	resultatsHead = ""
	if not (districte is None):
		resultatsHead = "Resultats Districte: "+str(districte)+" - "
		if not(seccio is None):
			resultatsHead = resultatsHead+"Secció: "+str(seccio)+" - "
			if not(mesa is None):
				resultatsHead = resultatsHead+"Mesa: "+str(mesa)+"\r\n"
			else:
				resultatsHead = resultatsHead+"Totes les meses\r\n"
		else:
			resultatsHead = resultatsHead+"Totes les seccions\r\n"
		resultatsHead='*'+resultatsHead+'*'
	else:
		query="select count(distinct districte ||'-'||seccio||'-'|| mesa) from ultimsREsultatsmesa where eleccio='actual';"
		cur.execute(query)
		rows = cur.fetchall()
		for row in rows:
			resultatsHead = "*Resultats globals*\r\nIntroduïdes "+str(row[0])+" meses de "+str(mesesTotals)+"\r\n"
	return resultatsHead

"""
Munta els resultats dels partits
"""
def muntarResultatsPartitsMostrarDades(where,cur,districte):
	query =" select u.partit, sum(u.vots) as vots, round(sum(u.vots)/cast(a.vots as real)*100,2) as per_vots, ifnull(e.escons,0) as escons from ultimsResultatsMEsa u left join escons e on u.partit=e.partit, (select sum(vots) as vots from ultimsResultatsMesa "+where + " and partit not  in ('Vots nuls'))a " + where +" and u.partit not  in ('Vots nuls') group by u.partit,a.vots,ifnull(e.escons,0) order by 2 desc;"
	cur.execute(query)
	rows = cur.fetchall()
	resultats = ""
	res =""
	for row in rows:
		escons =""
		if districte is None:
			a =(" Escons" if row[3]!=1 else " Escó")
			escons=" - "+str(row[3]).encode('utf-8')+a

		resultats = resultats +"_"+ row[0].encode('utf-8')+"_: "+str(row[1]).encode('utf-8')+" vots - "+str(row[2]).encode('utf-8')+"%"+escons+"\r\n"
	return resultats

"""
Munta els resultats dels vots globals
"""
def muntarResultatsVotsGlobalsMostrarDades(where,cur,resultatsIni):
	resultats = resultatsIni	
	if resultats =="":
		resultats = "_Sense resultats_"
	else:
		query =" select sum(u.vots) as votsNuls, a.vots as VotsTotals, a.vots-sum(u.vots) as VotsValids, 100-round(sum(u.vots)/cast(a.vots as real)*100,2) as per_vots, b.cens, case when b.cens>0 then 100-round(cast(a.vots as real)/b.cens*100,2) else 0.00 end as per_cens from ultimsResultatsMEsa u, (select sum(vots) as vots from ultimsResultatsMesa "+where + ")a, (select sum(cens) as cens from ultimCensMesa "+where + ")b  " + where +" and partit in ('Vots nuls') group by a.vots, b.cens ;"
		cur.execute(query)
		rows = cur.fetchall()
		for row in rows:
			resultats = "Cens: "+ str(row[4]).encode('utf-8')+"\r\nVots totals: " + str(row[1]).encode('utf-8')+"\r\n%Participació: "+ str(row[5]).encode('utf-8')+"%\r\nVots vàlids: "+str(row[2]).encode('utf-8')+"\r\nVots nuls: "+str(row[0]).encode('utf-8')+"\r\n% Vots vàlids: "+str(row[3]).encode('utf-8')+"%\r\n\r\n" + resultats
	return resultats

"""
Mostra les dades dels resultats
"""
def mostrarDades(bot, chat_id, districte, seccio, mesa):
	con = connectDB()
	cur = con.cursor()
	where = muntarWhereMostrarDades(districte, seccio, mesa)
	resultatsHead = muntarCapcaleraMostrarDades(districte, seccio, mesa,cur)
	resultats = muntarResultatsPartitsMostrarDades(where,cur,districte)
	resultatsVotsPartits = muntarResultatsVotsGlobalsMostrarDades(where,cur,resultats)
	bot.send_message(chat_id,text=resultatsHead+resultatsVotsPartits, parse_mode=telegram.ParseMode.MARKDOWN)
	if districte is None:
		bot.send_photo(chat_id=chat_id, photo=open('images/escons.png', 'rb'))
		bot.send_photo(chat_id=chat_id, photo=open('images/seguent_esco.png', 'rb'))
		bot.send_photo(chat_id=chat_id, photo=open('images/vots_.png', 'rb'))
	elif seccio is None:
		my_file = Path('images/vots_D'+str(districte)+'.png')
		if not my_file.is_file():
			#select districte
			selectDistricte =" select partit, sum(u.vots) as vots from ultimsResultatsMesa u where partit not in ('Vots nuls') and eleccio='actual' and districte='"+str(districte)+"' group by partit ;"	
			generarGraficVots(selectDistricte,'D'+str(districte),con)
		bot.send_photo(chat_id=chat_id, photo=open('images/vots_D'+str(districte)+'.png', 'rb'))
	elif mesa is None:
		my_file = Path('images/vots_D'+str(districte)+'_S'+str(seccio)+'.png')
		if not my_file.is_file():
			#select secció
			selectSeccio =" select partit, sum(u.vots) as vots from ultimsResultatsMesa u where partit not in ('Vots nuls') and eleccio='actual' and districte='"+str(districte)+"' and  seccio='"+str(seccio)+"' group by partit ;"
			generarGraficVots(selectSeccio,'D'+str(districte)+'_S'+str(seccio),con)
		bot.send_photo(chat_id=chat_id, photo=open('images/vots_D'+str(districte)+'_S'+str(seccio)+'.png', 'rb'))
	else:
		my_file = Path('images/vots_D'+str(districte)+'_S'+str(seccio)+'_M'+str(mesa)+'.png')
		if not my_file.is_file():
			#select mesa
			selectMesa =" select partit, sum(u.vots) as vots from ultimsResultatsMesa u where partit not in ('Vots nuls') and eleccio='actual' and districte='"+str(districte)+"' and  seccio='"+str(seccio)+"' and mesa='"+str(mesa)+"' group by partit ;"
			generarGraficVots(selectMesa,'D'+str(districte)+'_S'+str(seccio)+'_M'+str(mesa),con)
		bot.send_photo(chat_id=chat_id, photo=open('images/vots_D'+str(districte)+'_S'+str(seccio)+'_M'+str(mesa)+'.png', 'rb'))
	con.close()
	return
	

"""
Selecció de districtes 
"""	
def seleccionarDistricte(query):
	userDict[query.from_user.id]["initialStep"]=query.data
	#print(userDict[query.from_user.id]["initialStep"])
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
Selecció de seccions 
"""		
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
		
"""
Selecció de meses
"""				
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
	
"""
Amb la mesa seleccinada es mostren les dades o bé es fa la crida a introduir dades dels partits
"""			
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
		#esborrar de la taula auxiliar
		statementDel="delete from  resultatsMesaAux where eleccio='actual' and districte='"+str(userDict[query.from_user.id]["districte"])+"' and seccio='"+str(userDict[query.from_user.id]["seccio"])+"' and mesa='"+str(userDict[query.from_user.id]["mesa"])+"';"
		con = connectDB()
		with con:
			cur = con.cursor()
			cur.execute(statementDel)
		con.close()
		bot.send_message(chat_id=query.message.chat_id,	text="Introdueixi el nombre de vots del partit: *"+partits[0]+"*", parse_mode=telegram.ParseMode.MARKDOWN)
	elif userDict[query.from_user.id]["initialStep"]=='ICEN':
		bot.send_message(chat_id=query.message.chat_id,	text="Introdueixi el cens del *Districte: "+userDict[query.from_user.id]["districte"].encode('utf-8')+", Secció: "+userDict[query.from_user.id]["seccio"].encode('utf-8') +", Mesa: "+userDict[query.from_user.id]["mesa"].encode('utf-8')+"*", parse_mode=telegram.ParseMode.MARKDOWN)		


		
"""
Insert resultats mesa
"""
def insertResultatsMesa(userId, con):
	statement="INSERT INTO resultatsMesa select eleccio, partit, districte, seccio, mesa, vots, personaIns, dataIns from resultatsMesaAux where eleccio='actual' and districte='"+str(userDict[userId]["districte"])+"' and  seccio='"+str(userDict[userId]["seccio"])+"' and mesa='"+str(userDict[userId]["mesa"])+"';" ;
	
	statementDel="delete from  ultimsResultatsMesa where eleccio='actual' and districte='"+str(userDict[userId]["districte"])+"' and seccio='"+str(userDict[userId]["seccio"])+"' and mesa='"+str(userDict[userId]["mesa"])+"';"

	statementIns="INSERT INTO ultimsResultatsMesa select eleccio, partit, districte, seccio, mesa, vots from resultatsMesaAux where eleccio='actual' and districte='"+str(userDict[userId]["districte"])+"' and  seccio='"+str(userDict[userId]["seccio"])+"' and mesa='"+str(userDict[userId]["mesa"])+"';" ;
	
	statementDelAux="delete from  resultatsMesaAux where eleccio='actual' and districte='"+str(userDict[userId]["districte"])+"' and seccio='"+str(userDict[userId]["seccio"])+"' and mesa='"+str(userDict[userId]["mesa"])+"';"

	with con:
		cur = con.cursor()
		cur.execute(statement)
		cur.execute(statementDel)
		cur.execute(statementIns)
		cur.execute(statementDelAux)
		
	#select mesa
	selectMesa =" select partit, sum(u.vots) as vots from ultimsResultatsMesa u where partit not in ('Vots nuls') and eleccio='actual' and districte='"+str(userDict[userId]["districte"])+"' and  seccio='"+str(userDict[userId]["seccio"])+"' and mesa='"+str(userDict[userId]["mesa"])+"' group by partit ;"
	generarGraficVots(selectMesa,'D'+str(userDict[userId]["districte"])+'_S'+str(userDict[userId]["seccio"])+'_M'+str(userDict[userId]["mesa"]),con)
	#select secció
	selectSeccio =" select partit, sum(u.vots) as vots from ultimsResultatsMesa u where partit not in ('Vots nuls') and eleccio='actual' and districte='"+str(userDict[userId]["districte"])+"' and  seccio='"+str(userDict[userId]["seccio"])+"' group by partit ;"
	generarGraficVots(selectSeccio,'D'+str(userDict[userId]["districte"])+'_S'+str(userDict[userId]["seccio"]),con)
	#select districte
	selectDistricte =" select partit, sum(u.vots) as vots from ultimsResultatsMesa u where partit not in ('Vots nuls') and eleccio='actual' and districte='"+str(userDict[userId]["districte"])+"' group by partit ;"	
	generarGraficVots(selectDistricte,'D'+str(userDict[userId]["districte"]),con)
	#select total
	selectTotal =" select partit, sum(u.vots) as vots from ultimsResultatsMesa u where partit not in ('Vots nuls') and eleccio='actual' group by partit ;"	
	generarGraficVots(selectTotal,'',con)
	
	
"""
Log Errors caused by Updates.
"""
def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"', update, error)
	#si falla alguna cosa tornem a l'inici
	start(bot, update)


"""
Start 
"""	
def start(bot, update):
	userDict[update.message.chat.id]={"step":"Start","chatid":update.message.chat_id}
	#print("**** start userDict *****")
	#print(userDict)
	#print("**** start userDict *****")
	keyboard = [[InlineKeyboardButton("Introduir resultats", callback_data='IRES'),
				 InlineKeyboardButton("Consultar resultats", callback_data='CRES')],[InlineKeyboardButton("Introduir cens", callback_data='ICEN')]]
	reply_markup = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('Trieu una opció:',reply_markup=reply_markup)	

	
"""
Accions amb els inline buttons
"""
def button(bot, update):
	query = update.callback_query
	userDict[query.from_user.id]["step"]=query.data
	#print("**** button userDict *****")
	#print(userDict)
	#print("**** button userDict *****")
	#introduir/llegir resultats
	if query.data=='IRES' or query.data=='CRES' or query.data=='ICEN':
		seleccionarDistricte(query)
	#districte seleccionat
	elif query.data[0:2]=="D_":
		seleccionarSeccio(query, bot)
	#secció seleccionada
	elif query.data[0:2]=="S_":
		seleccionarMesa(query, bot)
	#mesa seleccionada
	elif query.data[0:2]=="T_":
		mesaSeleccionada(query, bot)
	elif query.data=="BACK":
		update.callback_query.data = userDict[query.from_user.id]["laststep"]
		button(bot, update)
	else:
		start(bot, query)	
	return
	
"""
Accions amb el text escrit
"""	
def other(bot, update):
	#print("**** other userDict *****")
	#print(userDict[update.message.from_user.id])
	#print("**** other userDict *****")
	#mirar si és IRES o ICEN
	if userDict[update.message.from_user.id]["initialStep"]=='IRES':	
		if userDict[update.message.from_user.id]["step"][0:2]=="T_":
			try:
				x = int(update.message.text)
				#guardar el valor a bbdd
				statementIns="INSERT INTO resultatsMesaAux select 'actual', '"+str(partits[userDict[update.message.from_user.id]["partit"]])+"', '"+str(userDict[update.message.from_user.id]["districte"])+"', '"+str(userDict[update.message.from_user.id]["seccio"])+"', '"+str(userDict[update.message.from_user.id]["mesa"])+"', '"+str(x)+"','"+str(update.message.from_user.id)+"_"+update.message.from_user.first_name+"', datetime('now') ;"
				con = connectDB()
				with con:
					cur = con.cursor()
					cur.execute(statementIns)
				con.close()
				update.message.reply_text("Valor introduït correctament")
				if userDict[update.message.from_user.id]["partit"]<len(partits)-1:	
					userDict[update.message.from_user.id]["partit"]=userDict[update.message.from_user.id]["partit"]+1
					bot.send_message(chat_id=update.message.chat_id,	text="Introdueixi el nombre de vots del partit: *"+partits[userDict[update.message.from_user.id]["partit"]]+"*", parse_mode=telegram.ParseMode.MARKDOWN)
				else: 
					con = connectDB()				
					insertResultatsMesa(update.message.from_user.id,con)				
					bot.send_message(chat_id=update.message.chat_id,	text="*Tots els valors introduïts correctament. Districte: "+str(userDict[update.message.from_user.id]["districte"])+" - Secció: "+str(userDict[update.message.from_user.id]["seccio"])+" - Mesa: "+str(userDict[update.message.from_user.id]["mesa"])+"*", parse_mode=telegram.ParseMode.MARKDOWN)
					res = muntarResultats(con)
					lleiHondt(res,con)
			
					con.close()
					start(bot, update)
			except ValueError, TypeError:
				bot.send_message(chat_id=update.message.chat_id,	text="*Ha d'introduir un número enter.* \r\n Introdueixi el nombre de vots del partit: *"+partits[userDict[update.message.from_user.id]["partit"]]+"*", parse_mode=telegram.ParseMode.MARKDOWN)
			except lite.Error ,e :
				update.message.reply_text("Error de BBDD")
				print "Error %s:" % e.args[0]
	
		else:
			start(bot, update)
	elif userDict[update.message.from_user.id]["initialStep"]=='ICEN':
		try:
			x = int(update.message.text)
			statementIns="INSERT INTO censMesa select 'actual', '"+str(userDict[update.message.from_user.id]["districte"])+"', '"+str(userDict[update.message.from_user.id]["seccio"])+"', '"+str(userDict[update.message.from_user.id]["mesa"])+"', "+str(x)+",'"+str(update.message.from_user.id)+"_"+update.message.from_user.first_name+"', datetime('now') ;"
			statementDel="Delete from ultimCensMesa where eleccio='actual' and districte='"+str(userDict[update.message.from_user.id]["districte"])+"' and  seccio='"+str(userDict[update.message.from_user.id]["seccio"])+"' and  mesa='"+str(userDict[update.message.from_user.id]["mesa"])+"';"
			statementInsUltim="INSERT INTO ultimCensMesa select 'actual', '"+str(userDict[update.message.from_user.id]["districte"])+"', '"+str(userDict[update.message.from_user.id]["seccio"])+"', '"+str(userDict[update.message.from_user.id]["mesa"])+"', "+str(x)+";"
			con = connectDB()
			with con:
				cur = con.cursor()
				cur.execute(statementIns)
				cur.execute(statementDel)
				cur.execute(statementInsUltim)
			con.close()
			bot.send_message(chat_id=update.message.chat_id,	text="*Valor del cens introduït correctament. Districte: "+str(userDict[update.message.from_user.id]["districte"])+" - Secció: "+str(userDict[update.message.from_user.id]["seccio"])+" - Mesa: "+str(userDict[update.message.from_user.id]["mesa"])+"*", parse_mode=telegram.ParseMode.MARKDOWN)
			start(bot, update)
		except ValueError, TypeError:
			bot.send_message(chat_id=update.message.chat_id, text="*Ha d'introduir un número enter.*\r\nIntrodueixi el cens del *Districte: "+userDict[update.message.from_user.id]["districte"]+", Secció: "+userDict[update.message.from_user.id]["seccio"] +", Mesa: "+userDict[update.message.from_user.id]["mesa"]+"*", parse_mode=telegram.ParseMode.MARKDOWN)
		except lite.Error ,e :
			update.message.reply_text("Error de BBDD")
			print "Error %s:" % e.args[0]	
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
