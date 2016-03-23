import os
import json
import sys
import random
import networkx as nx
import siphash

VLL_PUSHER_FILE_NAME = "../../Dreamer-Mininet-Extensions/vll_pusher.cfg"
FLOW_CATA_FILE_NAME = "flow_catalogue.json"

class FlowBuilderFactory:

	# For from_file, controller_address is the ctrl endpoint; For random generation...
	def getFlowBuilder(self, builder_type, controller_address):
		if builder_type == "from_file":
			return FromFileBuilder(controller_address)
		elif builder_type == "random":
			return None
		else:
			print "Builder %s Not Supported...Exit" %(type_testbed)
			sys.exit(-1)

class FlowBuilder:

	def __init__(self, controller_address):
		self.controller_address = controller_address
		self.flow_catalogue = {}
		self.pusher_cfg = {}
		# 100 Kb/s
		self.ub_static_rate = 100
		self.lb_static_rate = 50
		key = '123456789ABCDEFG'
		self.sip = siphash.SipHash_2_4(key)

	def cataloguePrint(self):
		print json.dumps(self.flow_catalogue, sort_keys=True, indent=4)

	def parseJsonToFC(self):
		raise NotImplementedError("Abstract Method")

	def serialize(self):
		raise NotImplementedError("Abstract Method")

class FromFileBuilder(FlowBuilder): 
        
	def __init__(self, controller_address):
		FlowBuilder.__init__(self, controller_address)
		    
	def parseJsonToFC(self):
		path = VLL_PUSHER_FILE_NAME
		if os.path.exists(path):
				conf = open(path,'r')
				self.pusher_cfg = json.load(conf)
				conf.close()
		else:
			print "No Configuration File Find In %s" % path
			sys.exit(-2)	

		self.retrieve_port_number_and_mac()

		i = 0
		for vll in self.pusher_cfg['vlls']:
			size = random.uniform(self.lb_static_rate, self.ub_static_rate)
			self.sip.update(str(i))
			id_ = str(self.sip.hash())
			self.flow_catalogue[i] = (vll['lhs_dpid'].replace(":",""), vll['rhs_dpid'].replace(":",""), {'out':{'size': size, 'allocated': False, 'srcPort': vll['lhs_intf'], 'dstPort':vll['rhs_intf'], 'type':'vll', 'path':[]}, 'in':{'size': size, 'allocated': False, 'srcPort': vll['rhs_intf'], 'dstPort':vll['lhs_intf'], 'type':'vll', 'path':[]}, 'id':id_})
			i = i + 1

		for pw in self.pusher_cfg['pws']:
			size = random.uniform(self.lb_static_rate, self.ub_static_rate)
			self.sip.update(str(i))
			id_ = str(self.sip.hash())
			self.flow_catalogue[i] = (pw['lhs_dpid'].replace(":",""), pw['rhs_dpid'].replace(":",""), {'out':{'size': size, 'allocated': False, 'srcPort': pw['lhs_intf'], 'dstPort':pw['rhs_intf'], 'srcMac': pw['lhs_mac'].replace(":",""), 'dstMac': pw['rhs_mac'].replace(":",""), 'type':'pw'}, 'in':{'size': size, 'allocated': False, 'srcPort': pw['rhs_intf'], 'dstPort':pw['lhs_intf'], 'srcMac': pw['rhs_mac'].replace(":",""), 'dstMac': pw['lhs_mac'].replace(":",""), 'type':'pw'}, 'id':id_})
			i = i + 1

	def retrieve_port_number_and_mac(self):

		intf_to_port_number = {}

		command = "curl -s http://%s/v1.0/topology/switches | python -mjson.tool" % (self.controller_address)
		result = os.popen(command).read()
		parsedResult = json.loads(result)
		default = None
		
		for vll in self.pusher_cfg['vlls']:
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

		for pw in self.pusher_cfg['pws']:
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

	# Transform the catolgue of the flows in a nx multidigraph
	def multidigraph_from_flow_catalogue(self):
		nx_flows = nx.MultiDiGraph()
		for flow_id, (src, dst, flow_dict) in self.flow_catalogue.iteritems():
			if 'out' in flow_dict and 'size' in flow_dict['out']:
					nx_flows.add_edge(src, dst, flow_id, {'size':flow_dict['out']['size'], 'path':[]})
			if 'in' in flow_dict and 'size' in flow_dict['in']:
					nx_flows.add_edge(dst, src, flow_id, {'size':flow_dict['in']['size'], 'path':[]})
		return nx_flows

	def serialize(self):
		with open(FLOW_CATA_FILE_NAME, 'w') as outfile:
			json.dump(self.flow_catalogue, outfile, indent=4, sort_keys=True)
			outfile.close()
