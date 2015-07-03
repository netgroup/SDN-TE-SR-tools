import os


def single_execution(): 

	base_filename = "flow_cata_topo_%s_%s_%s_%s_%s_%s" \
	%(topology, access_node_prob, t_rel_prob, mean_num_flows, max_num_flows, link__to_t_rel_ratio)

	command = "python ste-test.py --f graphml/Colt_2010_08-153N.graphml --in graphml --out t3d --access_node_prob %s --t_rel_prob %s --mean_num_flows %s --max_num_flows %s --link__to_t_rel_ratio %s > %s/%s.info" \
	%(access_node_prob, t_rel_prob, mean_num_flows, max_num_flows, link__to_t_rel_ratio, folder, base_filename)

	print command

	os.system (command)
	command2 = "cp flow_catalogue.json flow_catalogues/%s.json" %(base_filename)

	print command2

	os.system (command2)


folder = "flow_catalogues"
topology = "colt153"

access_node_prob = 0.4
t_rel_prob = 0.2
mean_num_flows = 4
max_num_flows = 10
link__to_t_rel_ratio = 10

for i in [10, 20, 40, 80]:
	link__to_t_rel_ratio = i
	single_execution()

access_node_prob = 0.8
for i in [10, 20, 40, 80, 160, 320]:
	link__to_t_rel_ratio = i
	single_execution()



#	python ste-test.py --f graphml/Colt_2010_08-153N.graphml --in graphml --out t3d --access_node_prob 0.4 --t_rel_prob 0.2 --mean_num_flows 4 --max_num_flows 10 --link__to_t_rel_ratio 10 > flow_catalogues/blabla.info 
