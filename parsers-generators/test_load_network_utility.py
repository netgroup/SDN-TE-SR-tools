import networkx as nx 
import random

CONFIDENCE=5
# L average length in bit
L = 1000
# Scale factor (Capacity and size are expressed in kb/s)
S = 1000

def Catalog_Generator(flussi_aggregati, epsilon, list_node, seed):                   # Ritorna una un dizionario di coppie di nodi di bordo

	#epsilon variabile:
	#size=epsilon=S*N/T      
	#S=Capacita' del flusso aggregato tra due nodi
	#N=numero di coppie di nodi con domanda diversa da zero
	#T=e' la somma di tutte le S (domanda aggregata)  

	flow_catalogue_test = {}
	count = 0
	
	random.seed(seed)
	random.shuffle(list_node)
	T=0
	for i in flussi_aggregati:
		T=T+i[2]

	for node in list_node:
		for i in flussi_aggregati:
			if i[0]==node[0] and i[1]==node[1] and node[3]==False:
				flow_catalogue_test[count]=(node[0],node[1],{'out':{'size': epsilon*(i[2])*len(flussi_aggregati)/float(T), 'allocated': False, 'srcPort': '', 'dstPort':'', "path": [], "type": "vll"}})            # epsilon variabile
				#flow_catalogue_test[count]=(node[0],node[1],{'out':{'size': epsilon, 'allocated': False, 'srcPort': '', 'dstPort':'', "path": [], "type": "vll"}})								                    # epsilon costante			
				count = count + 1

	return flow_catalogue_test

def multidigraph_from_flow_catalogue (fc_dict):
	nx_flows = nx.MultiDiGraph()
	for flow_id, (src, dst, flow_dict) in fc_dict.iteritems():
		if 'out' in flow_dict and 'size' in flow_dict['out']:
				nx_flows.add_edge(src, dst, flow_id, {'size':flow_dict['out']['size'], 'path':[]})
		if 'in' in flow_dict and 'size' in flow_dict['in']:
				nx_flows.add_edge(dst, src, flow_id, {'size':flow_dict['in']['size'], 'path':[]})
	return nx_flows

def cspf(nx_topology, flow_catalogue, nx_flows, control, BIGK, list_node, Risultato_test):
	
	for flow_id, (src, dst, flow_dict) in flow_catalogue.iteritems():
		for i in list_node:
			if i[0]==src and i[1]==dst and i[3]==False:
				if 'out' in flow_dict and 'size' in flow_dict['out']:
					work_nx_multidigraph = nx_topology.copy()   # Create a working copy
					size = flow_dict['out']['size']
					prune_graph_by_available_capacity(nx_topology, size, list_node)     # Se uso work_nx_multidigraph alla fine del ciclo ho la topologia completa in nx_topology (cosi' alla fine ho solo i link che non sono stati eliminati dal prune)
					try:
						path = nx.dijkstra_path(nx_topology, src, dst,'weight')         # Se uso work_nx_multidigraph alla fine del ciclo ho la topologia completa in nx_topology (cosi' alla fine ho solo i link che non sono stati eliminati dal prune)       
						i[2]=i[2]+size
						allocate_flow (nx_topology, path, size, "%s-out" % flow_id)
						#store_path (nx_flows, src, dst, flow_id, path)
						set_allocated (flow_catalogue, flow_id, "out", allocated = True)
						set_weights_on_available_capa(BIGK, nx_topology)
						control = True
					except nx.NetworkXNoPath:
						path = []
						i[3]=True
						#print "NON C'E' UN PATH"
						continue

				if 'in' in flow_dict and 'size' in flow_dict['in']:
					work_nx_multidigraph = nx_topology.copy()   # Create a working copy
					size = flow_dict['in']['size']
					prune_graph_by_available_capacity(work_nx_multidigraph, size)
					try:
						path = nx.dijkstra_path(work_nx_multidigraph, dst, src,'weight')
						allocate_flow (nx_topology, path, size, "%s-in" % flow_id)
						store_path (nx_flows, dst, src, flow_id, path)
						set_allocated (flow_catalogue, flow_id, "in", allocated = True)
						set_weights_on_available_capa(BIGK, nx_topology)
					except nx.NetworkXNoPath:
						path = nx_flows[src][dst][flow_id]['path']
						size = flow_dict['out']['size']
						de_allocate_flow (nx_topology, path, size, "%s-out" % flow_id)
						delete_path (nx_flows, src, dst, flow_id)
						set_allocated (flow_catalogue, flow_id, "out", allocated = False)
						set_weights_on_available_capa(BIGK, nx_topology)
	
	return control

	
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
		#nx_multidigraph[path[i]][path[i + 1]][index]['flows'].append(flow_id)
		
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


def prune_graph_by_available_capacity(nx_multidigraph, size, list_node, tolerance = False,):

	for edge in nx_multidigraph.edges_iter(data = True):
		if 'capacity' in edge[2]:
			epsilon = (float(edge[2]['capacity']) * CONFIDENCE)/100
			
			if (edge[2]['capacity'] - edge[2].get('allocated',0) - epsilon >= size): 
				continue
		else:
			if tolerance:
				continue		

		nx_multidigraph.remove_edge(edge[0],edge[1])
	
def set_weights_on_available_capa(BIGK, nx_multidigraph):
	for edge in nx_multidigraph.edges_iter(data = True):
		edge[2]['weight'] = float(BIGK)/(edge[2].get('capacity',BIGK) - edge[2].get('allocated',0))
	return
