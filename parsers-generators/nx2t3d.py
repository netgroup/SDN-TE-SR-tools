#######################################################################################################
# nx2t3d.py
#
# Copyright (C) 2015 Pier Luigi Ventre - (Consortium GARR and University of Rome "Tor Vergata")
# Copyright (C) 2015 Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
# www.garr.it - www.uniroma2.it/netgroup - www.cnit.it
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
# @author Stefano Salsano <stefano.salsano@uniroma2.it>

#######################################################################################################

"""
Converts among Networkx multidigraph and T3D formats
"""


import os
import json
import sys
import networkx as nx
import copy
import re
import siphash


#VERTEX_INFO_KEY='vertex_info' #old version
VERTEX_INFO_KEY='info'        #new version

#LINK_ID_KEY = 'link_label'  #old version
LINK_ID_KEY = 'id'          #new version

#LINK_TYPE_KEY = 'link-type' #old version
LINK_TYPE_KEY = 'view'     #new version

#NODE_TYPE_KEY = 'node-type' #old version
NODE_TYPE_KEY = 'type'     #new version



def nx_2_t3d_dict(nx_topology_new, defa_node_type="", defa_link_type="", add_link_id=False):
	"""converts from a Networkx multidigraph into a T3D dictionary (returns the dictionary)
	if defa_node_type is !="" adds a default node type
	if defa_link_type is !="" adds a default link type
	if add_link_id is True, if there is no LINK_ID_KEY adds a unique link_id for each link (the id is unique among all links in the graph)
	the unique link is taken from the key that identifies the link among the multilinks, but it is checked that it is unique

	OPEN ISSUE: HOW DOES IT CONVERT THE UNIDIRECTIONAL LINKS IN THE MultiDiGraph INTO THE BIDIRECTIONAL LINKS IN T3D????
	"""


	nodes_dict = {}
	#all node attributes in Networkx graph are copied in the [VERTEX_INFO_KEY][property]
	for n,d in nx_topology_new.nodes_iter(data=True):
		#print "!!!!node", n
		#print "!!!!dictionary", d
		if NODE_TYPE_KEY not in d and defa_node_type!="":
			d[NODE_TYPE_KEY]= defa_node_type
		nodes_dict[str(n)]={}
		nodes_dict[str(n)][VERTEX_INFO_KEY]={}
		nodes_dict[str(n)][VERTEX_INFO_KEY]['property']={}

		if NODE_TYPE_KEY in d:
			#nodes_dict[str(n)][VERTEX_INFO_KEY][NODE_TYPE_KEY]=d[NODE_TYPE_KEY]
			nodes_dict[str(n)][VERTEX_INFO_KEY][NODE_TYPE_KEY]=d[NODE_TYPE_KEY]
			del d[NODE_TYPE_KEY]
		for key_dict in d:
			#print "key_dict", key_dict
			nodes_dict[str(n)][VERTEX_INFO_KEY]['property'][key_dict]=d[key_dict]
	
	#print "!!!!nodes_dict", nodes_dict
	
	edges_dict = {}
	for source,dest,key,d in nx_topology_new.edges_iter(data=True,keys=True):
		#print "!!!!!source", source, " !!!!!dest", dest
		#print "!!!!edge dictionary", d
		edge_str_id = str(source)+"&&"+str(dest) 
		if edge_str_id not in edges_dict:
			edges_dict[edge_str_id]={}
			edges_dict[edge_str_id]['links']=[]
		link_dict={}
		for key_dict in d:
			link_dict[key_dict]=d[key_dict]
		if LINK_ID_KEY not in link_dict and add_link_id:
			link_dict['LINK_ID_KEY']=get_id(key)
			
		if LINK_TYPE_KEY not in link_dict and defa_link_type != "":
			link_dict[LINK_TYPE_KEY]=defa_link_type	

		#if 'capacity' in d:
		#	link_dict['capacity']=d['capacity']
		#	del d['capacity']
		#if 'allocated' in d:
		#	link_dict['allocated']=d['allocated']
		#	del d['allocated']
		edges_dict[edge_str_id]['links'].append (link_dict)
	#print "!!!!edges_dict", edges_dict

	topo_dict= dict ([("edges",edges_dict),("vertices",nodes_dict)])
	return topo_dict


def nx_2_t3d_json(nx_topology_new, json_out_file):

	topo_dict = nx_2_t3d_dict(nx_topology_new)

	#print topo_dict

	json_data = json.dumps(topo_dict, sort_keys=True, indent=4)
	#print(json_data)

	out_file = open(json_out_file,"w")
	out_file.write(str(json_data)+"\n")
	out_file.close()


def t3d_json_2_nx(nx_topology_new, json_file_in):
	"""converts from a T3D JSON file to a Networkx multidigraph 
	if there is no LINK_ID_KEY or it is the empty string, it adds a unique link_id for each link (the id is unique among all links in the graph)
	the unique link correspond to the key that identifies the link among the multilinks
	"""

	if json_file_in == None:
	   sys.exit('\n\tNo input file was specified as argument....!')
	with open(json_file_in) as data_file:    
		t3d = json.load(data_file)

	#nx_topology_new= nx.MultiDiGraph() it is not possible to redefine the variable here!!!

	for node_id in t3d['vertices']:
		#print "node_id: ", node_id
		#print t3d['vertices'][node_id][VERTEX_INFO_KEY][NODE_TYPE_KEY]
		node_dict={}
		if VERTEX_INFO_KEY in t3d['vertices'][node_id]:
			if 'property' in t3d['vertices'][node_id][VERTEX_INFO_KEY]:
				for key_dict in t3d['vertices'][node_id][VERTEX_INFO_KEY]['property']:
					node_dict[key_dict]=t3d['vertices'][node_id][VERTEX_INFO_KEY]['property'][key_dict]
			if NODE_TYPE_KEY in t3d['vertices'][node_id][VERTEX_INFO_KEY]:
				node_dict[NODE_TYPE_KEY]=t3d['vertices'][node_id][VERTEX_INFO_KEY][NODE_TYPE_KEY]
		nx_topology_new.add_node(node_id, attr_dict=node_dict)
		#print "ADDED NODE :", node_id
	
	for adjacency_id in t3d['edges']:
		#print "adjacency_id: ", adjacency_id
		[id_src, id_dest] = adjacency_id.split("&&")
		#print id_src, id_dest
		for link_dict in t3d['edges'][adjacency_id]['links']:
			#print link_dict
			if LINK_ID_KEY in link_dict:
				if link_dict[LINK_ID_KEY] != "":
					#print "valid link id"
					link_unique_id = link_dict[LINK_ID_KEY]
				else:
					#print "link id is a null string"
					link_unique_id = get_id()
					link_dict[LINK_ID_KEY] = link_unique_id
			else:
				#print "there is no link id"
				link_unique_id = get_id()
				link_dict[LINK_ID_KEY] = link_unique_id

			nx_topology_new.add_edge(id_src, id_dest, key=link_unique_id)

			for key_dict in link_dict:
				nx_topology_new[id_src][id_dest][link_unique_id][key_dict]=	link_dict[key_dict]

	#print "XXXXXXXXXXXXXXXXXXx"
	#for key, dict in nx_topology_new['134']['17'].iteritems():
	#	print key
	#	print dict
	#	print nx_topology_new['134']['17']['254']





def get_id(proposal=None):
	#TODO it could be possible to replace with sip
	if not hasattr(get_id, "counter"):
		get_id.counter = -1  # it doesn't exist yet, so initialize it
		#counter is -1 at the beginning, then it is the highest used integer
	if not hasattr(get_id, "set_of_used_ids"):
		get_id.set_of_used_ids = set()
	
	#if proposal==None:
		#get_id.counter += 1
		#return str(get_id.counter)
	#else:
	if proposal!=None:
		proposal_is_number = True
		try:
			val = int(proposal)
		except ValueError:
			proposal_is_number = False
		if proposal_is_number:
			if val > get_id.counter:
				get_id.counter = val
				return str(get_id.counter)
			#else:
			#	#get_id.counter += 1
			#	#return str(get_id.counter)
		else:
			#if proposal in get_id.set_of_used_ids:
			#	#get_id.counter += 1
			#	#return str(get_id.counter)
			#else:
			if proposal not in get_id.set_of_used_ids:
				get_id.set_of_used_ids.add(proposal)
				return proposal
	get_id.counter += 1
	return str(get_id.counter)

