from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
import time
import json

try:
    sys.path.append("/home/xprilion/sumo-0.32.0/tools")
    from sumolib import checkBinary
    import sumolib
except ImportError:
    sys.exit("please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true", default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


if __name__ == "__main__":

    random.seed(1)

    num_cars = 100

    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        # sumoBinary = checkBinary('sumo-gui')
        sumoBinary = checkBinary('sumo')


    # <tlLogic id="gneJ23" type="static" programID="0" offset="0">
    #     <phase duration="33" state="rrrGGgrrrGGg"/>
    #     <phase duration="3" state="rrryygrrryyg"/>
    #     <phase duration="6" state="rrrrrGrrrrrG"/>
    #     <phase duration="3" state="rrrrryrrrrry"/>
    #     <phase duration="33" state="GGgrrrGGgrrr"/>
    #     <phase duration="3" state="yygrrryygrrr"/>
    #     <phase duration="6" state="rrGrrrrrGrrr"/>
    #     <phase duration="3" state="rryrrrrryrrr"/>
    # </tlLogic>

    edgestore = "data/algo/tls.json"
    tlsstore = "data/parts/"

    with open(edgestore) as f:
        data = json.load(f)
        # print(data)
        o = ""

        for jnc in data.keys():

            o += "<tlLogic id=\""+jnc+"\" type=\"static\" programID=\"0\" offset=\"0\">\n"

            phases = data[jnc]
            for i in range(len(phases)):
                o += "<phase duration=\""+str(phases[i][0])+"\" state=\""+str(phases[i][1])+"\"/>\n"

            o += "</tlLogic>\n"

        with open(tlsstore+"part2.xml", "w") as g:
            g.write(o)

    filenames = ['part1.xml', 'part2.xml', 'part3.xml']
    with open('data/algo/cross.net.xml', 'w') as outfile:
        for fname in filenames:
            with open(tlsstore+fname) as infile:
                for line in infile:
                    outfile.write(line)

    juncs = {}

    network = sumolib.net.readNet('data/algo/cross.net.xml')
    for jnc in network.getNodes():
        desc = {}
        ine = [x.getID() for x in jnc.getIncoming()]
        desc["in"] = ine
        # print("Outgoing: ", end="")
        oue = [x.getID() for x in jnc.getOutgoing()]
        desc["out"] = oue

        # print(desc)

        juncs[jnc.getID()] = desc

    # print("\n--------------------------------------------------\n")

    edges = {}
    edgenames = []

    for edg in network.getEdges():
        desc = {}
        # desc = {"id": edg.getID()}
        desc["from"] = edg.getFromNode().getID()
        # print("Outgoing: ", end="")
        desc["to"] = edg.getToNode().getID()

        # print(desc)
        edgenames.append(edg.getID())

        edges[edg.getID()] = desc


    traci.start([sumoBinary, "-c", "data/algo/cross.sumocfg", "--tripinfo-output", "algo-trip.xml", "--additional-files", "data/algo/add.xml", "--start", "true", "-W", "false"])

    for i in range(num_cars):
        sei = random.randint(0, len(edgenames)-1)
        routelen = random.randint(5, 10)
        # routelen = random.randint(3, 6)

        cartrip = []

        cartrip.append(edgenames[sei])

        enow = edgenames[sei]

        for j in range(routelen):
            tojnc = edges[enow]["to"]
            randedg = random.randint(0, len(juncs[tojnc]["out"])-1)
            nedg = juncs[tojnc]["out"][randedg]
            while nedg.endswith(enow) or enow.endswith(nedg):
                randedg = random.randint(0, len(juncs[tojnc]["out"])-1)
                nedg = juncs[tojnc]["out"][randedg]

            cartrip.append(nedg)
            enow = nedg

        traci.route.add("trip"+str(i), cartrip)
        traci.vehicle.add("v"+str(i), "trip"+str(i), typeID="reroutingType",  depart= i+random.randint(0, 5*(i+1)))

    # data = {"state": 1}
    # with open('/var/www/html/enginx/sim3/storage/run_state.json', 'w') as outfile:
    #     json.dump(data, outfile)


    startTime = int(time.time())

    statefile = "data/algo/runs/"+str(startTime)+".json"

    step = 0

    # wb.open_new_tab('http://localhost/enginx/sim3/monitor.html')

    total_wait_time = 0
    running_cars = []

    nodestates = {}

    while traci.simulation.getMinExpectedNumber() > 0:

        # if step % 3 == 0:
        #     traci.gui.screenshot("View #0", "/var/www/html/enginx/sim3/storage/view.jpg")

        # total_wait_time

        junction_pressure = {}

        total_j_pressure = 0

        for jnc in juncs.keys():
            desc = 0

            links = traci.trafficlight.getControlledLinks(jnc)
            ins = []
            for l in links:
                if l[0][0] not in ins:
                    ins.append(l[0][0][:-2])

            # print(ins, juncs[jnc]["in"])


            try:
                pressures = [(traci.edge.getLastStepOccupancy(x) / 10) + ((traci.edge.getLastStepVehicleNumber(x) - traci.edge.getLastStepHaltingNumber(x))/traci.edge.getLastStepMeanSpeed(x)) + traci.edge.getLastStepHaltingNumber(x) * 2  for x in ins]
            except:
                pressures = [(traci.edge.getLastStepOccupancy(x) / 10) + (traci.edge.getLastStepVehicleNumber(x) - traci.edge.getLastStepHaltingNumber(x)) + traci.edge.getLastStepHaltingNumber(x) * 2  for x in ins]


            desc = sum(pressures) * 100 / len(pressures)

            total_j_pressure += desc

            pjuns = {}

            for i in range(len(ins)):
                pjuns[ins[i]] = pressures[i]

            junction_pressure[jnc] = [desc, pjuns]

        avg_jnc_pressure = total_j_pressure / len(juncs.keys())


        total_wait_time = 0
        loaded_cars = traci.simulation.getDepartedIDList()
        unloaded_cars = traci.simulation.getArrivedIDList()

        running_cars.extend(loaded_cars)
        running_cars = [x for x in running_cars if x not in unloaded_cars]


        for rcid in running_cars:
            try:
                total_wait_time += traci.vehicle.getAccumulatedWaitingTime(rcid)
            except:
                pass

        # print(total_wait_time)

        try:
            avg_wait_time = float(total_wait_time) / float(len(running_cars))
        except:
            avg_wait_time = 0

        now_time = traci.simulation.getCurrentTime() / 1000

        # data = {"value": round(avg_wait_time, 2)}
        # with open('/var/www/html/enginx/sim3/storage/avg_wait_time.json', 'w') as outfile:
        #     json.dump(data, outfile)

        # data = {"value": len(running_cars)}
        # with open('/var/www/html/enginx/sim3/storage/running_cars.json', 'w') as outfile:
        #     json.dump(data, outfile)

        # data = {"value": now_time}
        # with open('/var/www/html/enginx/sim3/storage/now_time.json', 'w') as outfile:
        #     json.dump(data, outfile)

        # data = {"value": round(avg_jnc_pressure, 3)}
        # with open('/var/www/html/enginx/sim3/storage/avg_jnc_pressure.json', 'w') as outfile:
        #     json.dump(data, outfile)


        # data = {"now_time": now_time, "pressures": junction_pressure}
        # with open(statefile, 'a+') as outfile:
        #     json.dump(data, outfile)
        #     outfile.write("\n")

        traci.simulationStep()
        step += 1

    # traci.gui.screenshot("View #0", "/var/www/html/enginx/sim3/storage/view.jpg")

    # data = {"state": 0}
    # with open('/var/www/html/enginx/sim3/storage/run_state.json', 'w') as outfile:
    #     json.dump(data, outfile)

    # data = {"value": 0.0}
    # with open('/var/www/html/enginx/sim3/storage/avg_wait_time.json', 'w') as outfile:
    #     json.dump(data, outfile)
    # data = {"value": 0}
    # with open('/var/www/html/enginx/sim3/storage/running_cars.json', 'w') as outfile:
    #     json.dump(data, outfile)

    # data = {"value": 0}
    # with open('/var/www/html/enginx/sim3/storage/now_time.json', 'w') as outfile:
    #     json.dump(data, outfile)

    # data = {"value": 0}
    # with open('/var/www/html/enginx/sim3/storage/avg_jnc_pressure.json', 'w') as outfile:
    #     json.dump(data, outfile)


    tls = {}

    for jnc in juncs.keys():
        desc = []

        tdef = traci.trafficlight.getCompleteRedYellowGreenDefinition(jnc)[0]

        for ph in tdef._phases:
            # print(type(ph), ph._duration // 1000, ph._phaseDef)
            # desc.append([ph._duration // 1000, ph._phaseDef])
            # desc.append([random.randint(3, 20), ph._phaseDef])
            desc.append([3, ph._phaseDef])

        # print(jnc, ": ", desc)

        tls[jnc] = desc

        # print("\n-----------------------------\n")

    with open(edgestore, 'w') as outfile:
        json.dump(tls, outfile)

    traci.close()
    sys.stdout.flush()

    from shutil import copyfile
    copyfile(statefile, "data/algo/last.json")
