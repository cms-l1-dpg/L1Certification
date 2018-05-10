#!/usr/bin/env python
# encoding: utf-8

# File        : WBM.py
# Author      : Zhenbin Wu
# Contact     : zhenbin.wu@gmail.com
# Date        : 2017 Oct 03
#
# Description : Script to open the WBM for L1 PFE

import urllib2
import webbrowser
import ssl
import requests
import json
from collections import OrderedDict
from runInfo import OmsApi
from functools import reduce
from L1Run import L1Run
import operator
import argparse

PUPlots = [
'L1_SingleMu22',
'L1_SingleJet180',
'L1_ETM100',
'L1_HTT300er',
'L1_SingleEG40',
'L1_SingleIsoEG34',
'L1_DoubleIsoTau32er2p1'
]

CosmicPlots = OrderedDict([
    ('L1_SingleMuCosmics' , 0),
    ('L1_SingleMu7', 10),
    ('L1_SingleEG5' , 50),
    ('L1_SingleJet35' , 133),
    ('L1_SingleJet20er3p0_NotBptxOR' , 207),
    ('L1_SingleMuOpen_NotBptxOR', 205)
])

OMSObjectName = {
    "run" : "runs/{}",
    "l1configurationKeys" : "runs/{}/l1configurationKeys"
}

def GetOMSValue(path, runObject):
    return reduce(operator.getitem, path, runObject)

if __name__ == "__main__":
    # parser = argparse.ArgumentParser( description='python example script to get run info from OMSAPI', formatter_class=argparse.ArgumentDefaultsHelpFormatter )
    # parser.add_argument( 'json', help='input json file with run number to get info for', default="PFE.json")
    # parser.add_argument( "-s", "--server", help = "server URL, default=" + OmsApi.defaultServer(), default=None )
    # args = parser.parse_args()
    api = OmsApi( None, False )
    # api = OmsApi( args.server, True )

    run_json = open("PFE.json", 'r')
    # run_json = open(args.json, 'r')
    data = json.load(run_json)
    OMSpath = json.load(open("OMSPath.json", 'r'))
    runmap = {}

    for r in data["L1PFE"]:
        run = r['run']
        LS = eval(r['LS'])
        runmap[run] = L1Run(run, r['type'])
        l1 = runmap[run]
        l1.fill =r['fill']
        isCosmics = isCollision = False
        if l1.fill == 0:
            isCosmics = True
            if "Cosmics" not in l1.runType:
                print("Error! Wrong type?")
        else:
            isCollision = True
            if "Collision" not in l1.runType:
                print("Error! Wrong type?")
#============================================================================#
#-------------------------     Start the PFE Shift   ------------------------#
#============================================================================#
        OMSObjects = {}
        for k, v in OMSObjectName.items():
            # print (k, v, v.format(run ) )
            OMSObjects[k] = api.getOmsObject( v.format(run ) )

        ## 
        for k, v in OMSpath.items():
            path = ["data", "attributes", "l1_key"]
            runmap[run].AddKeys(k, GetOMSValue(v["path"], OMSObjects[v["Object"]]))
        print(runmap[run].keys)

    cosmickeys= set()
    collisionkeys= set()
    for r, l in runmap.items():
        if l.fill == 0 :
            cosmickeys.update(l.keys.values())
        else:
            collisionkeys.update(l.keys.values())

    print("Cosmics keys" , cosmickeys)
    print("Collision Keys" , collisionkeys)

        # ## Check Fill number
        # OpenRunSummary(run)
        # ## Check L1 Key, GTKeys etc
        # ## TODO: Comparing keys to twiki is tedious! Unfortunately ssl
        # ## certification is difficult to work with in Python
        # OpenL1Summary(run) 
        # ## Check L1Ratew with selected Lumi Section
        # OpenL1RatewithLS(run, LS[0], LS[1]) ##


        # if isCollision:
            # ## Check for PU dependency of Collision
            # for l1seed in PUPlots:
                # OpenL1PUDepPlot(fill, l1seed)
            # ## Check for bunch fill, check pre/post firing with isolated bunch
            # OpenBunchFill(fill)

        # if isCosmics:
            # ## Check avg rate of cosmic L1Seeds
            # for h, bit in CosmicPlots.items():
                # OpenL1CosmisRate(run, LS[0], LS[1], h, bit)
