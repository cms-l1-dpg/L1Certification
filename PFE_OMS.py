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
import json
import textwrap
from collections import OrderedDict, defaultdict
from runInfo import OmsApi
from Config import ValidL1Keys, OMSObjectName, CosmicPlots
from functools import reduce
import operator
import argparse

api = OmsApi( None, False )
OMSpath = json.load(open("OMSPath.json", 'r'))

def GetOMSValue(path, runObject):
    return reduce(operator.getitem, path, runObject)

def OMSGetRate(run, bitmap):
    k = "l1algorithmtriggers"
    OMSObjects = api.getOmsObject( OMSObjectName[k].format(run ) )
    ratemap = {}
    for i in OMSObjects["data"]:
        for l1seed, bit in bitmap.items():
            if i["id"] == "%d_%d" % (run, bit):
                if l1seed != i["attributes"]["name"]:
                    print(l1seed,i["attributes"]["name"])
                ratemap[l1seed] = i["attributes"]["pre_dt_before_prescale_rate"]
    return ratemap

def OMSGetMissingKeys(data):
    keys = defaultdict(set)
    for r in data["L1PFE"]:
        keys[r['type']].update(OMSGetKeys(r['run']))

    restr = []
    for k, v in keys.items():
        m = "Missing keys for %s runs: %s\n" % (k, ", ".join(v - ValidL1Keys))
        restr+=textwrap.wrap(m, width=100)
    return "\n".join(restr)

def OMSGetKeys(run):
    global OMSpath
    k = "l1configurationKeys"
    OMSObjects = api.getOmsObject( OMSObjectName[k].format(run ) )

    keys=[]
    for k, v in OMSpath.items():
        keys.append(GetOMSValue(v["path"], OMSObjects))
    return keys

def OMSGetL1Key(run):
    k = "run"
    OMSObjects = api.getOmsObject( OMSObjectName[k].format(run ) )
    path = ["data", "attributes", "l1_key"]
    return GetOMSValue(path, OMSObjects)

def OMSGetBit(run, l1seeds):
    k = "l1algorithmtriggers"
    OMSObjects = api.getOmsObject( OMSObjectName[k].format(run ) )
    seedmap = {}
    for i in OMSObjects['data']:
        seedmap[i["attributes"]["name"]] = {
            "bit" : i["attributes"]["bit"],
            "prescale": i["attributes"]["initial_prescale"],
            "mask": i["attributes"]["mask"]
        }

    newmap = {}
    for l1 in l1seeds:
        if l1 in seedmap:
            newmap[l1] = seedmap[l1]
            if seedmap[l1]["bit"] != CosmicPlots[l1][0]:
                # print("Bit number is wrong in %s" % l1)
                # print(seedmap[l1]["bit"] , CosmicPlots[l1][0])
                CosmicPlots[l1][0] = seedmap[l1]["bit"] 
        else:
            newmap[l1] = {"bit" : -1, "prescale" : 0, "mask": True}

    return newmap

def OMSGetCosmicRates(runinfo):
    seedmap = OMSGetBit(runinfo['run'], CosmicPlots.keys())
    omsobj = "l1algoRateLS"
    restr = ""
    for k, v in seedmap.items():
        OMSObjects = api.getOmsObject( OMSObjectName[omsobj].format(runinfo['run'], v["bit"] ) )
        ratetype = "post_dt_hlt_rate"
        outline = "- {:<30} : ".format(k)
        if v["bit"] == -1:
            outline += "Not in menu"
            restr += outline+"\n"
            continue
        outline += "Not active, " if v["mask"] else ""
        if k == "L1_SingleEG8er2p5":
            ratetype = "pre_dt_before_prescale_rate"
            outline += "before prescale rate "
        else:
            outline += "prescale 0, " if v["prescale"] == 0 else ""
        outline += "%.3fHz " % OMSGetAverageRate(OMSObjects, ratetype, runinfo["LSs"])
        restr += outline+"\n"
    return restr

def OMSGetAverageRate(OMSObj, ratetype, LSs):
    lscnt = 0.0
    sumrate = 0.0
    for ls in OMSObj['data']:
        LumiSection = ls["attributes"]["lumisection_number"]
        rate = ls["attributes"][ratetype]
        for lsrange in LSs:
            if LumiSection >= lsrange[0] and LumiSection <= lsrange[1]:
                lscnt += 1
                sumrate += rate if rate is not None else 0.0
                break
    return sumrate/lscnt

if __name__ == "__main__":
    # OMSGetBit(319224, [""])
    # OMSGetKeys(319224)
    # OMSGetL1Key(319224)
    # OMSGetCosmicRates(319224)
    pass
