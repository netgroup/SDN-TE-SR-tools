from test_load_network_utility import *
import random
import itertools
import time

epsilon = 1              #capacita' dei flussi, e' il passo con cui saturiamo la rete

def Test_Load_Network(nx_topology, flow_catalogue_new, list_value, Risultato_test):    
	seed=5
	count = 0
	list_node = []										#list_node [source, sink, flusso allocato] contiene tutte le coppie di nodi di bordo con il relativo flusso massimo che satura la rete
	control = True
	flussi_aggregati = []                               #flussi_aggregati [source, sink, capacita' flussi aggregati, molteplicita'] contiene tutte le coppie di nodi di bordo con le relative capacita' dei flussi aggregati

	work_flow_catalogue_new = flow_catalogue_new.copy()

	for flow_id, (src, dst, flow_dict) in flow_catalogue_new.iteritems():
		size = 0
		multiplicity = 0
		for flow_id1, (src1, dst1, flow_dict1) in work_flow_catalogue_new.iteritems():
			if src == src1 and dst == dst1:
				multiplicity = multiplicity + 1 
				size = size + flow_dict1['out']['size']
		flussi_aggregati.append([src,dst,size,multiplicity])	
	
	flussi_aggregati.sort()																					#ordina e elimina i doppioni da flussi_aggregati
	flussi_aggregati = list(flussi_aggregati for flussi_aggregati,_ in itertools.groupby(flussi_aggregati))

	nx_topology_copy=nx_topology.copy()
	for edge in nx_topology.nodes_iter(data=True):
		if edge[1]['type_node'] == 'bordo' :
			for edge1 in nx_topology_copy.nodes_iter(data=True):
				if edge1[1]['type_node'] == 'bordo' and edge[0] != edge1[0] :
					list_node.append([edge[0],edge1[0], 0, False])                      #list_node contiene [source, sink, capacita' flusso allocato, flusso ancora allocabile]

	
	tempo_iniziale=time.time()
	passo=epsilon
	
	print 'while'

	while control:
		
		control = False
		
		flow_catalogue_test = Catalog_Generator(flussi_aggregati, passo, list_node, seed)      #crea il flow_caqtalogue a partire da list_node
		
		nx_flows = multidigraph_from_flow_catalogue(flow_catalogue_test) 
		seed = seed +1
		# BIGK is the max available capacity

		
		BIGK = 0
		for edge in nx_topology.edges_iter(data = True):   
			if edge[2]['capacity'] > BIGK:    
				BIGK = edge[2]['capacity']

		control = cspf(nx_topology, flow_catalogue_test, nx_flows, control, BIGK, list_node, Risultato_test)   #algoritmo CSPF 
		nx_topology_work=nx_topology.copy()

		for edge in nx_topology.edges_iter(data=True):
			for edge1 in nx_topology_work.edges_iter(data=True):
				if edge[0] == edge1[0] and edge[1] == edge1[1]:
					edge[2]['capacity']=edge1[2]['capacity']-edge1[2]['allocated']
					edge[2]['allocated'] = 0

		tempo_finale=time.time()
		if tempo_finale-tempo_iniziale >= 60:
			passo = passo * 2
			tempo_iniziale=time.time()
			print passo
		count = count +1

	Ftot = 0							# Domanda aggregata (somma dei flussi aggregati di ogni coppia di nodi)
	for fa in flussi_aggregati:
		Ftot = Ftot + fa[2]

	Prob_Rif = 0                        # probabilita' di riufiuto
	for fa in flussi_aggregati:
		for fmax in list_node:
			if fa[0] == fmax[0] and fa[1] == fmax[1]:
				Prob_Rif = Prob_Rif + (fa[2]/fmax[2]*fa[2]/Ftot)

	media_pesata_flussi = 0
	somma_cap_massima = 0

	Risultato_test.write("Lista dei flussi aggregati (Source, Sink, Capacita' in Mbps, Molteplicita'):\n"+str(flussi_aggregati)+"\n\n")
	Risultato_test.write("Lista dei flussi che saturano la rete (Source, Sink, Capacita' in Mbps):\n"+str(list_node)+"\n\n")
	Risultato_test.write("Percentuale di quanto i flussi occupano rispetto a flussi massimi che saturano la rete:\n")
	for i in flussi_aggregati:
		for j in list_node:
			for k in list_value:
				if i[0] == j[0] == k[0] and i[1] == j[1] == k[1]:
					try:
						Risultato_test.write("Source: "+str(i[0])+"    Sink: "+str(i[1])+"   Percentuale: "+str(i[2]/float(j[2])*100)+"%   "+"Max Flow: "+str(k[4])+"\n")
						media_pesata_flussi = media_pesata_flussi + (i[2]*j[2])
						somma_cap_massima = somma_cap_massima + j[2]
					except:
						Risultato_test.write("Source: "+str(i[0])+"    Sink: "+str(i[1])+"   Flusso non allocato    Max Flow: "+str(k[4])+"\n")
						media_pesata_flussi = media_pesata_flussi + (i[2]*j[2])
						somma_cap_massima = somma_cap_massima + j[2]

	Risultato_test.write("\nPercentuale di rifiuto:   "+str(Prob_Rif)+"\n")
