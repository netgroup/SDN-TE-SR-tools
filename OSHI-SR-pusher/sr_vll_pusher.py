#!/usr/bin/python

import argparse
import sys
import os
import json
import time

pusher_cfg = {}
tableIP = 0 
tableSBP = 1

def read_conf_file(path):

	global pusher_cfg

	print "*** Read Configuration File For SR Pusher"

	if os.path.exists(path):
		conf = open(path,'r')
		pusher_cfg = json.load(conf)
		conf.close()
	else:
		print "No Configuration File Find In %s" % path
		sys.exit(-2)	

	print "*** PUSHER_CFG", json.dumps(pusher_cfg, sort_keys=True, indent=4)

def get_vll_label_from_dpid(dpid):
	LABEL_MASK=0x0FFFF
	LABEL_VLL=0x080000
	temp = dpid.replace(":","")
	temp = temp[8:]
	loopback = int(temp,16)
	label = (loopback & LABEL_MASK) | LABEL_VLL
	return label

# Utility function for the vlls persisentce
def store_vll(name, dpid, table):
    # Store created vll attributes in local ./vlls.json
    datetime = time.asctime()
    vllParams = {'name': name, 'Dpid':dpid, 'datetime':datetime, 'table_id':table}
    stro = json.dumps(vllParams)
    vllsDb = open('./sr_vlls.json','a+')
    vllsDb.write(stro+"\n")
    vllsDb.close()

def add_command(args):
	print "*** Add Vlls From Configuration File"
	
	print "*** Read Previous Vlls Inserted"
	if os.path.exists('./sr_vlls.json'):
		vllsDb = open('./sr_vlls.json','r')
		vlllines = vllsDb.readlines()
		vllsDb.close()
	else:
		vlllines={}

	read_conf_file(args.path)
	controllerRestIp = args.controllerRestIp
	# Last 3 bits identify the SR-VLL TC
	# 0x40000 -> 010|0 0000 0000 0000 0000
	default_label_value = 262144
	# 0x5FFFF -> 010|1 1111 1111 1111 1111
	max_label_value = 393215

	sw_port_label = {}

	for key, vll in pusher_cfg.iteritems():
		
		srcSW = vll[0]
		dstSW = vll[1]
		srcPo = vll[2]['out']['srcPort']
		dstPo = vll[2]['out']['dstPort']

		out_ = vll[2]['out']
		in_ = vll[2]['in']
		id_ = vll[2]['id']
		out_path = out_['path']
		in_path = in_['path']

		print "out_path", out_path
		print "in_path", in_path

		vllExists = False

		# if the vll exists in the vllDb, we don't insert the flow
		for line in vlllines:
			data = json.loads(line)
			if data['name']==(id_):
				print "Vll %s exists already Skip" % id_
				vllExists = True
				break

		if vllExists == True:
			continue

		temp_sw_port_label = {}

		value = sw_port_label.get(out_path[len(out_path)-1], default_label_value)
		if value > max_label_value:
			print "(F) Reached MAX_LABEL_VALUE For Vll %s - Skipping" % id_
			continue
		temp_sw_port_label[out_path[len(out_path)-1]] = int(value)
		value = value + 1
		sw_port_label[out_path[len(out_path)-1]] = value

		value = sw_port_label.get(in_path[len(in_path)-1], default_label_value)
		if value > max_label_value:
			print "(R) Reached MAX_LABEL_VALUE For Vll %s - Skipping" % id_
			continue
		temp_sw_port_label[in_path[len(in_path)-1]] = int(value)
		value = value + 1
		sw_port_label[in_path[len(in_path)-1]] = value

		if srcSW == dstSW:
			
			# Forward's Rule
			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\"}, \"actions\":[{\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(srcSW, 16), id_, tableIP, int(srcPo, 16), int(dstPo, 16), controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"

			# Reverse Forward's Rule
			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\"}, \"actions\":[{\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(srcSW, 16), id_, tableIP, int(dstPo, 16), int(srcPo, 16), controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"              

			store_vll(id_, srcSW, tableIP)

		else:

			#Forward/in
			push_ip = "{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}," %("34887", temp_sw_port_label[out_path[len(out_path)-1]])
			push_arp = "{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}," %("34888", temp_sw_port_label[out_path[len(out_path)-1]])

			i = len(out_path)-1
			while i >= 0:
				label = get_vll_label_from_dpid(out_path[len(out_path)-1])
				push_ip = push_ip + "{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}," %("34887", label)
				push_arp = push_arp + "{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}," %("34888", label)
				i = i-1

			print "*** Install Ingress Rules (FW) - LHS"
			# Ingress Rule For IP
			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\"}, \"actions\":[%s {\"type\":\"GOTO_TABLE\", \"table_id\":%d}]}' http://%s/stats/flowentry/add" % (int(srcSW, 16), id_, tableIP, int(srcPo, 16), "2048", push_ip, tableSBP, controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"
			
			# Ingress Rule For ARP
			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\"}, \"actions\":[%s {\"type\":\"GOTO_TABLE\", \"table_id\":%d}]}' http://%s/stats/flowentry/add" % (int(srcSW, 16), id_, tableIP, int(srcPo, 16), "2054", push_arp, tableSBP, controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"
			store_vll(id_, srcSW, tableIP)

			print "Install Egress Rules (RV) - LHS"
			# Rule For IP
			labelrv1 = temp_sw_port_label[in_path[len(in_path)-1]]

			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"eth_type\":\"%s\", \"mpls_label\":\"%s\", \"mpls_bos\":\"1\"}, \"actions\":[{\"type\":\"POP_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(srcSW, 16), id_, tableSBP, "34887", labelrv1, "2048", int(srcPo, 16), controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"

			# Rule For ARP
			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"eth_type\":\"%s\", \"mpls_label\":\"%s\", \"mpls_bos\":\"1\"}, \"actions\":[{\"type\":\"POP_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(srcSW, 16), id_, tableSBP, "34888", labelrv1, "2054", int(srcPo, 16), controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"
			
			store_vll(id_, srcSW, tableSBP)

			#Reverse/out

			push_ip = "{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}," %("34887", temp_sw_port_label[in_path[len(in_path)-1]])
			push_arp = "{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}," %("34888", temp_sw_port_label[in_path[len(in_path)-1]])

			i = len(in_path)-1
			while i >= 0:
				label = get_vll_label_from_dpid(in_path[len(in_path)-1])
				push_ip = push_ip + "{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}," %("34887", label)
				push_arp = push_arp + "{\"type\":\"PUSH_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"SET_FIELD\", \"field\":\"mpls_label\", \"value\":%s}," %("34888", label)
				i = i-1

			print "*** Install Ingress Rules (RV) - RHS"
			# Ingress Rule For IP
			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\"}, \"actions\":[%s {\"type\":\"GOTO_TABLE\", \"table_id\":%d}]}' http://%s/stats/flowentry/add" % (int(dstSW, 16), id_, tableIP, int(dstPo, 16), "2048", push_ip, tableSBP, controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"
			
			# Ingress Rule For ARP
			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"in_port\":\"%s\", \"eth_type\":\"%s\"}, \"actions\":[%s {\"type\":\"GOTO_TABLE\", \"table_id\":%d}]}' http://%s/stats/flowentry/add" % (int(dstSW, 16), id_, tableIP, int(dstPo, 16), "2054", push_arp, tableSBP, controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"
			store_vll(id_, dstSW, tableIP)

			print "Install Egress Rules (RV) - LHS"
			# Rule For IP
			labelfw1 = temp_sw_port_label[out_path[len(out_path)-1]]

			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"eth_type\":\"%s\", \"mpls_label\":\"%s\", \"mpls_bos\":\"1\"}, \"actions\":[{\"type\":\"POP_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(dstSW, 16), id_, tableSBP, "34887", labelfw1, "2048", int(dstPo, 16), controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"

			# Rule For ARP
			command = "curl -s -d '{\"dpid\": \"%s\", \"cookie\":\"%s\", \"priority\":\"32768\", \"table_id\":%d, \"match\":{\"eth_type\":\"%s\", \"mpls_label\":\"%s\", \"mpls_bos\":\"1\"}, \"actions\":[{\"type\":\"POP_MPLS\", \"ethertype\":\"%s\"}, {\"type\":\"OUTPUT\", \"port\":\"%s\"}]}' http://%s/stats/flowentry/add" % (int(dstSW, 16), id_, tableSBP, "34888", labelfw1, "2054", int(dstPo, 16), controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"
			
			store_vll(id_, dstSW, tableSBP)

def del_command(data):
	print "*** Delete Saved Vlls and PWs"

	print "*** Read Previous Vlls Inserted"
	if os.path.exists('sr_vlls.json'):
		vllsDb = open('sr_vlls.json','r')
		lines = vllsDb.readlines()
		vllsDb.close()
		vllsDb = open('sr_vlls.json','w')
		
		# Removing previously created flow from switches
    	# using StaticFlowPusher rest API       
    	# currently, circuitpusher records created circuits in local file ./circuits.db 
    	# with circuit name and list of switches
		controllerRestIp = args.controllerRestIp

		for line in lines:
			data = json.loads(line)
			sw = data['Dpid']
			cookie = data['name']
			table = data['table_id']

			print "*** Deleting Vll: %s - Switch %s" % (cookie, sw)
			command = "curl -s -d '{\"cookie\":\"%s\", \"cookie_mask\":\"%s\", \"table_id\":%d, \"dpid\":\"%s\"}' http://%s/stats/flowentry/delete 2> /dev/null" % (cookie, (-1 & 0xFFFFFFFFFFFFFFFF), table, int(sw, 16), controllerRestIp)
			result = os.popen(command).read()
			print "*** Sent Command:", command + "\n"		

	
		vllsDb.close()
	else:
		lines={}
		print "*** No Vlls Inserted"
		#return

def run_command(data):
	if args.action == 'add':
		add_command(data)
	elif args.action == 'delete':
		del_command(data)

def parse_cmd_line():
	parser = argparse.ArgumentParser(description='Segment Routing Virtual Leased Line Pusher')
	parser.add_argument('--controller', dest='controllerRestIp', action='store', default='localhost:8080', help='controller IP:RESTport, e.g., localhost:8080 or A.B.C.D:8080')
	parser.add_argument('--add', dest='action', action='store_const', const='add', default='add', help='action: add')
	parser.add_argument('--delete', dest='action', action='store_const', const='delete', default='add', help='action: delete')
	parser.add_argument('--cfg', dest='path', action='store', default='out_flow_catalogue.json', help='configuration file: path')
	args = parser.parse_args()
	if len(sys.argv)==1:
		parser.print_help()
		sys.exit(1)    
	return args

if __name__ == '__main__':
	args = parse_cmd_line()
	run_command(args)
