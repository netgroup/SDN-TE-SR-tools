#!/usr/bin/python
#traffic_rel_probability e' la soglia che determina se tra due nodi c'e' un almeno un flusso
#p e' la soglia che determina se c'e' piu' di un flusso tra X E Y, segue una distribuzione geometrica



import random
import numpy as np

#n_medio_flussi_multipli = 3         # nemero medio di flussi multipli
link_capa_to_traff_rel_ratio = 0.04    #link_capa_to_traff_rel_ratio: ratio of the demand between two access node and the average link capacity 



def add_multiple_flows(flow_catalogue, s, src, dst, avg_flow_size):	                        # e' il modello che carica i flussi multipli
		
	for k in range(0,s):
		#count = count +1 	
		#out_file.write("il flusso "+str(count)+" ["+str(src)+", "+str(dst)+"]\n")
		size = capacita_flusso_mod_esp(avg_flow_size)
		flow_id = get_id()
		flow_catalogue[flow_id]=(src,dst,{'id': flow_id, 'out':{'path': [], 'size': size, 'allocated': False, 'srcPort': '', 'dstPort':''},'in':{'path': [], 'size': size, 'allocated': False, 'srcPort': '', 'dstPort':''}})
		size = capacita_flusso_mod_esp(avg_flow_size)
		flow_id = get_id()
		flow_catalogue[flow_id]=(dst,src,{'id': flow_id,'out':{'path': [], 'size': size, 'allocated': False, 'srcPort': '', 'dstPort':''},'in':{'path': [], 'size': size, 'allocated': False, 'srcPort': '', 'dstPort':''}})
	

#returns the avg_flow_demand that corresponds to the link_capa_to_traff_rel_ratio
def avg_flow_demand(nx_topology, link_capa_to_traff_rel_ratio, avg_num_flows):
	# avg_num_flows * r = C / link_capa_to_traff_rel_ratio  
	# r = peso medio dei flussi
	# C = capacita' media dei link
	C = 0
	count = 0
	for edge in nx_topology.edges_iter(data=True):
		C = C + edge[2]['capacity']
		count = count +1

	if count > 0:
		C = C / float(count)   #average link capacity

	print "average link capacity: ", C
	
	r = (C / link_capa_to_traff_rel_ratio) / float(avg_num_flows)
	
	return r	
	
def capacita_flusso_mod_esp(avg_flow_size):
	a=random.expovariate(1/float(avg_flow_size))             # la capacita' dei flussi segue un modello esponenziale limitato tra 1 e 10                       
	return a                                                  # non e' limitato!!

def capacita_flusso_mod_unif(avg_flow_size):
	cap_min=5
	cap_max=(2*avg_flow_size)-cap_min
	a=random.uniform(cap_min,cap_max)
	return a

# p_mark is the probability to mark a node
def add_nodes_marks(nx_topology, p_mark=1, key_to_add='mark'):
	for my_node, node_dict in nx_topology.nodes_iter(data=True):
		#print my_node, node_dict
		if random.random() < p_mark:
			node_dict[key_to_add]=True 

def del_nodes_marks (nx_topology, key_to_remove):
	for my_node, node_dict in nx_topology.nodes_iter(data=True):
		if key_to_remove in node_dict:
			del node_dict[key_to_remove]


 #traffic_rel_probability               probability that two access nodes have a traffic relation 
def build_flows(nx_topology, traffic_rel_probability=1, avg_num_flows=1, max_num_flows=10, link_capa_to_traff_rel_ratio=20):
	
	random.seed(10)	                      #rende ripetibili le prove 
	np.random.seed(10)                    #rende ripetibile la distribuzione geometrica che usa la libreria numpy
	flow_catalogue = {}


	#avg_flow_size = weight_flows(nx_topology, avg_num_flows)
	avg_flow_size = avg_flow_demand(nx_topology, link_capa_to_traff_rel_ratio, avg_num_flows)

	edge_nodes = list()
	for my_node, node_dict in nx_topology.nodes_iter(data=True):
		if 'is_edge' in node_dict and node_dict['is_edge']:
			edge_nodes.append({my_node:node_dict}) 

	print "number of access nodes ", len(edge_nodes)

	
	for src in range(len(edge_nodes)):
		#print edge_nodes[i]
		for dst in range (src+1, len(edge_nodes)): 	
			#print src, dst
			if random.random() < traffic_rel_probability:
				for node_id_src in edge_nodes[src]:
					for node_id_dst in edge_nodes[dst]:
						#print edge_nodes[src][node_id]

						s = min (np.random.geometric((1/float(avg_num_flows))),max_num_flows)
						#print "s= ", s
						add_multiple_flows(flow_catalogue, s, node_id_src, node_id_dst, avg_flow_size)
						
						#size = capacita_flusso_mod_unif(avg_flow_size)
						#out_file.write("il flusso "+str(count)+" ["+str(my_node[0])+", "+str(my_edge[0])+"] \n")
						#flow_catalogue[count]=(my_node[0],my_edge[0],{'out':{'size': size, 'allocated': False, 'srcPort': '', 'dstPort':'', "path": [], "type": "vll"}})
						#count = count +1
						#flow_catalogue[count]=(my_edge[0],my_node[0],{'out':{'size': size, 'allocated': False, 'srcPort': '', 'dstPort':'', "path": [], "type": "vll"}})
						#s = np.random.geometric((1/float(avg_num_flows)))                                        # s e' il numero dei flussi multipli, segue una distribuzione geometrica
						#flow_catalogue=add_multiple_flows(s, flow_catalogue, my_node[0], my_edge[0], count, out_file, avg_flow_size)           # carica i flussi multipli
						#count=len(flow_catalogue)



	return flow_catalogue		

def get_flow_catalogue_stats(flow_catalogue):
	out_dict={}
	out_dict['num_of_flows']=len(flow_catalogue)

	overall_size_sum = 0
	overall_count = 0
	unidir_traffic_relations={}
	for my_flow_id, flow_data in flow_catalogue.iteritems():
		if 'in' in flow_data[2] and 'size' in flow_data[2]['in']:
			overall_count += 1
			overall_size_sum += flow_data[2]['in']['size']
		if not (flow_data[0], flow_data[1]) in unidir_traffic_relations:
			unidir_traffic_relations[flow_data[0], flow_data[1]]={}
	#	if not 'num_flows' in unidir_traffic_relations[flow_data[0], flow_data[1]]:
	#		unidir_traffic_relations[flow_data[0], flow_data[1]]['num_flows']=0
	#	unidir_traffic_relations[flow_data[0], flow_data[1]]['num_flows']+=1

	avg_flow_size=0
	if overall_count > 0:
		avg_flow_size=overall_size_sum/float(overall_count)
	out_dict['avg_flow_size']=avg_flow_size

	out_dict['num_of_unidir_traffic_relations']=len(unidir_traffic_relations)
	if len(unidir_traffic_relations) > 0:
		out_dict['avg_num_of_flow_per_unidir_traffic_relation']=len(flow_catalogue)/float(len(unidir_traffic_relations))


	#for traffic_relation in unidir_traffic_relations:


	return out_dict

def get_id():
	#TODO it could be possible to replace with sip
	if not hasattr(get_id, "counter"):
		get_id.counter = -1  # it doesn't exist yet, so initialize it
	get_id.counter += 1
	return str(get_id.counter)
