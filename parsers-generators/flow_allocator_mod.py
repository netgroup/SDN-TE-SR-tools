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
from Graphml2nx import *
from NxToJson import * 






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
		

# Allocazione del flusso nello shortest path calcolato.
def allocate_flow (nx_multidigraph, path, size, flow_id):
	for i in range (0, len(path) - 1):
		index = 0
		max_av_cap = 0.0
		j=0
		for j in nx_multidigraph[path[i]][path[i + 1]]:
			av_cap = (nx_multidigraph[path[i]][path[i + 1]][j]['capacity'] - nx_multidigraph[path[i]][path[i + 1]][j]['allocated'])
			if av_cap > max_av_cap:
				max_av_cap = av_cap
				index=j
		nx_multidigraph[path[i]][path[i + 1]][index]['allocated'] = nx_multidigraph[path[i]][path[i + 1]][index]['allocated'] + size
		nx_multidigraph[path[i]][path[i + 1]][index]['flows'].append(flow_id)
	return

# De-allocazione del flusso nel path sostituito.
def de_allocate_flow (nx_multidigraph, path, size, flow_id):
	for i in range (0, len(path) - 1):
		for index in nx_multidigraph[path[i]][path[i + 1]]:
			if flow_id in nx_multidigraph[path[i]][path[i + 1]][index]['flows']:
				nx_multidigraph[path[i]][path[i + 1]][index]['allocated'] = nx_multidigraph[path[i]][path[i + 1]][index]['allocated'] - size
				nx_multidigraph[path[i]][path[i + 1]][index]['flows'].remove(flow_id)
				break
	return

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
print(nx_links.nodes())   # Print nodes of the nx_links
print(nx_links.edges())   # Print edges of the nx_links
print(nx_links.edge[1][3][0]['capacity']) # Print the attribute capacity of the link (1,3)
print(nx_links[1][3])   # Print the map of the link (1,3)
print(nx_links.edge[2])   # Print the adjancies of the node 2
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

def retrieve_port_number_and_mac(controllerRestIP):

	global pusher_cfg

	intf_to_port_number = {}

	command = "curl -s http://%s/v1.0/topology/switches | python -mjson.tool" % (controllerRestIP)
	result = os.popen(command).read()
	parsedResult = json.loads(result)
	default = None
		
	for vll in pusher_cfg['vlls']:
		lhs_intf = vll['lhs_intf']
		lhs_dpid = vll['lhs_dpid'].replace(":","")
		port_number = intf_to_port_number.get("%s-%s" % (lhs_dpid, lhs_intf), default)
		if port_number == None :
			for switch in parsedResult:
				if switch["dpid"] == lhs_dpid:
					for port in switch["ports"]:
						if port["name"] == lhs_intf:
							port_number = str(port["port_no"])
							intf_to_port_number["%s-%s" % (lhs_dpid, lhs_intf)] = port_number
		vll['lhs_intf'] = port_number

		rhs_intf = vll['rhs_intf']
		rhs_dpid = vll['rhs_dpid'].replace(":","")
		port_number = intf_to_port_number.get("%s-%s" % (rhs_dpid, rhs_intf), default)
		if port_number == None :
			for switch in parsedResult:
				if switch["dpid"] == rhs_dpid:
					for port in switch["ports"]:
						if port["name"] == rhs_intf:
							port_number = str(port["port_no"])
							intf_to_port_number["%s-%s" % (rhs_dpid, rhs_intf)] = port_number
		vll['rhs_intf'] = port_number

	for pw in pusher_cfg['pws']:
		lhs_intf = pw['lhs_intf']
		lhs_dpid = pw['lhs_dpid'].replace(":","")
		port_number = intf_to_port_number.get("%s-%s" % (lhs_dpid, lhs_intf), default)
		if port_number == None :
			for switch in parsedResult:
				if switch["dpid"] == lhs_dpid:
					for port in switch["ports"]:
						if port["name"] == lhs_intf:
							port_number = str(port["port_no"])
							intf_to_port_number["%s-%s" % (lhs_dpid, lhs_intf)] = port_number
		pw['lhs_intf'] = port_number

		rhs_intf = pw['rhs_intf']
		rhs_dpid = pw['rhs_dpid'].replace(":","")
		port_number = intf_to_port_number.get("%s-%s" % (rhs_dpid, rhs_intf), default)
		if port_number == None :
			for switch in parsedResult:
				if switch["dpid"] == rhs_dpid:
					for port in switch["ports"]:
						if port["name"] == rhs_intf:
							port_number = str(port["port_no"])
							intf_to_port_number["%s-%s" % (rhs_dpid, rhs_intf)] = port_number
		pw['rhs_intf'] = port_number


	print "*** PUSHER_CFG", json.dumps(pusher_cfg, sort_keys=True, indent=4)

def flow_allocator(ctrl_endpoint):
	
	factory = TopologyBuilderFactory()
	topobuilder = factory.getTopologyBuilder(CTRL, ctrl_endpoint)
	
	# Retrieves the topology from the CTRL controller and build the networkx topology
	topobuilder.parseJsonToNx()
	flow_catalogue = retrieve_flows(ctrl_endpoint)
	nx_links = topobuilder.nx_links
	print('\nnx_multidigraph edges')
	print(list(nx_links.edges_iter(data=True)))
	print "#############################################################", "\n"
	BIGK = topobuilder.max_capacity

	
	# Assign the weights
	set_weights_on_available_capa(BIGK, nx_links)

	# Transforms flow_catalogue in a nx multidigraph
	nx_flows = multidigraph_from_flow_catalogue(flow_catalogue)

	# Assigns the flows
	flow_assignment(nx_links, flow_catalogue, nx_flows, BIGK)

	# Pushes the flows
	flow_pusher(nx_links, flow_catalogue, nx_flows, ctrl_endpoint)


def simulate_flow_allocator(nx_links):


	# BIGK is the max available capacity
	BIGK = 0
	for edge in nx_links.edges_iter(data = True):   
		if edge[2]['capacity'] > BIGK:    
			BIGK = edge[2]['capacity']


	nx.write_dot(nx_links,'multi.dot')
	#dot -Tpng multi.dot > multi.png            PER STAMPARE LA MAPPA DELLA RETE
	

	flows={} 

	flows_file=open("flussi.out","w")

	flow_catalogue_new = build_flows(nx_links, flows_file)				# richiama la funzione che genera i flussi 

	# Assign the weights
	set_weights_on_available_capa(BIGK, nx_links)  
	
	# Transforms flow_catalogue in a nx multidigraph
	nx_flows = multidigraph_from_flow_catalogue(flow_catalogue_new)       #flow_catalogue

	nx_links_Json_Serialization(nx_links)	

	flow_Catalogue_Json_Serialization(flow_catalogue_new)


	nx_links_sp = nx_links.copy()
	nx_links_cspfe = nx_links.copy()
	nx_links_cspf = nx_links.copy()

	flow_catalogue_new_sp = flow_catalogue_new.copy()
	nx_flows_sp = nx_flows.copy()

	flow_catalogue_new_cspf = flow_catalogue_new.copy()
	nx_flows_cspf = nx_flows.copy()

	flow_catalogue_new_cspfe = flow_catalogue_new.copy()
	nx_flows_cspfe = nx_flows.copy()

	
	sh_path_file=open("shortest_path.out","w")
	time_shortestpath(nx_links_sp, flow_catalogue_new_sp, nx_flows_sp, sh_path_file)                         #timer per algoritmo di shortest path
	
	cspf_he_file=open("CSPF_euristico.out","w")
	time_cspf_heuristic(nx_links_cspfe, flow_catalogue_new_cspfe, nx_flows_cspfe, BIGK, cspf_he_file)         #timer per algoritmo cspf euristico
	
	cspf_file=open("CSPF.out","w")
	time_cspf(nx_links_cspf, flow_catalogue_new_cspf,nx_flows_cspf, BIGK, cspf_file)				       #timer per algoritmo cspf					
	

	
	# Assigns the flows
	flow_assignment(nx_links, flow_catalogue_new, nx_flows, BIGK)       


def flow_assignment(nx_links, flow_catalogue, nx_flows, BIGK):

	# CSPF phase	
	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		
		if 'out' in flow_dict and 'size' in flow_dict['out']:
			work_nx_multidigraph = nx_links.copy()   # Create a working copy
			#print(list(work_nx_multidigraph.edges_iter(data=True)))
			size = flow_dict['out']['size']
			prune_graph_by_available_capacity(work_nx_multidigraph, size)
			print "Prune Graph"
			print(list(work_nx_multidigraph.edges_iter(data=True)))
			try:
				path = nx.dijkstra_path(work_nx_multidigraph, src, dst,'weight')
				print "path: "+str(path)
				allocate_flow (nx_links, path, size, "%s-out" % flow_id)
				store_path (nx_flows, src, dst, flow_id, path)
				set_allocated (flow_catalogue, flow_id, "out", allocated = True)
				set_weights_on_available_capa(BIGK, nx_links)
			except nx.NetworkXNoPath:
				path = []
				print "NON C'E' UN PATH"
				continue

		if 'in' in flow_dict and 'size' in flow_dict['in']:
			work_nx_multidigraph = nx_links.copy()   # Create a working copy
			size = flow_dict['in']['size']
			prune_graph_by_available_capacity(work_nx_multidigraph, size)
			try:
				path = nx.dijkstra_path(work_nx_multidigraph, dst, src,'weight')
				allocate_flow (nx_links, path, size, "%s-in" % flow_id)
				store_path (nx_flows, dst, src, flow_id, path)
				set_allocated (flow_catalogue, flow_id, "in", allocated = True)
				set_weights_on_available_capa(BIGK, nx_links)
			except nx.NetworkXNoPath:
				path = nx_flows[src][dst][flow_id]['path']
				size = flow_dict['out']['size']
				de_allocate_flow (nx_links, path, size, "%s-out" % flow_id)
				delete_path (nx_flows, src, dst, flow_id)
				set_allocated (flow_catalogue, flow_id, "out", allocated = False)
				set_weights_on_available_capa(BIGK, nx_links)
				

	# Calculate the total size of the traffic relations admitted
	total_size = 0
	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		if 'out' in flow_dict and flow_dict['out']['allocated']:
			total_size = (float(flow_dict['out']['size'])*S/L) + total_size	
		if 'in' in flow_dict and flow_dict['in']['allocated']:
			total_size = (float(flow_dict['in']['size'])*S/L) + total_size

	print('\nTotal size:')
	print(total_size)
	print '###################################', '\n'

	print('\nFlow catalogue:')
	print(flow_catalogue)
	print '###################################', '\n'

	print('\nnx_Flows:')
	print(list(nx_flows.edges_iter(data=True)))
	print '###################################', '\n'

	print('\nnx_multidigraph edges')
	print(list(nx_links.edges_iter(data=True)))
	print "#############################################################", "\n"
	print "#############################################################", "\n"
	print "#############################################################", "\n"

	if total_size <= 0.0:
		print "\n", "No Flows"
		return

	# Assignment Phase
	Tglob = calculate_t_s(total_size, nx_links)
	print 'Tglob:', Tglob, "\n"
	Tfin = Tglob

	while True:
		Toldfin = Tfin
		for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
			for direction, data in flow_dict.iteritems():
				size = data['size']
				allocated = data['allocated']			
				if allocated:
					print "Tfin:", Tfin, "\n"
					work_nx_links = nx_links.copy()
					if direction == 'out':
						path = nx_flows.edge[src][dst][flow_id]['path']
					elif direction == 'in':
						path = nx_flows.edge[dst][src][flow_id]['path']
					print "Old Path:", path
					print('\nnx_multidigraph edges pre-rerouting')
					print(list(work_nx_links.edges_iter(data=True)))
					print "#############################################################", "\n"
					if direction == 'out':
						de_allocate_flow (work_nx_links, path, size, "%s-out" % flow_id)
					elif direction == 'in':
						de_allocate_flow (work_nx_links, path, size, "%s-in" % flow_id)
					set_weights_on_available_capa(BIGK, work_nx_links)
					work_nx_links2 = work_nx_links.copy()
					prune_graph_by_available_capacity(work_nx_links, size)
					calculate_l(total_size, work_nx_links, S)
					print('\nPruned Topology')
					print(list(work_nx_links.edges_iter(data=True)))
					print "#############################################################", "\n"
					try:
						if direction == 'out':
							new_path = nx.dijkstra_path(work_nx_links, src, dst, 'l_value')
						elif direction == 'in':
							new_path = nx.dijkstra_path(work_nx_links, dst, src, 'l_value')
						print "New Path :", new_path
						if direction == 'out':
							allocate_flow (work_nx_links2, new_path, size, "%s-out" % flow_id)
						elif direction == 'in':
							allocate_flow (work_nx_links2, new_path, size, "%s-in" % flow_id)						
						set_weights_on_available_capa(BIGK, work_nx_links2)
						print('\nnx_multidigraph edges post-rerouting')
						print(list(work_nx_links2.edges_iter(data=True)))
						print "#############################################################", "\n"
						t = calculate_t_s(total_size, work_nx_links2)
						print "T:", t
						if(t < Tfin):
							if direction == 'out':
								de_allocate_flow (nx_links, path, size, "%s-out" % flow_id)
								allocate_flow (nx_links, new_path, size, "%s-out" % flow_id)
								store_path (nx_flows, src, dst, flow_id, new_path)
							elif direction == 'in':
								de_allocate_flow (nx_links, path, size, "%s-in" % flow_id)
								allocate_flow (nx_links, new_path, size, "%s-in" % flow_id)
								store_path (nx_flows, dst, src, flow_id, new_path)
							set_weights_on_available_capa(BIGK, nx_links)
							Tfin = t
					except nx.NetworkXNoPath:
						new_path = []	

					print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", "\n"
					

		if Tfin <= Tglob and Toldfin == Tfin:
			break


def retrieve_link_from_id(nx_multidigraph, lhs, rhs, flow_id):
	for index in nx_multidigraph[lhs][rhs]:
		if flow_id in nx_multidigraph[lhs][rhs][index]['flows']:
			return nx_multidigraph[lhs][rhs][index]


def flow_pusher(nx_links, flow_catalogue, nx_flows, ctrl_endpoint):

	print "*** Add Vlls From Configuration File"

	print "*** Read Previous Vlls Inserted"
	if os.path.exists('./vlls.json'):
		vllsDb = open('./vlls.json','r')
		vlllines = vllsDb.readlines()
		vllsDb.close()
	else:
		vlllines={}

	if os.path.exists('./pws.json'):
		pwsDb = open('./pws.json','r')
		pwlines = pwsDb.readlines()
		pwsDb.close()
	else:
		pwlines={}
		
	# We use this algorithm for the name generation    
	key = '0123456789ABCDEF'
	sip = siphash.SipHash_2_4(key)
	# Extract from cmd line options the controlller information
	controllerRestIp = ctrl_endpoint
	# Dictionary that stores the mapping port:next_label
	# We allocate the label using a counter, and we associate for each port used in this execution the next usable label
	# Probably in future we can add the persistence for the label
	sw_port_label = {}
	
	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		for direction, data in flow_dict.iteritems():
			
			if data['type'] != 'vll' or data['allocated'] == False:
				break
			
			# Retrieve the ingress/egress information
			if direction == 'out':
				srcSwitch = src
				srcPort = data['srcPort']
				dstSwitch = dst
				dstPort = data['dstPort']
			elif direction == 'in':
				srcSwitch = dst
				srcPort = data['srcPort']
				dstSwitch = src
				dstPort = data['dstPort']

			srcLabel=0
			dstLabel=0
			
			print "*** Generate Name From VLL (%s-%s-%s) - (%s-%s-%s)" % (srcSwitch, srcPort, 0, dstSwitch, dstPort, 0)
			sip.update(srcSwitch + "$" + srcPort + "$" + dstSwitch + "$" + dstPort + "$" + "0" + "$" + "0")
			# Generate the name        
			cookie = sip.hash()
			cookie = str(cookie)
			print "*** Vll Name", cookie        
			
			vllExists = False
			
			# if the vll exists in the vllDb, we don't insert the flow
			for line in vlllines:
				data = json.loads(line)
				if data['name']==(cookie):
					print "Vll %s exists already Skip" % cookie
					vllExists = True
					break

			if vllExists == True:
				continue


			print "*** Create Vll:"
			print "*** From Source Device OSHI-PE %s Port %s" % (srcSwitch, srcPort)
			print "*** To Destination Device OSHI-PE %s port %s"% (dstSwitch, dstPort)

			# Dictionary used for store the label of current vll
			temp_sw_port_label = {}

			default = 16
			max_value = 131071

			if int(srcLabel) > max_value or int(dstLabel) > max_value:
				print "Ingress or Egress Label Not Allowable"
				sys.exit(-2)

			route = nx_flows[srcSwitch][dstSwitch][flow_id]['path']
			
			# We generate the labels associated for each port, while the ingress/egress and egress/ingress labels
			# come from the configuration file, because they depend on the local network choice
			for j in range(0, len(route)):
				# Label for the LHS port
				if j == 0:
					temp_key1 = srcSwitch + "-" + srcPort
					temp_sw_port_label[temp_key1] = int(srcLabel)
					if sw_port_label.get(temp_key1,default) <= int(srcLabel):
						sw_port_label[temp_key1] = int(srcLabel)
				# Label for the RHS port            
				elif j == len(route)-1:
					temp_key1 = dstSwitch + "-" + dstPort
					temp_sw_port_label[temp_key1] = int(dstLabel)
					if sw_port_label.get(temp_key1,default) <= int(dstLabel):
						sw_port_label[temp_key1] = int(dstLabel)            
				# Middle ports            
				elif (j > 0 and j < (len(route)-1)):
					ap0Dpid = route[j-1]
					ap1Dpid = route[j]
					inlink = retrieve_link_from_id(nx_links, ap0Dpid, ap1Dpid, "%s-%s" %(flow_id, direction))
					ap2Dpid = route[j+1]
					outlink = retrieve_link_from_id(nx_links, ap1Dpid, ap2Dpid, "%s-%s" %(flow_id, direction))
					inPort = inlink['dst_port_no']
					outPort = outlink['dst_port_no']
					temp_key1 = ap1Dpid + "-" + str(inPort)
					value = sw_port_label.get(temp_key1, default)
					temp_sw_port_label[temp_key1] = value
					value = value + 1
					sw_port_label[temp_key1] = value  
					temp_key1 = ap2Dpid + "-" + str(outPort)
					value = sw_port_label.get(temp_key1, default)
					temp_sw_port_label[temp_key1] = value
					value = value + 1
					sw_port_label[temp_key1] = value          

			print "*** Current Route Label:"
			print json.dumps(temp_sw_port_label, sort_keys=True, indent=4)
			print
			print "*** Global Routes Label:"
			print json.dumps(sw_port_label, sort_keys=True, indent=4)
			print

		
			# Manage the special case of one hop
			if len(route) == 1:
				print "*** One Hop Route"
				# Forward's Rule
				command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\"}, \"actions\":[{\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(srcSwitch, 16), cookie, pusher_cfg['tableIP'], int(srcPort, 16), int(dstPort, 16), controllerRestIp)
				result = os.popen(command).read()
				print "*** Sent Command:", command + "\n"              

				store_vll(cookie, ap1Dpid, pusher_cfg['tableIP'])            

			elif (len(route)) >= 2:
				# In the other cases we use a different approach for the rule; before we see the label
				# of the inport and outport of the same dpid; with more than one hop we see in general for
				# the forward rule the label of the inport on the next switch, while in the reverse rule the label of the inport on the 
				# previous switch. The previous approach is nested in a for loop, we use this loop in the middle dpid, while
				# we manage as special case the ingress/egress node, because the rules are different
				print "*** %s Hop Route" % len(route)
				# We manage first ingress/egress node
				print "*** Create Ingress Rules For LHS Of The Vll - %s" % (srcSwitch)
				# see the image more_than_one_hop for details on the switching label procedure
				ap1Dpid = route[0]
				ap2Dpid = route[1]
				link = retrieve_link_from_id(nx_links, ap1Dpid, ap2Dpid, "%s-%s" %(flow_id, direction))
				ap1Port = link['src_port_no']
				ap2Port = link['dst_port_no']
				temp_key = ap2Dpid + "-" + str(ap2Port)
				label = temp_sw_port_label[temp_key] 
				print "*** Key: %s, Label: %s" % (temp_key, label)

				# Rule For IP
				command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\"}, \"actions\":[{\"type\":\"GOTO_TABLE\", \"table_id\":%d}]}' http://%s/stats/flowentry/add" % (int(srcSwitch, 16), cookie, pusher_cfg['tableIP'], int(srcPort, 16), "2048", pusher_cfg['tableSBP'], ctrl_endpoint)
				result = os.popen(command).read()
				print "*** Sent Command:", command + "\n"

				# Rule For ARP
				command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\"}, \"actions\":[{\"type\":\"GOTO_TABLE\", \"table_id\":%d}]}' http://%s/stats/flowentry/add" % (int(srcSwitch, 16), cookie, pusher_cfg['tableIP'], int(srcPort, 16), "2054", pusher_cfg['tableSBP'], ctrl_endpoint)
				result = os.popen(command).read()
				print "*** Sent Command:", command + "\n"

				store_vll(cookie, srcSwitch, pusher_cfg['tableIP'])

				# Rule For IP
				command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\"}, \"actions\":[{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(srcSwitch, 16), cookie, pusher_cfg['tableSBP'], int(srcPort, 16), "2048", "34887", label, int(ap1Port, 16), ctrl_endpoint)
				result = os.popen(command).read()
				print "*** Sent Command:", command + "\n"

				# Rule For ARP
				command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\"}, \"actions\":[{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(srcSwitch, 16), cookie, pusher_cfg['tableSBP'], int(srcPort, 16), "2054", "34888", label, int(ap1Port, 16), ctrl_endpoint)
				result = os.popen(command).read()
				print "*** Sent Command:", command + "\n"

				store_vll(cookie, srcSwitch, pusher_cfg['tableSBP'])

				print "*** Create Egress Rules For RHS Of The Vll - %s" % (dstSwitch)
				ap1Dpid = route[(len(route)-2)]
				ap2Dpid = route[(len(route)-1)]
				link = retrieve_link_from_id(nx_links, ap1Dpid, ap2Dpid, "%s-%s" %(flow_id, direction))
				ap1Port = link['src_port_no']
				ap2Port = link['dst_port_no']
				temp_key = ap2Dpid + "-" + str(ap2Port)
				label = temp_sw_port_label[temp_key] 
				print "*** Key: %s, Label: %s" % (temp_key, label)

				# Rule For IP
				command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\", \"mpls_label\":\"%s\"}, \"actions\":[{\"type\":\"POP_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(dstSwitch, 16), cookie, pusher_cfg['tableSBP'], int(ap2Port, 16), "34887", label, "2048", int(dstPort, 16), ctrl_endpoint)
				result = os.popen(command).read()
				print "*** Sent Command:", command + "\n"

				# Rule For ARP
				command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\", \"mpls_label\":\"%s\"}, \"actions\":[{\"type\":\"POP_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(dstSwitch, 16), cookie, pusher_cfg['tableSBP'], int(ap2Port, 16), "34888", label, "2054", int(dstPort, 16), ctrl_endpoint)
				result = os.popen(command).read()
				print "*** Sent Command:", command + "\n"

				store_vll(cookie, dstSwitch, pusher_cfg['tableSBP'])
			
				# Now we manage the middle nodes
				for i in range(0, (len(route)-2)):
					print "index:", i
					ap0Dpid = route[i]
					ap1Dpid = route[i+1]
					inlink = retrieve_link_from_id(nx_links, ap0Dpid, ap1Dpid, "%s-%s" %(flow_id, direction))
					ap2Dpid = route[i+2]
					outlink = retrieve_link_from_id(nx_links, ap1Dpid, ap2Dpid, "%s-%s" %(flow_id, direction))
					ap0Port = inlink['dst_port_no']
					ap1Port = outlink['src_port_no']
					ap2Port = outlink['dst_port_no']
					print ap0Dpid, ap0Port					
					print ap1Dpid, ap1Port
					print ap2Dpid, ap2Port

					print "*** Create Rules For %s" % ap1Dpid

					# send one flow mod per pair in route
					temp_key = temp_key = ap1Dpid + "-" + str(ap0Port)
					inlabel = temp_sw_port_label[temp_key]            
					print "*** Key: %s, inLabel: %s" % (temp_key, inlabel)
					print
					temp_key = temp_key = ap2Dpid + "-" + str(ap2Port)
					outlabel = temp_sw_port_label[temp_key]            
					print "*** Key: %s, OutLabel: %s" % (temp_key, outlabel)
					print

					# Rule For IP
					command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\", \"mpls_label\":\"%s\"}, \"actions\":[{\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(ap1Dpid, 16), cookie, pusher_cfg['tableSBP'], int(ap0Port, 16), "34887", inlabel, outlabel, int(ap1Port, 16), ctrl_endpoint)
					result = os.popen(command).read()
					print "*** Sent Command:", command + "\n"

					# Rule For ARP
					command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\", \"mpls_label\":\"%s\"}, \"actions\":[{\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(ap1Dpid, 16), cookie, pusher_cfg['tableSBP'], int(ap0Port, 16), "34888", inlabel, outlabel, int(ap1Port, 16), ctrl_endpoint)
					result = os.popen(command).read()
					print "*** Sent Command:", command + "\n"

					store_vll(cookie, ap1Dpid, pusher_cfg['tableSBP'])

			else:
				print "Error Wrong Route"
				sys.exit(-2)

# Utility function for the vlls persisentce
def store_vll(name, dpid, table):
	# Store created vll attributes in local ./vlls.json
	datetime = time.asctime()
	vllParams = {'name': name, 'Dpid':dpid, 'datetime':datetime, 'table_id':table}
	stro = json.dumps(vllParams)
	vllsDb = open('./vlls.json','a+')
	vllsDb.write(stro+"\n")
	vllsDb.close()

def run_command(data):
	nx_links = nx.MultiDiGraph()
	nx_nodes = nx.MultiDiGraph()
	parse_graphml(args.file, nx_links, nx_nodes, defa_node_type="OSHI-CR", defa_link_type="core")
	add_edge_nodes(nx_links,nx_nodes)
	#flow_allocator(args.controllerRestIp)
	simulate_flow_allocator(nx_links)	

def parse_cmd_line():
	parser = argparse.ArgumentParser(description='Flow Allocator')
	parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
	parser.add_argument('--f', dest='file', action='store', help='file graphml to parse')
	args = parser.parse_args()    
	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)    
	return args
	
if __name__ == '__main__':
	args = parse_cmd_line()
	run_command(args)