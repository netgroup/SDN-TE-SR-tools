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
from Graphml2nx_ste import * 
from Nx2t3d import *
from Nx2json import *
from demand_gen_ste import *


CONFIDENCE = 5
CTRL = 'ryu'
n_nodi_core = 0
n_nodi_di_bordo = 0

# Set the links weights considering the availale capcity and the allocated capacity
def set_weights_on_available_capa(BIGK, nx_multidigraph):
	for edge in nx_multidigraph.edges_iter(data = True):
		edge[2]['weight'] = float(BIGK)/(edge[2].get('capacity',BIGK) - edge[2].get('allocated',0))
	return

# Transform the catolgue of the flows in a nx multidigraph
def multidigraph_from_flow_catalogue (fc_dict):
	nx_flows = nx.MultiDiGraph()
	for flow_id, (src, dst, flow_dict) in fc_dict.iteritems():
		if 'out' in flow_dict and 'size' in flow_dict['out']:
				nx_flows.add_edge(src, dst, flow_id, {'size':flow_dict['out']['size'], 'path':[]})
		if 'in' in flow_dict and 'size' in flow_dict['in']:
				nx_flows.add_edge(dst, src, flow_id, {'size':flow_dict['in']['size'], 'path':[]})
	return nx_flows

# Prune from the topologies all the links that do not have enough available capacity to support the traffic relation (size is the bitrate)
def prune_graph_by_available_capacity(nx_multidigraph, size, tolerance = False,):
	
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
	
# Calculate T in seconds
def calculate_t_s(total_capacity, nx_multidigraph):
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

# Retrieves the flows from the vll_pusher.cfg and generate the flow_catalogue
def retrieve_flows(controllerRestIP):

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


#generates links.json and nodes.json
def serialize(nx_topology_new):

	with open('links.json', 'w') as outfile:
		json.dump(nx_topology_new.edges(data=True), outfile, indent=4, sort_keys=True)
		outfile.close()

	with open('nodes.json', 'w') as outfile:
		json.dump(nx_topology_new.nodes(data=True), outfile, indent=4, sort_keys=True)
		outfile.close()	

#generates flow_catalogue.json
def serialize_flow_catalogue(flow_catalogue):
	with open('flow_catalogue.json', 'w') as outfile:
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
	

def retrieve_link_from_id(nx_multidigraph, lhs, rhs, flow_id):
	for index in nx_multidigraph[lhs][rhs]:
		if flow_id in nx_multidigraph[lhs][rhs][index]['flows']:
			return nx_multidigraph[lhs][rhs][index]


def run_command(args_in):

	my_seed = 69
	random.seed(my_seed)	   #reset random seed to have repeteable output 
	np.random.seed(my_seed)    #reset random seed for numpy library (used in  geometric distribution)


	nx_topology_new = nx.MultiDiGraph()


	if args_in.file_type_in=='graphml':

		#print inspect.getfile(parse_graphml)
		
		parse_graphml(nx_topology_new, args_in.file, defa_node_type="OSHI-CR", defa_link_type="Data", allow_multilink=False)
		print "imported a topology from graphml file"
		print_info(nx_topology_new)


		#### randomly adds the key value pair 'is_edge'=True to a subset of nodes (needed to generate traffic demand)
		(access_nodes, total_nodes) = add_nodes_marks(nx_topology_new, p_mark=float(args_in.access_prob), key_to_add='is_edge')
		print "number of access nodes ", access_nodes, " (", float(access_nodes)/total_nodes*100, "% )"
		
		#del_nodes_marks(nx_topology_new, "is_edge")

		serialize(nx_topology_new)
	

		#### generates a traffic demand
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

	if args_in.file_type_in=='t3d':
		t3d_json_2_nx(nx_topology_new, args_in.file)


	#print_links(nx_topology_new)
	
	if args_in.file_type_out=='t3d':
		nx_2_t3d_json(nx_topology_new, 'out.t3d')
		print "converted topology in .t3d format"


	#generate_flows(nx_topology_new, edge_nodes_fraction)



	#t3d_json_2_nx(nx_topology_new, 'out.t3d')


	#add_edge_nodes (nx_topology_new)
	#print_links(nx_topology_new)

	#flow_allocator(args.controllerRestIp)

# python ste-test.py --f graphml/Colt_2010_08-153N.graphml --in graphml --out t3d --access_node_prob 0.4 --t_rel_prob 0.2 --mean_num_flows 4 --max_num_flows 10 --link__to_t_rel_ratio 10


def parse_cmd_line():
	parser = argparse.ArgumentParser(description="Parses and transforms topologies between different formats - Generates traffic demands")
	#parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
	parser.add_argument('--f', dest='file', action='store', help='input file to parse')
	parser.add_argument('--in', dest='file_type_in', action='store', default='graphml', help='type of input file, default = graphml, options = t3d')
	parser.add_argument('--out', dest='file_type_out', action='store', default='t3d', help='type of output file, default = t3d, options = nx')
	#parser.add_argument('--generate_demands', dest='generate_demands', action='store', default=False, help='type of output file, default = t3d, options = nx')

	parser.add_argument('--access_node_prob', dest='access_prob', action='store', default='1', help='probability of a node to be an access node, default = 1')

	parser.add_argument('--t_rel_prob', dest='t_rel_prob', action='store', default='1', help='probability of a traffic relation between nodes, default = 1')
	parser.add_argument('--mean_num_flows', dest='mean_num_flows', action='store', default='1', help='average number of flows in a traffic relation, default = 1')
	parser.add_argument('--max_num_flows', dest='max_num_flows', action='store', default='1', help='maximum number of flows in a traffic relation, default = 1')
	parser.add_argument('--link__to_t_rel_ratio', dest='l_to_t_rel_prob', action='store', default='1', help='ratio between avg link capa and sum of flow rates in a traffic relation, default = 1')




	args = parser.parse_args()    
	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)    
	return args

	
if __name__ == '__main__':
	args = parse_cmd_line()
	run_command(args)