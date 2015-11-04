import os
import sys
import networkx as nx
import copy
import argparse
import time
from timer_utility import *


def time_cspf(nx_topology, flow_catalogue, nx_flows, BIGK, out_file, Risultati_Test):
	
	out_file.write("Flussi e relativi path calcolati a fine algoritmo sono: \n")

	n_nodi_di_bordo = 0
	n_nodi_core = 0

	for node in nx_topology.nodes_iter(data=True):
		if node[1]['type_node'] == 'bordo' :
			n_nodi_di_bordo = n_nodi_di_bordo +1 
		if node[1]['type_node'] == 'core' :
			n_nodi_core = n_nodi_core +1

	count_flows = 0
	
	tempo_iniziale=time.time()

	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		
		if 'out' in flow_dict and 'size' in flow_dict['out']:
			work_nx_multidigraph = nx_topology.copy()   # Create a working copy
			size = flow_dict['out']['size']
			prune_graph_by_available_capacity(work_nx_multidigraph, size)
			try:
				path = nx.dijkstra_path(work_nx_multidigraph, src, dst,'weight')
				out_file.write(str(path)+"\n")
				allocate_flow (nx_topology, path, size, "%s-out" % flow_id)
				store_path (nx_flows, src, dst, flow_id, path)
				set_allocated (flow_catalogue, flow_id, "out", allocated = True)
				set_weights_on_available_capa(BIGK, nx_topology)
				count_flows = count_flows + 1
			except nx.NetworkXNoPath:
				path = []
				#print "NON C'E' UN PATH"
				continue


		if 'in' in flow_dict and 'size' in flow_dict['in']:
			work_nx_multidigraph = nx_topology.copy()   # Create a working copy
			size = flow_dict['in']['size']
			prune_graph_by_available_capacity(work_nx_multidigraph, size)
			try:
				path = nx.dijkstra_path(work_nx_multidigraph, dst, src,'weight')
				allocate_flow (nx_topology, path, size, "%s-in" % flow_id)
				store_path (nx_flows, dst, src, flow_id, path)
				set_allocated (flow_catalogue, flow_id, "in", allocated = True)
				set_weights_on_available_capa(BIGK, nx_topology)
				count_flows = count_flows + 1
			except nx.NetworkXNoPath:
				path = nx_flows[src][dst][flow_id]['path']
				size = flow_dict['out']['size']
				de_allocate_flow (nx_topology, path, size, "%s-out" % flow_id)
				delete_path (nx_flows, src, dst, flow_id)
				set_allocated (flow_catalogue, flow_id, "out", allocated = False)
				set_weights_on_available_capa(BIGK, nx_topology)

	# Calculate the total size of the traffic relations admitted
	total_size = 0
	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		if 'out' in flow_dict and flow_dict['out']['allocated']:
			total_size = (float(flow_dict['out']['size'])*S/L) + total_size	
		if 'in' in flow_dict and flow_dict['in']['allocated']:
			total_size = (float(flow_dict['in']['size'])*S/L) + total_size

	if total_size <= 0.0:
		#print "\n", "No Flows"
		return

	# Assignment Phase
	Tglob = calculate_t_s(total_size, nx_topology)
	Tfin = Tglob

	tempo_finale=time.time()
	
	perc_capa = 0	
	Nlink = nx_topology.size()
	cap_allocated = 0
	for edge in nx_topology.edges_iter(data=True):

		perc = (edge[2]['allocated'])/float(edge[2]['capacity'])
		perc_capa = perc_capa + perc

		if cap_allocated < edge[2]['allocated']:
			cap_allocated = edge[2]['allocated']
			cap_tot = edge[2]['capacity'] 
			src_id = edge[0]
			dst_id = edge[1]
	
	out_file.write("La rete e' composta da "+str(n_nodi_core)+" nodi core e "+str(n_nodi_di_bordo)+" nodi di bordo, con un totale di "+str(len(flow_catalogue))+" flussi\n")
	out_file.write("L'algoritmo di CSPF e' stato eseguito in "+str(tempo_finale-tempo_iniziale)+" secondi \n")
	out_file.write("Sono stati allocati "+str(count_flows)+" flussi su "+str(len(flow_catalogue))+"\n")
	out_file.write("Tglob = "+str(Tglob)+"\n")
	out_file.write("La somma totale dei flussi (total_size) e' "+str(total_size)+"\n")
	out_file.close()

	Risultati_Test.write("Utilizzando l'algoritmo CSPF vengono allocati "+str(count_flows)+" flussi su "+str(len(flow_catalogue))+"  la probabilita' di rifiuto e': "+str((len(flow_catalogue)-count_flows)/float(len(flow_catalogue)))+"\n")
	Risultati_Test.write("I link totali nella topologia sono "+str(Nlink)+" e mediamente sono carichi al "+str((perc_capa/Nlink)*100)+"%\n")
	Risultati_Test.write("Il link piu' carico e' quello tra i nodi "+str(src_id)+" e "+str(dst_id)+" ed ha allocato "+str(cap_allocated)+ " Mbps su "+str(cap_tot)+" Mbps\n")
	Risultati_Test.write("Al termine dell'algoritmo il Tglob e': "+str(Tglob)+"\n")
	Risultati_Test.write("L'algoritmo di CSPF viene eseguito in "+str(tempo_finale-tempo_iniziale)+" secondi \n")
	Risultati_Test.write("\n")