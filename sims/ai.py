# Welcome, to the world's coolest learner algorithm

import json
from random import randint

lastfile = "data/algo/last.json"
tlsfile = "data/algo/tls.json"

rundata = []

with open(lastfile, "r") as l:
	for line in l:
		rundata.append(json.loads(line))

with open(tlsfile, "r") as t:
	tlsdata = json.load(t)

'''
for r in rundata:
	print(r)

garbage:
#_, time = now_time
#time = int(time)

for i in range(len(rundata)): #total no of iterations to go
        now_time, pressures = rundata[i].items()
        _, junc_dict = pressures
        junc_dict_list = list(junc_dict.values())
        j_values = []
        j_values_sum = 0.0
        for j in range(len(junc_dict_list)):
                j_values.append(junc_dict_list[j][0])
                j_values_sum = j_values_sum + junc_dict_list[j][0]
                
        if j_values_sum != 0.0:
                print(max(j_values))
                max_index = j_values.index(max(j_values))
                key_max = list(junc_dict.keys())[max_index]
                print('for every iteration max key: {} and value: {}'.format(key_max, j_values[max_index]))
        else:
                key_max = list(junc_dict.keys())[0]

        print('=================================')

'''
#print("\n\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n\n")

#print(tlsdata)

# =============================================================================

#total no of iterations to go
for i in range(20):
        #unpack rundata dict which gives tuples
        now_time, pressures = rundata[i].items() 
        #print the iteration no
        print(now_time)
        # unpacks pressure tuple
        _, junc_dict = pressures
        # store junc_dict dict 'values' 
        junc_dict_list = list(junc_dict.values()) 
        j_values = []
        # for the case of 0 junc pressure
        j_values_sum = 0.0 
        for j in range(len(junc_dict_list)):
                j_values.append(junc_dict_list[j][0])
                j_values_sum = j_values_sum + junc_dict_list[j][0]
                
        if j_values_sum != 0.0:
                # for the given iteration index of the junc with the maximum pressure
                junc_max_index = j_values.index(max(j_values))
                
                #===================================
                
                # corresponding to junc with max pressure index of edge with max pressure
                max_edge_index = list(junc_dict_list[junc_max_index][1].values()).index(max(list(junc_dict_list[junc_max_index][1].values())))
                #id of the edge with max pressure
                edge_key_max = list(junc_dict_list[junc_max_index][1].keys())[max_edge_index]
                # the id of the junc with max pressure
                junc_key_max = list(junc_dict.keys())[junc_max_index] 
                print('for every iteration max junc key: {} and value: {}'.format(junc_key_max, j_values[junc_max_index]))
                print('for every iteration max edge corresponding to max junc key: {} and value: {}'.format(edge_key_max, list(junc_dict_list[junc_max_index][1].values())[max_edge_index]))

                print("*********************************")

                #tls json unpacking into keys and values
                tls_keys = list(tlsdata.keys())
                tls_values = list (tlsdata.values())

                #reaching the target phase array corresponding to junc with maximum pressure
                target_j_tls = tls_values[junc_max_index]
                #reaching the target phase array corresponding to edge with maximum pressure
                target_e_tls1 = target_j_tls[max_edge_index * 2]
                target_e_tls2 = target_j_tls[max_edge_index * 2 + 1]

                #selecting between both traffic phase definition to increase the time of the one with max 'g' or 'G'
                if (target_e_tls1[1].count('r') < target_e_tls2[1].count('r')):
                    #change the time phase of first
                    target_e_tls1[0] = randint(1,10) #to be modified
                else:
                    target_e_tls2[0] = randint(1,10) #to be modified

                
        else:
                print("donot need to alter")
        
        print('=================================')
        






















        
