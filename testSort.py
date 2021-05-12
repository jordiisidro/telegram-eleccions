#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3 as lite
import math
resultats = [('comuns', 100), ('cup' , 500), ('pp', 45), ('erc', 300), ('Vots en blanc', 50)]

def connectDB():
	pass
	"""
	try:
		con = lite.connect('databases/eleccions.db')
		return con
	except lite.Error, e:
		print "Error %s:" % e.args[0]
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
			if x[1]>totalVots5per and x[0]<>'Vots en blanc':
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
			
	#for i in res:
	#	print i
	"""	
	statementDel="delete from escons;"
	
	with con:
		cur = con.cursor()
		cur.execute(statementDel)
	"""
	esconsDict = {}
	for x in resultats:
		esconsCnt = escons.count(x[0])
		if(x[0]<>'Vots en blanc' and esconsCnt>0):
			esconsDict[x[0]]=escons.count(x[0])
			print(x[0]+"-"+str(esconsCnt ))
			"""
			statementIns="INSERT INTO escons values ('actual', '"+str(x[0])+"', '"+str(escons.count(x[0]) )+"');"
			with con:
				cur = con.cursor()
				cur.execute(statementIns)
	con.close()
	"""
	
	#càlcul últim escó
	#ultEsc = []
	ultEsc = {}
	for i in reversed(range(25,len(res))):
		#print(len(res))
		if(res[i][0]<>'Vots en blanc'):
			esconsFinal =0
			try:
				esconsFinal=esconsDict[res[i][0]]
			except:
				pass
			more5 = math.floor(((votsUltimEsco-res[i][4])*(esconsFinal+1))+1)
			less5 = math.floor(totalVots5per-res[i][4]+1)
			#ultEsc.append(( res[i][0], more5 if more5>less5 else less5, more5, less5,res[i][4],esconsFinal, votsUltimEsco  ))
			ultEsc[res[i][0]]=[more5 if more5>less5 else less5,0]
	ultEsc[partitUltimEsco][1]=1
	print(ultEsc)
		
	
	
lleiHondt(resultats, connectDB())