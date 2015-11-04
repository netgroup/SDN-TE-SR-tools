import networkx as nx 
from networkx.algorithms.flow import ford_fulkerson
import random
from math import sqrt


def Ford_Fulkerson(mod,nx_topology, nx_flows, num_random_rep, Risultati_Test):

    G = nx.DiGraph()


    for edge in nx_topology.edges_iter(data=True):
        G.add_edge(edge[0], edge[1], capacity=edge[2]['capacity'])

    G_copy = G.copy()    

    nx_topology_copy=nx_topology.copy()    

    list_node=[]                   # contiene tutti i nodi di bordo, source e sink su cui calcolare il maxflow
    list_result_maxflow = []       # e' l'array che contiene tutti i maxflow di tutte le num_random_rep combinazioni ingresso uscita
    
    seed = 5
    
    for edge in nx_topology.nodes_iter(data=True):
        if edge[1]['type_node'] == 'bordo' :
            for edge1 in nx_topology_copy.nodes_iter(data=True):
                if edge1[1]['type_node'] == 'bordo' and edge[0] != edge1[0] :
                    list_node.append([edge[0],edge1[0]])                
                            
    Algorithm(G_copy,list_node, list_result_maxflow, mod, Risultati_Test)
    #Risultati_Test.write(str(G_copy.edges(data=True))+"\n\n")
    G_copy = G.copy()
    for i in range(0,num_random_rep-1):
        random.seed(seed+i)
        random.shuffle(list_node)
        Algorithm(G_copy, list_node, list_result_maxflow, mod, Risultati_Test)
        #Risultati_Test.write(str(G_copy.edges(data=True))+"\n\n")
        G_copy = G.copy()

    Risultati_Test.write("Elenco max flow ([source, sink, maxflow]):\n")    
    for i in list_result_maxflow:       
        Risultati_Test.write(str(i))
        Risultati_Test.write("\n")

    list_value = Calculation_of_value(list_result_maxflow, Risultati_Test)    

    return list_value

def Algorithm(G, list_node, list_result_maxflow, mod, Risultati_Test):              #calcola il flusso massimo utilizzando l'algoritmo di Ford Fulkerson tra il source e il sink
    result_maxflow = []
    for i in list_node:
        max_flow = ford_fulkerson(G,i[0],i[1])            #max flow e' una lista che contiene nel primo elemento il max flow della rete, nel secondo elemento contiene una lista con tutti i link della rete e le relative capacita' utilizzate dal flusso
        if mod=="dipendente":                                                 
            G = New_Topology(G, max_flow)
        #if max_flow[0] != 0:                                    #NON INSERISCE NELLA LISTA LE COPPIE CHE HANNO MAXFLOW UGUALE A ZERO 
        result_maxflow.append([i[0],i[1],max_flow[0]])      #e' un'array che contiene [source, sink, maxflow]
    list_result_maxflow.append(result_maxflow)
      

def New_Topology(G, max_flow):                #Aggiorna le capacita' rimanenti nella topologia dopo aver calcolato il max flow tra un Source e un Sink, in questo modo le prove non sono indipendenti l'una dalle altre
    for edge in G.edges_iter(data = True):
        for k in max_flow[1].iteritems():
            if edge[0] == k[0]:
                for j in k[1].iteritems():
                    if edge[1] == j[0]:
                        edge[2]['capacity'] = edge[2]['capacity'] - j[1]       #toglie alla capacita' della rete la capacita' residua del
    return G
    
def Calculation_of_value(list_result_maxflow, Risultati_Test):              #Da come risultato minimo maxflow, massimo max_flow, valore medio, deviazione standard di ogni coppia sorgente destinazione    

    massimo = 0
    minimo = 0
    val_medio = 0
    var_parz = 0
    list_value = []                     # lista che contiene [source, sink, min, max, val_medio, deviazione standard] del max flow
    cont=0
    list_result_maxflow_copy=list_result_maxflow[:]         
    

    del list_result_maxflow_copy[0]
    for i in list_result_maxflow[0]:
        val_medio = i[2]
        minimo = i[2]
        massimo = i[2] 
        n=1
        for k in list_result_maxflow_copy:
            for j in k: 
                if i[0]==j[0] and i[1]==j[1]:
                    n=n+1
                    val_medio = val_medio+ j[2]
                    if j[2]<minimo:
                        minimo=j[2]
                    if j[2]>massimo:
                        massimo=j[2]
        val_medio=float(val_medio)/n                        #val_medio= 1/n*(som x)
        list_value.append([i[0], i[1], minimo, massimo, val_medio, 0])
        
    for i in list_result_maxflow[0]:
        var_parz = (i[2]-list_value[cont][4])**2
        n=1
        for k in list_result_maxflow_copy:
            for j in k: 
                if i[0]==j[0] and i[1]==j[1]:
                    n=n+1 
                    var_parz = var_parz + (j[2]-list_value[cont][4])**2   
        var_camp_corr=float(1)/(n)*var_parz                      #varianza campionaria corretta= 1/(n-1)*Som(x-val_medio)^2    
        list_value[cont][5] = sqrt(var_camp_corr)                #deviazione standard
        cont = cont +1
    Risultati_Test.write("\nLista che contiene i valori calcolati [source, sink, minimo maxflow, massimo max_flow, valore medio, deviazione standard]:\n")
    for i in list_value:
        Risultati_Test.write(str(i)+"\n")

    return list_value

