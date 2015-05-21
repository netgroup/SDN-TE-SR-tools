
CONFIDENCE=5
# L average length in bit
L = 1000
# Scale factor (Capacity and size are expressed in kb/s)
S = 1000

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
		nx_multidigraph[path[i]][path[i + 1]][index]['flows'].append(flow_id)
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


def calculate_t_s(total_capacity, nx_multidigraph):
	t = 0
	temp = 0
	for edge in nx_multidigraph.edges_iter(data = True):
		temp = ((float(edge[2]['allocated']) / (edge[2]['capacity'] - 
				edge[2]['allocated']))) + float(temp)
	t = (float(1) / total_capacity) * temp
	return t


def calculate_l(total_capacity, nx_multidigraph, S):
	l = 0
	for edge in nx_multidigraph.edges_iter(data = True):
		l = (float(1) / total_capacity) * ( (float(edge[2]['capacity'])*S) / ( (float(edge[2]['capacity'] - 
			edge[2]['allocated'])*S) ) ** 2) * (10 ** 7)
		edge[2]['l_value'] = l
	return


# Metodo che permette di registrare se un flusso di traffico e' stato allocato o no.
def set_allocated (flow_catalogue, flow_id, direction, allocated = True):
	if direction == 'out':
		flow_catalogue[flow_id][2]['out']['allocated']=allocated
	if direction == 'in':
		flow_catalogue[flow_id][2]['in']['allocated']=allocated


def prune_graph_by_available_capacity(nx_multidigraph, size, tolerance = False,):
	
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

#setta il peso dei link ad 1, viene utilizzato dall'algoritmo di shortest path
def set_weights_on_available_capa_SP(nx_multidigraph):
	for edge in nx_multidigraph.edges_iter(data = True):
		edge[2]['weight'] = 1
	return

