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
from Config import ValidL1Keys, OMSObjectName
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
        path = ["data", "attributes", "l1_key"]
        keys.append(GetOMSValue(v["path"], OMSObjects))
    return keys
