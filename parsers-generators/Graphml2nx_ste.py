#########################
# Graphml2nx.py
#########################

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
import numpy as np
from distribuzioni import *

NODE_TYPE_KEY = 'node-type' #old version
#NODE_TYPE_KEY = 'type'     #new version

LINK_TYPE_KEY = 'link-type' #old version
#LINK_TYPE_KEY = 'view'     #new version

# L average length in bit
L = 1000
# Scale factor (Capacity and size are expressed in kb/s)
S = 1000
DEFAULT_LINK_CAPA = 60
PERCENTAGE_NODES_CORE = 0.2



pusher_cfg = {}




# operates on the topology object nx_topology_new passed by reference
def parse_graphml(nx_topology_new, input_file_name, defa_node_type="", defa_link_type=""):

	if input_file_name == 'None':
	   sys.exit('\n\tNo input file was specified as argument....!')

	xml_tree = ET.parse(input_file_name)

	namespace   = "{http://graphml.graphdrawing.org/xmlns}"
	ns = namespace

	
	root_element    = xml_tree.getroot()
	
	graph_element   = root_element.find(ns + 'graph')
	
	 
	index_values_set    = root_element.findall(ns + 'key')	
	node_set            = graph_element.findall(ns + 'node')
	edge_set            = graph_element.findall(ns + 'edge')

	
	id_node_city_dict   = {}
	id_node_country_dict = {}
	id_node_link_speed_dict = {}
	id_node_id_dict = {}
	id_node_link_dict = {"src_id","dst_id"}

	node_name_value=""
	node_country_value=""
	node_id_value=""
	node_link_speed_value=""

	node_speed_link_in_graphml=""
	node_label_country_in_graphml=""
	node_label_name_in_graphml=""
	node_label_id_in_graphml=""

	
	#Trova e assegna il codice degli attributi che ci interessano
	for i in index_values_set:
		if i.attrib['attr.name'] == "id" and i.attrib["for"] == "node":
			node_label_id_in_graphml = i.attrib["id"]  #d37
		if i.attrib['attr.name'] == 'label' and i.attrib['for'] == 'node':
			node_label_name_in_graphml = i.attrib['id']    #d33        
		if i.attrib['attr.name'] == 'Country' and i.attrib['for'] == 'node':
			node_label_country_in_graphml = i.attrib['id']   #d30
		if i.attrib['attr.name'] == 'LinkSpeed' and i.attrib['for'] == 'edge':
			node_speed_link_in_graphml = i.attrib['id']   #d39


	#Entra in ogni nodo del file xml 		
	for n in node_set:

		node_index_value = n.attrib['id']

 		data_set = n.findall(ns + 'data')
 		#entra negli attributi del campo nodo 
		for d in data_set:

			if d.attrib['key'] == node_label_name_in_graphml:
				#prende il nome della citta' dove e' situato il nodo            	
				node_name_value = re.sub(r'\s+', '', d.text)

			if d.attrib['key'] == node_label_country_in_graphml:
				#prende il nome del paese dove e' situato il nodo
				node_country_value = re.sub(r'\s+', '', d.text)

			if d.attrib["key"] == node_label_id_in_graphml:
				#prende l'id del nodo
				node_id_value = re.sub(r'\s+', '', d.text)		

				
        	

        #save id:data couple
		id_node_city_dict[node_index_value] = node_name_value
		id_node_country_dict[node_index_value] = node_country_value
		id_node_id_dict[node_index_value] = int(node_id_value)
		

			
	for i in range(0, len(id_node_city_dict)):
		#Aggiungo i link nella lista 
		nx_topology_new.add_node(int(id_node_id_dict[str(i)]))
		nx_topology_new.node[int(id_node_id_dict[str(i)])][NODE_TYPE_KEY]=defa_node_type

		#print "===========", nx_topology_new.node[int(id_node_id_dict[str(i)])][NODE_TYPE_KEY]

		print 'node City = '+id_node_city_dict[str(i)]+" Country = "+ id_node_country_dict[str(i)]+" id = "+str(id_node_id_dict[str(i)])
		
	print "\n"


	i=0
	#Entra in ogni edge del file xml
	for e in edge_set:
		
		data_set = e.findall(ns + 'data')
		cont = False

		#Entra negli attributi del campo edge
		for d in data_set:
			if d.attrib['key'] == node_speed_link_in_graphml:
				#salva la capacita' del link
				node_link_speed_value = re.sub(r'\s+', '', d.text)     # Da sistemare le unita' di misura delle capacita' della linea!!!!!!!
				cont = True
				
		if cont is False:
			node_link_speed_value=DEFAULT_LINK_CAPA  #Se nel xml non c'e' la capacita', di default l'ho messa a 60  
				
		id_node_link_speed_dict[i] = node_link_speed_value		

		src_id = e.attrib['source']
		dst_id = e.attrib['target']
		
		print "Link tra "+str(id_node_id_dict[src_id])+" e "+str(id_node_id_dict[dst_id])+" con capacita': "+str(id_node_link_speed_dict[i])

		#Carico il link 
		src_index= int(id_node_id_dict[src_id])
		dst_index= int(id_node_id_dict[dst_id])

		unique_key = get_id()
		
		#nx_topology_new.add_edge(src_index,dst_index, key= unique_key, capacity = round(float(id_node_link_speed_dict[i])), allocated=0, type=defa_link_type ,flows=[])
		nx_topology_new.add_edge(src_index,dst_index, key= unique_key, capacity = round(float(id_node_link_speed_dict[i])), allocated=0 ,flows=[])
		#nx_topology_new.add_edge(src_index,dst_index) 
		#print "eccooooo", nx_topology_new.edges(data=True)
		#nx_topology_new.edge[src_index][dst_index]['capacity'] = round(float(id_node_link_speed_dict[i]))
		#nx_topology_new.edge[src_index][dst_index]['allocated'] = 0
		nx_topology_new.edge[src_index][dst_index][unique_key][LINK_TYPE_KEY] = defa_link_type
		#nx_topology_new.edge[src_index][dst_index]['flows'] = []

		unique_key = get_id()
		#GENERA COLLEGAMENTI CONTRARI A QUELLI SOPRA IN MODO DA CREARE LINK BIDIREZIONALI TRA I NODI CORE        
		#nx_topology_new.add_edge(dst_index,src_index, key= unique_key, capacity = round(float(id_node_link_speed_dict[i])), allocated=0, type=defa_link_type ,flows=[])
		nx_topology_new.add_edge(dst_index,src_index, key= unique_key, capacity = round(float(id_node_link_speed_dict[i])), allocated=0, flows=[])
		#nx_topology_new.add_edge(dst_index,src_index) 
		#nx_topology_new.edge[dst_index][src_index]['capacity'] = round(float(id_node_link_speed_dict[i]))
		#nx_topology_new.edge[dst_index][src_index]['allocated'] = 0
		nx_topology_new.edge[dst_index][src_index][unique_key][LINK_TYPE_KEY] = defa_link_type
		#nx_topology_new.edge[dst_index][src_index]['flows'] = []

		i=i+1



	#return is not needed as the function operates on the topology object passed by reference


#it adds edge nodes to the nx_topology_new object
def add_edge_nodes(nx_topology_new):

	global n_nodi_core
	n_nodi_core = nx_topology_new.number_of_nodes()


	global n_nodi_di_bordo	
	n_nodi_di_bordo=int((n_nodi_core*PERCENTAGE_NODES_CORE))    #ho deciso che i nodi di bordo che aggiungo sono il 10% dei nodi presi dal file xml


	random.seed(10)        #generatore casuale con seme per rendere ripetibile la topologia, viene usato per decidere i collegamenti dei nodi di bordo

	for i in range(0,n_nodi_di_bordo):
		dst= random.randrange(0,n_nodi_core-1,1)
		#GENERA COLLEGAMENTI TRA NODI DI BORDO E I NODI CORE SCELTI RANDOM
		nx_topology_new.add_edge(n_nodi_core+i, dst, capacity = int(random.uniform(50,200)), allocated=0, type='bordo-core' ,flows=[])
		
		#GENERA COLLEGAMENTI CONTRARI A QUELLI SOPRA IN MODO DA CREARE LINK BIDIREZIONALI TRA I NODI DI BORDO 
		nx_topology_new.add_edge(dst, n_nodi_core+i, capacity = int(random.uniform(50,200)), allocated=0, type='core-bordo' ,flows=[])		

	#return is not needed as the function operates on the topology object passed by reference

def get_id():
	#TODO it could be possible to replace with sip
	if not hasattr(get_id, "counter"):
		get_id.counter = -1  # it doesn't exist yet, so initialize it
	get_id.counter += 1
	return str(get_id.counter)

