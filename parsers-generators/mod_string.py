import os

def modifica(b): 
	os.system("sed -i 's/perc = "+str(b)+"/perc = "+str(b+0.1)+"/g' flow_allocator_mod.py")
	os.system("python flow_allocator_mod.py --controller 127.0.0.1:8080 --f graphml/Colt.graphml")