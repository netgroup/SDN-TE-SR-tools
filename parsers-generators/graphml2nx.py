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

# L average length in bit
L = 1000
# Scale factor (Capacity and size are expressed in kb/s)
S = 1000
DEFAULT_LINK_CAPA = 155               # Le capacita' sono espresse in Mbps
PERCENTAGE_NODES_CORE = 0.2

pusher_cfg = {}


def parse_graphml(input_file_name, nx_topology, defa_node_type="OSHI-CR", defa_link_type="core"):

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
	node_speed_units_in_graphml=""

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
		if i.attrib['attr.name'] == 'LinkSpeedUnits' and i.attrib['for'] == 'edge':
			node_speed_units_in_graphml = i.attrib['id']   #d39
			

	i=0
	#Entra in ogni edge del file xml
	
	for e in edge_set:
		
		data_set = e.findall(ns + 'data')
		cont = False

		#Entra negli attributi del campo edge
		for d in data_set:
			if d.attrib['key'] == node_speed_link_in_graphml:
				node_link_speed_value = float(re.sub(r'\s+', '', d.text))
				cont = True
			if d.attrib['key'] == node_speed_units_in_graphml:
				node_speed_units_value = re.sub(r'\s+', '', d.text)
				if node_speed_units_value == 'G':
					node_link_speed_value = node_link_speed_value * 1000 
				
				
		if cont is False:
			node_link_speed_value=DEFAULT_LINK_CAPA  #Se nel xml non c'e' la capacita', di default l'ho messa a 155 Mbps


		id_node_link_speed_dict[i] = node_link_speed_value	

		src_id = e.attrib['source']
		dst_id = e.attrib['target']
		
		#print "Link tra "+str(id_node_id_dict[src_id])+" e "+str(id_node_id_dict[dst_id])+" con capacita': "+str(id_node_link_speed_dict[i])

		#Carico il link 
		nx_topology.add_edge(int(src_id),int(dst_id), capacity = id_node_link_speed_dict[i], allocated=0, flows=[])
		
		#GENERA COLLEGAMENTI CONTRARI A QUELLI SOPRA IN MODO DA CREARE LINK BIDIREZIONALI TRA I NODI CORE        
		nx_topology.add_edge(int(dst_id),int(src_id), capacity = id_node_link_speed_dict[i], allocated=0, flows=[])

		i=i+1

	
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
		for node in nx_topology.nodes_iter(data=True):
			if int(node_id_value) == node[0]:		
				nx_topology.add_node(int(node_id_value), city = node_name_value, country = node_country_value, type_node = 'core' )	

		
#it adds edge nodes to the nx_topology object
def add_edge_nodes(nx_topology):
	
	global n_nodi_core
	n_nodi_core = nx_topology.number_of_nodes()


	global n_nodi_di_bordo	
	n_nodi_di_bordo=int((n_nodi_core*PERCENTAGE_NODES_CORE))    #ho deciso che i nodi di bordo che aggiungo sono il 10% dei nodi presi dal file xml


	random.seed(10)        #generatore casuale con seme per rendere ripetibile la topologia, viene usato per decidere i collegamenti dei nodi di bordo

	count = 0
	random.seed(10)
	
	while count < n_nodi_di_bordo:
		nodo_bordo = random.randrange(0,n_nodi_core)

		if nx_topology.node[nodo_bordo]['type_node'] == 'core':
			nx_topology.node[nodo_bordo]['type_node'] = 'bordo'
			count = count + 1

	
	
