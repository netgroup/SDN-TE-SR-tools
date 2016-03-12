#!/usr/bin/python

#######################################################################################################

# Copyright (C) 2015 Pier Luigi Ventre - (Consortium GARR and University of Rome "Tor Vergata")
# Copyright (C) 2015 Alessandro Sbardella, Giuseppe Siracusano, Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
# www.garr.it - www.uniroma2.it/netgroup - www.cnit.it
#
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# te traffic engineering
#
# @author Pier Luigi Ventre <pl.ventre@gmail.com>
# @author Alessandro Sbardella <alex.sbardella.91@gmail.com>
# @author Giuseppe Siracusano <a_siracusano@tin.it>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>

#######################################################################################################

"""
Parses and transforms topologies between different formats - Generates traffic demands
"""

import os
import json
import inspect
import sys
import networkx as nx
import copy
import argparse
import random
import siphash
import time
import xml.etree.ElementTree as ET
import re
from topologybuilder import * 
import numpy as np
from distribuzioni import *
from timer_shortestpath import *
from timer_cspf_euristico import *
from timer_cspf import *
from graphml2nx_ste import * 
from nx2t3d import *
from nx2json import *
from demand_gen_ste import *


CONFIDENCE = 5
CTRL = 'ryu'
n_nodi_core = 0
n_nodi_di_bordo = 0
FLOW_CATALOGUE_FILENAME = 'flow_catalogue.json'

VLL_TOKEN_IN_T3D = 'Vll'
DATA_TOKEN_IN_T3D = 'Data'
PW_TOKEN_IN_T3D = 'PW'

def set_weights_on_available_capa(BIGK, nx_multidigraph):
	"""Set the links weights considering the availale capcity and the allocated capacity"""

	for edge in nx_multidigraph.edges_iter(data = True):
		edge[2]['weight'] = float(BIGK)/(edge[2].get('capacity',BIGK) - edge[2].get('allocated',0))
	return

def multidigraph_from_flow_catalogue (fc_dict):
	"""Transform the catalogue of the flows in a nx multidigraph"""

	nx_flows = nx.MultiDiGraph()
	for flow_id, (src, dst, flow_dict) in fc_dict.iteritems():
		if 'out' in flow_dict and 'size' in flow_dict['out']:
				nx_flows.add_edge(src, dst, flow_id, {'size':flow_dict['out']['size'], 'path':[]})
		if 'in' in flow_dict and 'size' in flow_dict['in']:
				nx_flows.add_edge(dst, src, flow_id, {'size':flow_dict['in']['size'], 'path':[]})
	return nx_flows

 
def prune_graph_by_available_capacity(nx_multidigraph, size, tolerance = False,):
	"""Prune from the topologies all the links that do not have enough available capacity
	to support the traffic relation (size is the bitrate)
	"""
	
	for edge in nx_multidigraph.edges_iter(data = True):
		if 'capacity' in edge[2]:
			epsilon = (float(edge[2]['capacity']) * CONFIDENCE)/100
			
			if (edge[2]['capacity'] - edge[2].get('allocated',0) - epsilon >= size): 
				continue
		else:
			if tolerance:
				continue		
		nx_multidigraph.remove_edge(edge[0],edge[1])
		


# Metodo che permette di registrare il path del flusso di traffico che stiamo considerando.
def store_path (nx_multidigraph, src, dst, flow_id, path):
	nx_multidigraph[src][dst][flow_id]['path'] = path
	return

def delete_path (nx_multidigraph, src, dst, flow_id):
	nx_multidigraph[src][dst][flow_id]['path'] = []
	return

# Metodo che permette di registrare se un flusso di traffico e' stato allocato o no.
def set_allocated (flow_catalogue, flow_id, direction, allocated = True):
	if direction == 'out':
		flow_catalogue[flow_id][2]['out']['allocated']=allocated
	if direction == 'in':
		flow_catalogue[flow_id][2]['in']['allocated']=allocated
	
def calculate_t_s(total_capacity, nx_multidigraph):
	"""Calculates T in seconds"""
	t = 0
	temp = 0
	for edge in nx_multidigraph.edges_iter(data = True):
		temp = ((float(edge[2]['allocated']) / (edge[2]['capacity'] - 
				edge[2]['allocated']))) + float(temp)
	t = (float(1) / total_capacity) * temp
	return t

# Calculate T in mseconds
def calculate_t_ms(total_capacity, nx_multidigraph):
	return (calculate_t_s * 1000)

def calculate_l(total_capacity, nx_multidigraph, S):
	l = 0
	for edge in nx_multidigraph.edges_iter(data = True):
		l = (float(1) / total_capacity) * ( (float(edge[2]['capacity'])*S) / ( (float(edge[2]['capacity'] - 
			edge[2]['allocated'])*S) ) ** 2) * (10 ** 7)
		edge[2]['l_value'] = l
	return

#Print functions
"""
print(nx_topology.nodes())   # Print nodes of the nx_topology
print(nx_topology.edges())   # Print edges of the nx_topology
print(nx_topology.edge[1][3][0]['capacity']) # Print the attribute capacity of the link (1,3)
print(nx_topology[1][3])   # Print the map of the link (1,3)
print(nx_topology.edge[2])   # Print the adjancies of the node 2
"""

def retrieve_flows(controllerRestIP):
	"""Retrieves the flows from the vll_pusher.cfg and generates the flow_catalogue
	"""

	global pusher_cfg
	
	flow_catalogue = {}
	# 100 Kb/s
	ub_static_rate = 100
	lb_static_rate = 50

	print "*** Read Configuration File"
	path = "vll_pusher.cfg"
	if os.path.exists(path):
			conf = open(path,'r')
			pusher_cfg = json.load(conf)
			conf.close()
	else:
		print "No Configuration File Find In %s" % path
		sys.exit(-2)	

	retrieve_port_number_and_mac(controllerRestIP)

	i = 0
	for vll in pusher_cfg['vlls']:
		size = random.uniform(lb_static_rate, ub_static_rate)
		flow_catalogue[i] = (vll['lhs_dpid'].replace(":",""), vll['rhs_dpid'].replace(":",""), {'out':{'size': size, 'allocated': False, 'srcPort': vll['lhs_intf'], 'dstPort':vll['rhs_intf'], 'type':'vll'}, 'in':{'size': size, 'allocated': False, 'srcPort': vll['rhs_intf'], 'dstPort':vll['lhs_intf'], 'type':'vll'}})
		i = i + 1

	for pw in pusher_cfg['pws']:
		size = random.uniform(lb_static_rate, ub_static_rate)
		flow_catalogue[i] = (pw['lhs_dpid'].replace(":",""), pw['rhs_dpid'].replace(":",""), {'out':{'size': size, 'allocated': False, 'srcPort': pw['lhs_intf'], 'dstPort':pw['rhs_intf'], 'srcMac': pw['lhs_mac'].replace(":",""), 'dstMac': pw['rhs_mac'].replace(":",""), 'type':'pw'}, 'in':{'size': size, 'allocated': False, 'srcPort': pw['rhs_intf'], 'dstPort':pw['lhs_intf'], 'srcMac': pw['rhs_mac'].replace(":",""), 'dstMac': pw['lhs_mac'].replace(":",""), 'type':'pw'}})
		i = i + 1

	print('\nFlow catalogue:')
	print(flow_catalogue)
	print '###################################', '\n'

	return flow_catalogue

def flow_allocator(ctrl_endpoint):
	
	factory = TopologyBuilderFactory()
	topobuilder = factory.getTopologyBuilder(CTRL, ctrl_endpoint)
	
	# Retrieves the topology from the CTRL controller and build the networkx topology
	topobuilder.parseJsonToNx()
	flow_catalogue = retrieve_flows(ctrl_endpoint)
	nx_topology = topobuilder.nx_topology
	print('\nnx_multidigraph edges')
	print(list(nx_topology.edges_iter(data=True)))
	print "#############################################################", "\n"
	BIGK = topobuilder.max_capacity

	
	# Assign the weights
	set_weights_on_available_capa(BIGK, nx_topology)

	# Transforms flow_catalogue in a nx multidigraph
	nx_flows = multidigraph_from_flow_catalogue(flow_catalogue)

	# Assigns the flows
	flow_assignment(nx_topology, flow_catalogue, nx_flows, BIGK)

	# Pushes the flows
	flow_pusher(nx_topology, flow_catalogue, nx_flows, ctrl_endpoint)

def extracts_links(nx_topology_new, my_key, my_value):
	""" extracts the links in a nx multidigraph that match the filter
	returns a new nx multidigraph, the one in input is not changed
	"""
	output_nx = nx.MultiDiGraph()

	for source,dest,key_iter,d in nx_topology_new.edges_iter(data=True,keys=True):
		#print nx_topology_new[source][dest][key]
		if my_key in nx_topology_new[source][dest][key_iter]:
			if nx_topology_new[source][dest][key_iter][my_key]== my_value:
				output_nx.add_edge(source, dest, key=key_iter)
				output_nx[source][dest][key_iter] = nx_topology_new[source][dest][key_iter]
			else:
				#do nothing
				pass
		else:
				#do nothing
				pass
	return output_nx			


def filter_links(nx_topology_new, my_key, my_value):
	""" filter the links in a nx multidigraph, keeping only the ones that match the filter
	operates on the multidigraph given in input
	"""
	remove = []
	for source,dest,key,d in nx_topology_new.edges_iter(data=True,keys=True):
		#print nx_topology_new[source][dest][key]
		if my_key in nx_topology_new[source][dest][key]:
			if nx_topology_new[source][dest][key][my_key]== my_value:
				#do nothing
				pass
			else:
				remove.append([source,dest,key])
		else:
				remove.append([source,dest,key])

	for source,dest,key in remove:
		#print "DELETED : ",source,dest,key
		del nx_topology_new[source][dest][key]



def serialize(nx_topology_new):
	"""generates links.json and nodes.json"""

	with open('links.json', 'w') as outfile:
		json.dump(nx_topology_new.edges(data=True), outfile, indent=4, sort_keys=True)
		outfile.close()

	with open('nodes.json', 'w') as outfile:
		json.dump(nx_topology_new.nodes(data=True), outfile, indent=4, sort_keys=True)
		outfile.close()	

def serialize_flow_catalogue(flow_catalogue):
	"""generates flow catalogue (flow_catalogue.json)"""
	with open(FLOW_CATALOGUE_FILENAME, 'w') as outfile:
		json.dump(flow_catalogue, outfile, indent=4, sort_keys=True)
		outfile.close()		

def print_links(nx_topology_new):

	print "link list"
	print(list(nx_topology_new.edges_iter(data=True)))
	print json.dumps(list(nx_topology_new.edges_iter(data=True)))
	print_info (nx_topology_new)
	print "#####################################################"

def print_info(nx_topology_new):

	print "(nodes, edges, avg_degree) : (", \
	    nx_topology_new.number_of_nodes(), ",",\
	    nx_topology_new.number_of_edges(), ",",\
	    float(nx_topology_new.number_of_edges())/nx_topology_new.number_of_nodes(), \
	    ")"
	
def	generate_flow_cata(nx_topology_links, outfile_name):
	flow_cata = {}
	for source,dest,key_iter,d in nx_topology_links.edges_iter(data=True,keys=True):

		flow_id = get_id()
		size_out = ''
		size_in = ''
		flow_type = 'vll'
		flow_cata[flow_id]=(source,dest,{'id': flow_id, 'out':{'path': [], 'size': size_out, 'allocated': False, 'srcPort': '', 'dstPort':'', 'type': flow_type},'in':{'path': [], 'size': size_in, 'allocated': False, 'srcPort': '', 'dstPort':'', 'type': flow_type}})

	with open(outfile_name, 'w') as outfile:
		json.dump(flow_cata, outfile, indent=4, sort_keys=True)
		outfile.close()		



def retrieve_link_from_id(nx_multidigraph, lhs, rhs, flow_id):
	for index in nx_multidigraph[lhs][rhs]:
		if flow_id in nx_multidigraph[lhs][rhs][index]['flows']:
			return nx_multidigraph[lhs][rhs][index]


def run_command(args_in):

	
	my_seed = int(args_in.random_seed)
	print "SEED : ", my_seed
	random.seed(my_seed)	   #reset random seed to have repeteable output 
	np.random.seed(my_seed)    #reset random seed for numpy library (used in  geometric distribution)


	nx_topology_new = nx.MultiDiGraph()

	##########################################
	#import topology phase 
	##########################################

	if args_in.file_type_in=='graphml':

		#print inspect.getfile(parse_graphml)
		
		parse_graphml(nx_topology_new, args_in.file, defa_node_type="OSHI-CR", defa_link_type="Data", allow_multilink=False)
		print "imported a topology from graphml file"
		print_info(nx_topology_new)


	if args_in.file_type_in=='nx':
		with open("nodes.json") as data_file:    
			nodes_file = json.load(data_file)
		#print json.dumps(nodes_file)
		for node_couple in nodes_file:
			#print node_couple[0]
			nx_topology_new.add_node(node_couple[0], attr_dict=node_couple[1])

		with open("links.json") as data_file:    
			links_file = json.load(data_file)
		#print json.dumps(links_file)
		for link_triple in links_file:
			#print link_triple[2]['id']
			nx_topology_new.add_edge(link_triple[0], link_triple[1], key=link_triple[2]['id'])
			for key_dict in link_triple[2]:
				#print key_dict
				nx_topology_new[link_triple[0]][link_triple[1]][link_triple[2]['id']][key_dict]=link_triple[2][key_dict]

		print "imported a topology from nodes.json and links.json"
		print_info(nx_topology_new)


	if args_in.file_type_in=='t3d':
		t3d_json_2_nx(nx_topology_new, args_in.file)

		print "imported a topology t3d file"
		print_info(nx_topology_new)


	##########################################
	# selecting source/destination nodes
	##########################################

	if args_in.select_edge_nodes:
		#### randomly adds the key value pair 'is_edge'=True to a subset of nodes (needed to generate traffic demand)
		(access_nodes, total_nodes) = add_nodes_marks(nx_topology_new, p_mark=float(args_in.access_prob), key_to_add='is_edge')
		print "number of access nodes ", access_nodes, " (", float(access_nodes)/total_nodes*100, "% )"
		
		#del_nodes_marks(nx_topology_new, "is_edge")

		#uncomment this line if you want to output the links.json and node.json
		#serialize(nx_topology_new)

	##########################################
	#traffic demand generation phase 
	##########################################

	if args_in.generate_demands:

		#flow_catalogue = build_flows(nx_topology_new, traffic_rel_probability=0.2, avg_num_flows = 4, max_num_flows = 10, link_capa_to_traff_rel_ratio=10)
		flow_catalogue = build_flows(nx_topology_new,
									 traffic_rel_probability=float(args_in.t_rel_prob),
									 avg_num_flows = float(args_in.mean_num_flows),
									 max_num_flows = int(args_in.max_num_flows),
									 link_capa_to_traff_rel_ratio=float(args_in.l_to_t_rel_prob)
									 )
		serialize_flow_catalogue(flow_catalogue)

		print "generated traffic demands"
		dict=get_flow_catalogue_stats(flow_catalogue, access_nodes)
		print dict


	#print_links(nx_topology_new)

	##########################################
	#topology output/convertion phase
	##########################################
	
	if args_in.file_type_out=='t3d':
		nx_2_t3d_json(nx_topology_new, 'out.t3d')
		print "converted topology in .t3d format"

	if args_in.file_type_out=='nx':


		if args_in.filters_only_data_link:
			print "filtered only links with view = Data"
			filter_links(nx_topology_new, 'view', DATA_TOKEN_IN_T3D)

		if args_in.generate_vll_pw_flow_cata:
			#only vll catalogue is considered
			vll_list = extracts_links(nx_topology_new, 'view', VLL_TOKEN_IN_T3D) 
			if vll_list.size() > 0:
				generate_flow_cata (vll_list, 'flow_cata_vll.json')
				print "serialized vll_list in flow_cata_vll.json"

			pw_list = extracts_links(nx_topology_new, 'view', PW_TOKEN_IN_T3D) 
			if pw_list.size() > 0:
				generate_flow_cata (pw_list, 'flow_cata_pw.json')
				print "serialized pw_list in flow_cata_pw.json"


		#output the links.json and node.json
		serialize(nx_topology_new)
		print "serialized topology in links.json and node.json"



	#t3d_json_2_nx(nx_topology_new, 'out.t3d')

	#add_edge_nodes (nx_topology_new)
	#print_links(nx_topology_new)

	#flow_allocator(args.controllerRestIp)

# python parse_transform_generate.py --f graphml/Colt_2010_08-153N.graphml --in graphml --out t3d 
# python parse_transform_generate.py --f graphml/Colt_2010_08-153N.graphml --in graphml --out nx --select_edge_nodes --generate_demands --access_node_prob 0.4 --t_rel_prob 0.2 --mean_num_flows 4 --max_num_flows 10 --link__to_t_rel_ratio 10  
# python parse_transform_generate.py --f t3d/small-topology.t3d --in t3d --out nx --filters_only_data_link --generate_vll_pw_flow_cata
# python parse_transform_generate.py --f t3d/small-topo2-4-vll.t3d --in t3d --out nx --filters_only_data_link --generate_vll_pw_flow_cata



def parse_cmd_line():
	parser = argparse.ArgumentParser(description="Parses and transforms topologies between different formats - Generates traffic demands")
	#parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
	parser.add_argument('--f', dest='file', action='store', help='input file to parse')
	parser.add_argument('--in', dest='file_type_in', action='store', default='graphml', help='type of input file, default = graphml, options = t3d, nx')
	parser.add_argument('--out', dest='file_type_out', action='store', default='t3d', help='type of output file, default = t3d, options = nx')
	parser.add_argument('--generate_demands', dest='generate_demands', action='store_true', help='used to generate the traffic demands')
	parser.add_argument('--select_edge_nodes', dest='select_edge_nodes', action='store_true', help='marks edge nodes (needed to generate the traffic demands)')
	parser.add_argument('--filters_only_data_link', dest='filters_only_data_link', action='store_true', help='outputs only links with view = Data')
	parser.add_argument('--generate_vll_pw_flow_cata', dest='generate_vll_pw_flow_cata', action='store_true', help='generates flowcata of vll and pw')

	parser.add_argument('--access_node_prob', dest='access_prob', action='store', default='1', help='probability of a node to be an access node, default = 1')

	parser.add_argument('--t_rel_prob', dest='t_rel_prob', action='store', default='1', help='probability of a traffic relation between nodes, default = 1')
	parser.add_argument('--mean_num_flows', dest='mean_num_flows', action='store', default='1', help='average number of flows in a traffic relation, default = 1')
	parser.add_argument('--max_num_flows', dest='max_num_flows', action='store', default='1', help='maximum number of flows in a traffic relation, default = 1')
	parser.add_argument('--link__to_t_rel_ratio', dest='l_to_t_rel_prob', action='store', default='1', help='ratio between avg link capa and sum of flow rates in a traffic relation, default = 1')

	parser.add_argument('--seed', dest='random_seed', action='store', default='69', help='seed for the random number generato, default = 69')


	args = parser.parse_args()    
	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)    
	return args

	
if __name__ == '__main__':
	args = parse_cmd_line()
	run_command(args)