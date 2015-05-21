#!/usr/bin/python

import os
import sys
from pprint import pprint
import json
import networkx as nx

class TopologyBuilderFactory:

	def getTopologyBuilder(self, controller, ip_data):
		if controller == "ryu":
			return RyuTopologyBuilder(ip_data)
		elif controller == "floodlight":
			return FloodlightTopologyBuilder(ip_data)
		else:
			print "Controller %s Not Supported...Exit" %(type_testbed)
			sys.exit(-1)

class TopologyBuilder:
	"""docstring for CoTRLTopoTo"""

	def __init__(self, controller):
		self.IpPort = controller
		self.topology = {}
		self.nodes = []
		self.ports = {}
		self.nx_topology = None
		self.max_capacity = 0.0

	def ctrl_topoPrint(self):
		print json.dumps(self.topology, sort_keys=True, indent=4)

	def nx_topoPrint(self):
		if self.nx_topology is None:
			print []
		else:
			print self.nx_topology.edges(data=True)

	def parseJsonToNx(self):
		raise NotImplementedError("Abstract Method")

# XXX Out of date
class FloodlightTopologyBuilder(TopologyBuilder): 
        
	def __init__(self, controller):
		TopologyBuilder.__init__(self, controller)
		    
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

class RyuTopologyBuilder(TopologyBuilder): 

	def __init__(self, controller):
		TopologyBuilder.__init__(self, controller)
		    
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

				for dpid, ports in self.ports.iteritems():
					if dpid not in self.nodes:
						self.nodes.append(hex(int(dpid)))

				self.nx_topology.add_nodes_from(self.nodes)

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

					self.nx_topology.add_edge(src, dst, capacity=capacity, allocated=0.0, src_port=src_port, dst_port=dst_port, src_port_no=src_port_no, dst_port_no=dst_port_no, src_mac=src_mac, dst_mac=dst_mac, flows=[]) 

			else:
				print "Error something does not work"
				sys.exit(-2)