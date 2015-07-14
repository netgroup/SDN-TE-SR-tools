#!/usr/bin/python

import os
import sys
from pprint import pprint
import json
import networkx as nx
import siphash
import matplotlib.pyplot as plt

class TopologyBuilderFactory:

	def getTopologyBuilder(self, source, data):
		if source == "ryu":
			return RyuTopologyBuilder(data)
		elif source == "floodlight":
			return FloodlightTopologyBuilder(data)
		elif source == "erdos-renyi":
			return ErdosRenyiTopologyBuilder(data)
		elif source == "waxman":
			return WaxmanTopologyBuilder(data)
		elif source == "barabasi-albert":
			return BarabasiAlbertTopologyBuilder(data)
		else:
			print "Builder %s Not Supported...Exit" %(source)
			sys.exit(-1)

class RandomTopologyBuilder:

	def __init__(self):
		self.nx_topology = None
		self.max_capacity = 0.0
		key = '0123456789ABCDEF'
		self.sip = siphash.SipHash_2_4(key)

	def nx_topoPrint(self):
		if self.nx_topology is None:
			print []
		else:
			print self.nx_topology.edges(data=True)
			nx.draw_random(self.nx_topology)
			plt.show()

	def is_connected(self):
		return nx.is_strongly_connected(self.nx_topology)

	def serialize(self):

		with open('links.json', 'w') as outfile:
			json.dump(self.nx_topology.edges(data=True), outfile, indent=4, sort_keys=True)
			outfile.close()

		with open('nodes.json', 'w') as outfile:
			json.dump(self.nx_topology.nodes(data=True), outfile, indent=4, sort_keys=True)
			outfile.close()	
		

class ErdosRenyiTopologyBuilder(RandomTopologyBuilder):


# n : The number of nodes.
# p : Probability for edge creation.
# seed : Seed for random number generator (default=None).
# directed : If True return a directed graph

	DEFAULT_SPEED = 10000

	def __init__(self, data):
		RandomTopologyBuilder.__init__(self)
		self.nodes = data[0]
		self.probability = data[1]
		self.seed = data[2]
		self.directed = data[3]

	def generate(self):

		erdos = nx.erdos_renyi_graph(self.nodes, self.probability)
		self.nx_topology = nx.MultiDiGraph()
		self.nx_topology.clear()

		index = 0

		nodes = []
		for node in erdos.nodes():
			nodes.append(node+1)

		self.nx_topology.add_nodes_from(nodes)

		for (n1, n2) in erdos.edges():

			n1 = n1 + 1
			n2 = n2 + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			self.nx_topology.add_edge(n1, n2, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			self.nx_topology.add_edge(n2, n1, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1	

class WaxmanTopologyBuilder(RandomTopologyBuilder):

# n : Number of nodes
# alpha: Model parameter
# beta: Model parameter
# L : Maximum distance between nodes. If not specified the actual distance is calculated.
# domain : Domain size (xmin, ymin, xmax, ymax)

	DEFAULT_SPEED = 10000

	def __init__(self, data):
		RandomTopologyBuilder.__init__(self)
		self.nodes = data[0]
		self.alpha = data[1]
		self.beta = data[2]
		self.L = data[3]
		self.domain = data[4]

	def generate(self):

		waxman = nx.waxman_graph(self.nodes, self.alpha, self.beta, self.L, self.domain)
		self.nx_topology = nx.MultiDiGraph()
		self.nx_topology.clear()

		index = 0

		nodes = []
		for node in waxman.nodes():
			nodes.append(node+1)

		self.nx_topology.add_nodes_from(nodes)

		for (n1, n2) in waxman.edges():

			n1 = n1 + 1
			n2 = n2 + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			self.nx_topology.add_edge(n1, n2, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			self.nx_topology.add_edge(n2, n1, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1	

class BarabasiAlbertTopologyBuilder(RandomTopologyBuilder):

# n : Number of nodes
# m : Number of edges to attach from a new node to existing nodes
# seed : Seed for random number generator (default=None)

	DEFAULT_SPEED = 10000

	def __init__(self, data):
		RandomTopologyBuilder.__init__(self)
		self.nodes = data[0]
		self.m = data[1]
		self.seed = data[2]
		
	def generate(self):

		barabasi_albert = nx.barabasi_albert_graph(self.nodes, self.m, self.seed)
		self.nx_topology = nx.MultiDiGraph()
		self.nx_topology.clear()

		index = 0

		nodes = []
		for node in barabasi_albert.nodes():
			nodes.append(node+1)

		self.nx_topology.add_nodes_from(nodes)

		for (n1, n2) in barabasi_albert.edges():

			n1 = n1 + 1
			n2 = n2 + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			self.nx_topology.add_edge(n1, n2, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			self.nx_topology.add_edge(n2, n1, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1	
	 
class CtrlTopologyBuilder:
	"""docstring for CoTRLTopoTo"""

	def __init__(self, controller):

		self.IpPort = controller
		self.topology = {}
		self.nodes = []
		self.ports = {}
		self.nx_topology = None
		self.max_capacity = 0.0
		key = '0123456789ABCDEF'
		self.sip = siphash.SipHash_2_4(key)

	def ctrl_topoPrint(self):

		print json.dumps(self.topology, sort_keys=True, indent=4)

	def nx_topoPrint(self):

		if self.nx_topology is None:
			print []
		else:
			print self.nx_topology.edges(data=True)

	def parseJsonToNx(self):
		raise NotImplementedError("Abstract Method")

	def serialize(self):
		raise NotImplementedError("Abstract Method")

# XXX Out of date
class FloodlightTopologyBuilder(CtrlTopologyBuilder): 

	def __init__(self, controller):
		CtrlTopologyBuilder.__init__(self, controller)
		    
	def parseJsonToNx(self):
			command = "curl -s http://"+self.IpPort+"/wm/topology/links/json | python -mjson.tool" 
			result = os.popen(command).read()
			if result != "":
				self.topology = json.loads(result)
				self.nx_topology = nx.MultiDiGraph()
				self.nx_topology.clear()
				for link in self.topology:
					src = link['src-switch'].replace(":","")
					dst = link['dst-switch'].replace(":","")
					self.nx_topology.add_edge(src, dst, src_port=str(link['src-port']), dst_port=str(link['dst-port']))

class RyuTopologyBuilder(CtrlTopologyBuilder): 

	def __init__(self, controller):
		CtrlTopologyBuilder.__init__(self, controller)
		    
	def parseJsonToNx(self):
			command = "curl -s http://"+self.IpPort+"/v1.0/topology/links | python -mjson.tool" 
			result = os.popen(command).read()
			command = "curl -s http://"+self.IpPort+"/stats/portdesc | python -mjson.tool"
			result2 = os.popen(command).read()

			if result != "" and result2 != "":
				self.topology = json.loads(result)
				self.ports = json.loads(result2)
				self.nx_topology = nx.MultiDiGraph()
				self.nx_topology.clear()

				index = 0

				for link in self.topology:
					src = link['src']['dpid']
					dst = link['dst']['dpid']
					src_port = link['src']['name']
					dst_port = link['dst']['name']
					src_port_no = link['src']['port_no']
					dst_port_no = link['dst']['port_no']
					src_mac = link['src']['hw_addr'].replace(":","")
					dst_mac = link['dst']['hw_addr'].replace(":","")				

					src_capacity = 0.0
					src_ports = self.ports[str(int(src,16))]
					for port in src_ports:
						if port['name'] == src_port:
							src_capacity = int(port['curr_speed'])/1000						
							break
					if src_capacity == 0.0:
						print "Error - SRC Capacity cannot be 0.0"
						sys.exit(-1)
				
					dst_capacity = 0.0
					dst_ports = self.ports[str(int(dst,16))]
					for port in dst_ports:
						if port['name'] == dst_port:
							dst_capacity = int(port['curr_speed'])/1000						
							break
					if dst_capacity == 0.0:
						print "Error - DST Capacity cannot be 0.0"
						sys.exit(-1)

					if src_capacity <= dst_capacity:
						capacity = src_capacity
					else:
						capacity = dst_capacity	

					if capacity >= self.max_capacity:
						self.max_capacity = capacity		

					self.sip.update(str(index))
					id_ = str(self.sip.hash())

					self.nx_topology.add_edge(src, dst, capacity=capacity, allocated=0.0, src_port=src_port, dst_port=dst_port, src_port_no=src_port_no, dst_port_no=dst_port_no, src_mac=src_mac, dst_mac=dst_mac, flows=[], id=id_) 

					index = index + 1

			else:
				print "Error something does not work"
				sys.exit(-2)

	def serialize(self):

		with open('links.json', 'w') as outfile:
			json.dump(self.nx_topology.edges(data=True), outfile, indent=4, sort_keys=True)
			outfile.close()

		with open('nodes.json', 'w') as outfile:
			json.dump(self.nx_topology.nodes(data=True), outfile, indent=4, sort_keys=True)
			outfile.close()		
		

if __name__ == '__main__':
	#type_builder = "erdos-renyi"
	#data = [153, 0.05, None, False]	
	#type_builder = "waxman"
	#data = [153, 0.4, 0.1, 1000, (-90, -180, 90, 180)]	
	type_builder = "barabasi-albert"
	data = [153, 1, None]
	factory = TopologyBuilderFactory()
	builder = factory.getTopologyBuilder(type_builder, data)
	builder.generate()
	if builder.is_connected():
		builder.nx_topoPrint()
		builder.serialize()
	else:
		print "Topology is not strongly connected"



