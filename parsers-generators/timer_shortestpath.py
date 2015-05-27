from __future__  import  division
import os
import sys
import networkx as nx
import copy
import argparse
import time
from timer_utility import *

flows_overload = {}

def time_shortestpath(nx_topology, flow_catalogue, nx_flows, out_file):

	n_nodi_di_bordo = 0
	n_nodi_core = 0

	for node in nx_topology.nodes_iter(data=True):
		if node[1]['type_node'] == 'bordo' :
			n_nodi_di_bordo = n_nodi_di_bordo +1 
		if node[1]['type_node'] == 'core' :
			n_nodi_core = n_nodi_core +1
	
	tempo_iniziale=time.time()

	#setta il peso dei link a 1
	set_weights_on_available_capa_SP(nx_topology)
	
	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		
		if 'out' in flow_dict and 'size' in flow_dict['out']:
			work_nx_multidigraph = nx_topology.copy()   # Create a working copy
			size = flow_dict['out']['size']
			try:
				path = nx.dijkstra_path(work_nx_multidigraph, src, dst,'weight')
				out_file.write(str(path)+"\n")
				allocate_flow (nx_topology, path, size, "%s-out" % flow_id)
				store_path (nx_flows, src, dst, flow_id, path)
				set_allocated (flow_catalogue, flow_id, "out", allocated = True)     #ho dovuto commentarlo altrimenti non funziona il flowassignment  perche'???
			except nx.NetworkXNoPath:
				path = []
				out_file.write("NON C'E' UN PATH\n")
				continue

		if 'in' in flow_dict and 'size' in flow_dict['in']:
			work_nx_multidigraph = nx_topology.copy()   # Create a working copy
			try:
				path = nx.dijkstra_path(work_nx_multidigraph, dst, src,'weight')
				allocate_flow (nx_topology, path, size, "%s-in" % flow_id)
				store_path (nx_flows, dst, src, flow_id, path)
				set_allocated (flow_catalogue, flow_id, "in", allocated = True)
			except nx.NetworkXNoPath:
				path = nx_flows[src][dst][flow_id]['path']
				size = flow_dict['out']['size']
				de_allocate_flow (nx_topology, path, size, "%s-out" % flow_id)
				delete_path (nx_flows, src, dst, flow_id)
				set_allocated (flow_catalogue, flow_id, "out", allocated = False)

	# Calculate the total size of the traffic relations admitted
	total_size = 0
	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		if 'out' in flow_dict and flow_dict['out']['allocated']:
			total_size = (float(flow_dict['out']['size'])*S/L) + total_size	
		if 'in' in flow_dict and flow_dict['in']['allocated']:
			total_size = (float(flow_dict['in']['size'])*S/L) + total_size
		

	if total_size <= 0.0:
		print "minore di zero"
	else:	
		# Assignment Phase
		Tglob = 0                 #calculate_t_s(total_size, nx_topology)  DA SISTEMARE!!! DIVISIONE PER ZERO
		

	if Tglob < 0:
		Tglob = -1 	

	tempo_finale=time.time()	

	n_link_overload = 0
	for edge in nx_topology.edges_iter(data = True):
		if edge[2]['capacity'] < edge[2]['allocated']:
			flows_overload[n_link_overload]={'src': edge[0],'dst': edge[1]}
			n_link_overload = n_link_overload + 1


	n_link_tot = 0		
	for edge in nx_topology.edges_iter(data = True):
		if edge[2]['flows'] :
			n_link_tot = n_link_tot + 1

	perc = (n_link_overload/n_link_tot)*100
	

	out_file.write("La rete e' composta da "+str(n_nodi_core)+" nodi core e "+str(n_nodi_di_bordo)+" nodi di bordo, con un totale di "+str(len(flow_catalogue))+" flussi\n")
	out_file.write("L'algoritmo di shortestpath e' stato eseguito in "+str(tempo_finale-tempo_iniziale)+"\n")
	out_file.write("Il numero totale dei link allocati e' "+str(n_link_tot)+", il munero di link sovraccarichi e' "+str(n_link_overload)+"\n")
	out_file.write("la percentuale di link sovraccarichi e' "+"%.2f" % perc+"%\n")   #(n_link_overload/n_link_tot)*100)
	out_file.write('Tglob = '+str(Tglob)+ "\n")
	out_file.write("La somma totale dei flussi (total_size) e' "+str(total_size)+"\n")

	
	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		if 'out' in flow_dict and 'size' in flow_dict['out']:
			set_allocated (flow_catalogue, flow_id, "out", allocated = False)

	
	
	out_file.close()
				