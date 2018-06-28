# Welcome, to the world's coolest learner algorithm

import json

lastfile = "data/algo/last.json"
tlsfile = "data/algo/tls.json"

rundata = []

with open(lastfile, "r") as l:
	for line in l:
		rundata.append(json.loads(line))

with open(tlsfile, "r") as t:
	tlsdata = json.load(t)

for r in rundata:
	print(r)

print("\n\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n\n")

print(tlsdata)

