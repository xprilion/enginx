# Welcome, to the world's coolest learner algorithm

import json
import random
from subprocess import call
from shutil import copyfile


lastfile = "data/algo/last.json"
tlsfile = "data/algo/tls.json"

toprun = "data/algo/bestrun.json"
toptls = "data/algo/besttls.json"

bestrun = sum(1 for line in open(toprun))

iter_since_best = 0

while iter_since_best <= 10:

	iter_since_best += 1

	rundata = []

	with open(lastfile, "r") as l:
		for line in l:
			rundata.append(json.loads(line))

	with open(tlsfile, "r") as t:
		tlsdata = json.load(t)

	pressure_edges = {}

	for row in rundata:
		now_time = row["now_time"]
		pressures = row["pressures"]

		# print(pressures)

		maxpr = 0
		maxprid = ""

		for jnc in pressures.keys():
			if maxpr < pressures[jnc][0]:
				maxpr = pressures[jnc][0]
				maxprid = jnc

			# print(jnc, pressures[jnc][1])

		# print(pressures.keys())
		# print(maxprid)

		if maxprid in pressures.keys():
			# print(pressures[maxprid][1])

			emaxpr = 0
			emaxprid = ""
			emaxprindex = 0

			# print(pressures[maxprid])
			i = 0
			for edg in pressures[maxprid][1].keys():
				if emaxpr < pressures[maxprid][1][edg]:
					emaxpr = pressures[maxprid][1][edg]
					emaxprid = edg
					emaxprindex = i
				i += 1

			# print(now_time, ":", maxprid, "->", maxpr, "............", emaxprid, "(", emaxprindex, ")", "==>", emaxpr)

			# print(pressures[maxprid][1][emaxprid])

			# print(tlsdata[maxprid])

			# factor = len(tlsdata[maxprid]) // len(pressures[maxprid][1])

			# print(factor)

			# print(tlsdata[maxprid][factor*emaxprindex: factor*(emaxprindex+1)])

			tp = (maxprid, emaxprid)

			if tp not in pressure_edges:
				pressure_edges[tp] = [emaxprindex, emaxpr, 1]
			else:
				pressure_edges[tp][1] += emaxpr
				pressure_edges[tp][2] += 1

	# print(pressure_edges)

	for pek, pev in pressure_edges.items():
		avgpr = round(pev[1] / (pev[2] * 100), 1)
		# print(pek, avgpr, tlsdata[pek[0]])

		for t in range(len(tlsdata[pek[0]])):
			if tlsdata[pek[0]][t][1][pev[0]] in ['g', 'G']:
				tlsdata[pek[0]][t][0] += ((avgpr / 2) + random.random() * 3)
			elif tlsdata[pek[0]][t][1][pev[0]] in ['r', 'R']:
				tlsdata[pek[0]][t][0] -= ((avgpr / 2)  + random.random() * 2)
			else:
				tlsdata[pek[0]][t][0] -= ((avgpr / 3)  + random.random())

			if tlsdata[pek[0]][t][0] < 3:
				tlsdata[pek[0]][t][0] = 3
			elif tlsdata[pek[0]][t][0] > 40:
				tlsdata[pek[0]][t][0] = 40

		# print("-------------------")

	with open(tlsfile, "w") as f:
		json.dump(tlsdata, f)

	call(["python3", "algo.py"])

	lastrun = sum(1 for line in open(lastfile))

	if lastrun < bestrun:
		iter_since_best = 0
		bestrun = lastrun
		copyfile(lastfile, toprun)
		copyfile(tlsfile, toptls)

	print("\n---------------------------------------------------------------------------\n")
	print("Last Run: %s || Best Run: %s " % (lastrun, bestrun))
	print("\n---------------------------------------------------------------------------\n")


copyfile(toprun, lastfile)
copyfile(toptls, tlsfile)



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
# for i in range(20):
#     #unpack rundata dict which gives tuples
#     now_time, pressures = rundata[i].items()
#     #print the iteration no
#     # print(now_time)
#     # unpacks pressure tuple
#     _, junc_dict = pressures

#     print(pressures)

#     # store junc_dict dict 'values'
#     junc_dict_list = list(junc_dict.values())
#     j_values = []
#     # for the case of 0 junc pressure
#     j_values_sum = 0.0
#     for j in range(len(junc_dict_list)):
#         j_values.append(junc_dict_list[j][0])
#         j_values_sum = j_values_sum + junc_dict_list[j][0]

#     if j_values_sum != 0.0:
#         # for the given iteration index of the junc with the maximum pressure
#         junc_max_index = j_values.index(max(j_values))

#         #===================================

#         # corresponding to junc with max pressure index of edge with max pressure
#         max_edge_index = list(junc_dict_list[junc_max_index][1].values()).index(max(list(junc_dict_list[junc_max_index][1].values())))
#         #id of the edge with max pressure
#         edge_key_max = list(junc_dict_list[junc_max_index][1].keys())[max_edge_index]
#         # the id of the junc with max pressure
#         junc_key_max = list(junc_dict.keys())[junc_max_index]
#         print('for every iteration max junc key: {} and value: {}'.format(junc_key_max, j_values[junc_max_index]))
#         print('for every iteration max edge corresponding to max junc key: {} and value: {}'.format(edge_key_max, list(junc_dict_list[junc_max_index][1].values())[max_edge_index]))

#         print("*********************************")

#         #tls json unpacking into keys and values
#         tls_keys = list(tlsdata.keys())
#         tls_values = list (tlsdata.values())

#         #reaching the target phase array corresponding to junc with maximum pressure
#         target_j_tls = tls_values[junc_max_index]
#         #reaching the target phase array corresponding to edge with maximum pressure
#         target_e_tls1 = target_j_tls[max_edge_index * 2]
#         target_e_tls2 = target_j_tls[max_edge_index * 2 + 1]

#         #selecting between both traffic phase definition to increase the time of the one with max 'g' or 'G'
#         if (target_e_tls1[1].count('r') < target_e_tls2[1].count('r')):
#             #change the time phase of first
#             target_e_tls1[0] = randint(1,10) #to be modified
#         else:
#             target_e_tls2[0] = randint(1,10) #to be modified


#     else:
#         print("donot need to alter")

#     print('=================================')
























