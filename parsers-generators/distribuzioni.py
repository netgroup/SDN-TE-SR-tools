#!/usr/bin/python
#alfa e' la soglia che determina se tra due nodi c'e' un almeno un flusso
#p e' la soglia che determina se c'e' piu' di un flusso tra X E Y, segue una distribuzione geometrica



import random
import numpy as np

alfa = 0.7                          # mettere alfa a 0.7 per avere circa 300 flussi
n_medio_flussi_multipli = 3         # nemero medio di flussi multipli
perc = 4



def add_multiple_flows(s, flow_catalogue, src, dst, count, out_file, capacita_media):	                        # e' il modello che carica i flussi multipli
		
	for k in range(0,s):
		count = count +1 	
		out_file.write("il flusso "+str(count)+" ["+str(src)+", "+str(dst)+"]\n")
		size = capacita_flusso_mod_esp(capacita_media)
		flow_catalogue[count]=(src,dst,{'out':{'size': size, 'allocated': False, 'srcPort': '', 'dstPort':''}})
		count = count +1
		flow_catalogue[count]=(dst,src,{'out':{'size': size, 'allocated': False, 'srcPort': '', 'dstPort':''}})
	
	return flow_catalogue

def weight_flows(nx_topology, n_medio_flussi_multipli):
	# n_medio_flussi_multipli * r = perc% C  
	# r = peso medio dei flussi
	# C = capacita' media dei link
	C = 0
	count = 0
	for edge in nx_topology.edges_iter(data=True):
		C = C + edge[2]['capacity']
		count = count +1

	C = C / float(count)
	r = (perc/float(100)) * C / float(n_medio_flussi_multipli)
	
	return r	
	
def capacita_flusso_mod_esp(capacita_media):
	a=random.expovariate(1/float(capacita_media))             # la capacita' dei flussi segue un modello esponenziale limitato tra 1 e 10                       
	return a 

def capacita_flusso_mod_unif(capacita_media):
	cap_min=5
	cap_max=(2*capacita_media)-cap_min
	a=random.uniform(cap_min,cap_max)
	return a

def generatore_pr_alfa():
	alfa=random.random()
	return alfa

def build_flows(nx_topology, out_file):
	
	random.seed(10)	                      #rende ripetibili le prove 
	np.random.seed(10)                    #rende ripetibile la distribuzione geometrica che usa la libreria numpy
	flow_catalogue = {}
	count = 0
	flow=0
	
	
	nx_topology_copy=nx_topology.copy()
	
	capacita_media = weight_flows(nx_topology, n_medio_flussi_multipli)
	
	for edge in nx_topology.nodes_iter(data=True):
		if edge[1]['type_node'] == 'bordo' :
			for edge1 in nx_topology_copy.nodes_iter(data=True):
				if edge1[1]['type_node'] == 'bordo' and edge[0] != edge1[0] :
					test = False
					for c in flow_catalogue:
						if  edge[0] == flow_catalogue[c][0] and edge1[0] == flow_catalogue[c][1]:
							test = True
						
					if test == False:
						pr_alfa=generatore_pr_alfa()
						if pr_alfa < alfa:
							size = capacita_flusso_mod_esp(capacita_media)
							#size = capacita_flusso_mod_unif(capacita_media)
							out_file.write("il flusso "+str(count)+" ["+str(edge[0])+", "+str(edge1[0])+"] \n")
							flow_catalogue[count]=(edge[0],edge1[0],{'out':{'size': size, 'allocated': False, 'srcPort': '', 'dstPort':'', "path": [], "type": "vll"}})
							count = count +1
							flow_catalogue[count]=(edge1[0],edge[0],{'out':{'size': size, 'allocated': False, 'srcPort': '', 'dstPort':'', "path": [], "type": "vll"}})
							s = np.random.geometric((1/float(n_medio_flussi_multipli)))                                        # s e' il numero dei flussi multipli, segue una distribuzione geometrica
							flow_catalogue=add_multiple_flows(s, flow_catalogue, edge[0], edge1[0], count, out_file, capacita_media)           # carica i flussi multipli
							count=len(flow_catalogue)

	return flow_catalogue		

