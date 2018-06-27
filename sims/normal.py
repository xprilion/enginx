from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random
import re
import webbrowser as wb

import json

try:
    sys.path.append("/home/xprilion/sumo-0.32.0/tools")  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join('home', 'xprilion', 'sumo-0.32.0')), "tools"))  # tutorial in docs
    from sumolib import checkBinary
    import sumolib
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci

def run():
    step = 0

    # wb.open_new_tab('http://localhost/enginx/sim3/monitor.html')

    total_wait_time = 0
    running_cars = 0

    while traci.simulation.getMinExpectedNumber() > 0:

        if step % 3 == 0:
            traci.gui.screenshot("View #0", "/var/www/html/enginx/sim3/storage/view.jpg")

        ### total_wait_time
        total_wait_time = 0
        loaded_cars = traci.simulation.getDepartedNumber()
        unloaded_cars = traci.simulation.getArrivedNumber()

        running_cars += loaded_cars
        running_cars -= unloaded_cars

        for i in range(100):
            try:
                total_wait_time += traci.vehicle.getAccumulatedWaitingTime("v"+str(i))
            except:
                pass

        # print(total_wait_time)

        try:
            avg_wait_time = float(total_wait_time) / float(running_cars)
        except:
            avg_wait_time = 0

        now_time = traci.simulation.getCurrentTime() / 1000

        data = {"value": round(avg_wait_time, 2)}
        with open('/var/www/html/enginx/sim3/storage/avg_wait_time.json', 'w') as outfile:
            json.dump(data, outfile)

        data = {"value": running_cars}
        with open('/var/www/html/enginx/sim3/storage/running_cars.json', 'w') as outfile:
            json.dump(data, outfile)

        data = {"value": now_time}
        with open('/var/www/html/enginx/sim3/storage/now_time.json', 'w') as outfile:
            json.dump(data, outfile)

        traci.simulationStep()
        step += 1

    traci.gui.screenshot("View #0", "/var/www/html/enginx/sim3/storage/view.jpg")

    data = {"state": 0}
    with open('/var/www/html/enginx/sim3/storage/run_state.json', 'w') as outfile:
        json.dump(data, outfile)

    data = {"value": 0.0}
    with open('/var/www/html/enginx/sim3/storage/avg_wait_time.json', 'w') as outfile:
        json.dump(data, outfile)
    data = {"value": 0}
    with open('/var/www/html/enginx/sim3/storage/running_cars.json', 'w') as outfile:
        json.dump(data, outfile)

    data = {"value": 0}
    with open('/var/www/html/enginx/sim3/storage/now_time.json', 'w') as outfile:
        json.dump(data, outfile)

    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


if __name__ == "__main__":

    random.seed(1)

    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    juncs = {}

    network = sumolib.net.readNet('data/normal/cross.net.xml')
    for jnc in network.getNodes():
        # desc = {"id": jnc.getID()}
        # print(jnc.getID())
        # juncs.append(jnc.getID())
        # print("Incoming: ", end="")
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

    traci.start([sumoBinary, "-c", "data/normal/cross.sumocfg",
                             "--tripinfo-output", "normal-trip.xml", "--additional-files", "data/normal/add.xml", "--start", "true"])

    for i in range(100):
        sei = random.randint(0, len(edgenames)-1)
        routelen = random.randint(0, 50)
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

    data = {"state": 1}
    with open('/var/www/html/enginx/sim3/storage/run_state.json', 'w') as outfile:
        json.dump(data, outfile)

    run()
