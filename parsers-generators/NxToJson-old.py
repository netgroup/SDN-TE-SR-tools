from networkx.readwrite import json_graph 
import json
import copy


def flow_Catalogue_Json_Serialization(flow_catalogue):
	with open('flow_catalogue.json', 'w') as outfile:
		json.dump(flow_catalogue, outfile, indent=4, sort_keys=True)
	outfile.close()

def nx_topology_Json_Serialization(nx_topology):

	out_file = open("Links.json","w")
	data = []

	for edge in nx_topology.edges_iter(data = True):
		lista = []
		lista_diz = []
		diz = {}

		lista.append(edge[0])
		lista.append(edge[1])
		diz['allocated'] = edge[2]['allocated']
		diz['capacity'] = edge[2]['capacity']
		diz['dst_mac'] = ""
		diz['dst_port'] = ""
		diz['dst_port_no'] = ""
		diz['flows'] = edge[2]['flows']
		diz['src_mac'] = ""
		diz['src_port'] = ""
		diz['src_port_no'] = ""
		lista.append(diz)
		data.append(lista)

	json_data = json.dumps(data, indent=2)

	
	out_file.write(str(json_data)+"\n")
	out_file.close()