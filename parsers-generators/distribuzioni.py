#!/usr/bin/python
#alfa e' la soglia che determina se tra due nodi c'e' un almeno un flusso
#p e' la soglia che determina se c'e' piu' di un flusso tra X E Y, segue una distribuzione geometrica



import random
import numpy as np

alfa = 0.7                          # mettere alfa a 0.7 per avere circa 300 flussi
n_medio_flussi_multipli = 3         # nemero medio di flussi multipli
capacita_media = 5



def add_multiple_flows(s, flow_catalogue, src, dst, count, out_file):	                        # e' il modello che carica i flussi multipli
		
	for k in range(0,s):
		count = count +1 	
		out_file.write("il flusso "+str(count)+" ["+str(src)+", "+str(dst)+"]\n")
		flow_catalogue[count]=(src,dst,{'out':{'size': capacita_flusso_mod_esp(), 'allocated': False, 'srcPort': '', 'dstPort':''}})

	return flow_catalogue
	
def capacita_flusso_mod_esp():
	cap_media=10
	a=int(random.expovariate(1/float(capacita_media)))             # la capacita' dei flussi segue un modello esponenziale limitato tra 1 e 10
	if a < 1:						 					
		a = 1
	if a > 10:                            		
		a = 10                         
	return a 

def capacita_flusso_mod_unif():
	cap_media=10
	cap_min=5
	cap_max=(2*cap_media)-cap_min
	a=int(random.uniform(cap_min,cap_max))
	return a

def generatore_pr_alfa():
	alfa=random.random()
	return alfa

def build_flows(nx_links,out_file):
	
	random.seed(10)	                      #rende ripetibili le prove 
	np.random.seed(10)                    #rende ripetibile la distribuzione geometrica che usa la libreria numpy
	flow_catalogue = {}
	count = 0
	flow=0
	
	
	nx_links_copy=nx_links.copy()
	
	for edge in nx_links.edges_iter(data=True):
		if edge[2]['type'] == 'bordo-core' :
			for edge1 in nx_links_copy.edges_iter(data=True):
				if edge1[2]['type'] == 'bordo-core' and edge[0] != edge1[0] :
					pr_alfa=generatore_pr_alfa()
					if pr_alfa < alfa:
						size = capacita_flusso_mod_esp()
						out_file.write("il flusso "+str(count)+" ["+str(edge[0])+", "+str(edge1[0])+"] \n")
						#size = capacita_flusso_mod_unif()
						flow_catalogue[count]=(edge[0],edge1[0],{'out':{'size': size, 'allocated': False, 'srcPort': '', 'dstPort':'', "path": [], "type": "vll"}})
						s = np.random.geometric((1/float(n_medio_flussi_multipli)))                                        # s e' il numero dei flussi multipli, segue una distribuzione geometrica
						flow_catalogue=add_multiple_flows(s, flow_catalogue, edge[0], edge1[0], count, out_file)           # carica i flussi multipli
						count=len(flow_catalogue)
						
					
	print "flow_catalogue prob"
	print flow_catalogue
	print"#########################################"
	return flow_catalogue		

