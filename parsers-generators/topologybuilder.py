#!/usr/bin/python

import os
import sys
from pprint import pprint
import argparse
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
			#SSnodes.append(node+1)
			nodes.append(str(node+1))

		self.nx_topology.add_nodes_from(nodes)

		for (n1, n2) in erdos.edges():

			n1 = n1 + 1
			n2 = n2 + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			#SSself.nx_topology.add_edge(n1, n2, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 
			self.nx_topology.add_edge(str(n1), str(n2), capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			#SSself.nx_topology.add_edge(n2, n1, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 
			self.nx_topology.add_edge(str(n2), str(n1), capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

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
			#SS nodes.append(node+1)
			nodes.append(str(node+1))

		self.nx_topology.add_nodes_from(nodes)

		for (n1, n2) in waxman.edges():

			n1 = n1 + 1
			n2 = n2 + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			#SSself.nx_topology.add_edge(n1, n2, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 
			self.nx_topology.add_edge(str(n1), str(n2), capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			#self.nx_topology.add_edge(n2, n1, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 
			self.nx_topology.add_edge(str(n2), str(n1), capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

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
			#SSnodes.append(node+1)
			nodes.append(str(node+1))

		self.nx_topology.add_nodes_from(nodes)

		for (n1, n2) in barabasi_albert.edges():

			n1 = n1 + 1
			n2 = n2 + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			#SSself.nx_topology.add_edge(n1, n2, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 
			self.nx_topology.add_edge(str(n1), str(n2), capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1
			self.sip.update(str(index))
			id_ = str(self.sip.hash())

			#SSself.nx_topology.add_edge(n2, n1, capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 
			self.nx_topology.add_edge(str(n2), str(n1), capacity=self.DEFAULT_SPEED, allocated=0.0, src_port="", dst_port="", src_port_no="", dst_port_no="", src_mac="", dst_mac="", flows=[], id=id_) 

			index = index + 1	
	 
class CtrlTopologyBuilder:
	"""docstring for CoTRLTopoTo"""

	def __init__(self, controller):

		self.IpPort = controller
		print "initialized TopologyBuilder with address : ", controller
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
			#command = "curl -s http://"+self.IpPort+"/wm/topology/links/json | python -mjson.tool" 
			command = "curl --max-time 30 -s http://"+self.IpPort+"/wm/topology/links/json" 
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
			#command = "curl -s http://"+self.IpPort+"/v1.0/topology/links | python -mjson.tool" 
			command = "curl --max-time 30 -s http://"+self.IpPort+"/v1.0/topology/links" 
			result = os.popen(command).read()
			#command = "curl -s http://"+self.IpPort+"/stats/portdesc | python -mjson.tool"
			command = "curl --max-time 30 -s http://"+self.IpPort+"/stats/portdesc"
			result2 = os.popen(command).read()
			#print "result : ", result
			#print "result2 : ", result2

			if result != "" and result2 != "":
				try:
					self.topology = json.loads(result)
					self.ports = json.loads(result2)
				except ValueError: 
					print 'Decoding JSON has failed'
					print "Error: something does not work in getting info from ryu controller"
					sys.exit(-2)

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
				print "Error: something does not work in getting info from ryu controller"
				sys.exit(-2)

	def serialize(self):

		with open('links.json', 'w') as outfile:
			json.dump(self.nx_topology.edges(data=True), outfile, indent=4, sort_keys=True)
			outfile.close()

		with open('nodes.json', 'w') as outfile:
			json.dump(self.nx_topology.nodes(data=True), outfile, indent=4, sort_keys=True)
			outfile.close()		
		

def run_command(args_in):

	#my_seed = None
	if args_in.random_seed == None:
		random_seed = None
	else:
		random_seed = int(args_in.random_seed)

	print "SEED : ", random_seed
	num_nodes = int(args_in.num_nodes)
	connections = int(args_in.connections)

	#type_builder = "erdos-renyi"
	#data = [num_nodes, 0.05, random_seed, False]	

	#type_builder = "waxman"
	#data = [num_nodes, 0.4, 0.1, 1000, (-90, -180, 90, 180)]	

	#type_builder = "barabasi-albert"
	data = [num_nodes, connections, random_seed]
	
	factory = TopologyBuilderFactory()
	builder = factory.getTopologyBuilder(args_in.type_builder, data)
	builder.generate()
	while not builder.is_connected():
		print "Topology is not strongly connected"
		builder.generate()
	
	#builder.nx_topoPrint()
	print "Generated a connected topology (saved in nodes.json and links.json)"
	builder.serialize()


def parse_cmd_line():
	parser = argparse.ArgumentParser(description="Generates topology according to different models (command line parameters have been linked only for BarabasiAlbert)")
	parser.add_argument('--model', dest='type_builder', action='store', default='barabasi-albert', help='model type, default = barabasi-albert, options = erdos-renyi waxman')
	parser.add_argument('--nodes', dest='num_nodes', action='store', default='100', help='number of nodes, default = 100')
	parser.add_argument('--connections', dest='connections', action='store', default='1', help='number of connections parameter for barabasi-albert model, default = 1')
	parser.add_argument('--seed', dest='random_seed', action='store', default=None, help='seed for the random number generator, default = None')


	args = parser.parse_args()    
#	if len(sys.argv)==1:
#		parser.print_help()
#		sys.exit(1)    
	return args

if __name__ == '__main__':
	args = parse_cmd_line()
	run_command(args)

	#python topologybuilder.py --model barabasi-albert --nodes 153 --connection 1 --seed 69
	#python topologybuilder.py --model waxman --nodes 153 
	#python topologybuilder.py --model erdos-renyi --nodes 153 --seed 69