#!/usr/bin/env python
# encoding: utf-8

# File        : PFE_Shifter.py
# Author      : Zhenbin Wu
# Contact     : zhenbin.wu@gmail.com
# Date        : 2018 Jul 05
#
# Description : The main script to run for the shifter

import os
import argparse
import json
import datetime

from PFE_WBM import RunWBM
from PFE_DQM import RunDQM
from PFE_Prefiring import CheckPreFiringFill
from PFE_OMS import OMSGetMissingKeys, OMSGetL1Key, OMSGetCosmicRates
from Config import PUPlots, CosmicPlots
from collections import defaultdict


def fprint(s):
    global outfile
    outfile.write(s+"\n")

def PrintCollisionElog(r):
    fprint('---------------------------------------------------------------------')
    fprint('')
    fprint("## Run %d (%s, fill %d) -- L1T %s" % (r['run'], r['type'], r['fill'], r['L1T']) )
    fprint('')
    fprint("Detector components: %s" % r['DetComp'])
    if r['LSs'] is None:
        fprint("No Physically meaningful LS range")
    else:
        fprint("Physically meaningful LS range: %s" % r['LSs'])
    fprint("L1 key: %s" % OMSGetL1Key(r['run']))
    fprint("")
    fprint("L1A Physics rate: <++>kHz")
    fprint("Average PU: <++>")
    fprint("")
    fprint("Rates as a function of pileup:")
    for p in PUPlots:
        fprint("- {:<30} : <++>".format(p))
    fprint("")
    fprint("")
    fprint("L1T DQM: <++>")
    fprint("L1TEMU DQM: <++>")
    fprint("")
    return True

def PrintCosmicElog(r):
    fprint('---------------------------------------------------------------------')
    fprint('')
    fprint("## %s Run : %d -- L1T %s" % (r['type'], r['run'], r['L1T']) )
    fprint('')
    fprint("Detector components: %s" % r['DetComp'])
    fprint("Physically meaningful LS range: %s" % r['LSs'])
    fprint("L1 key: %s" % OMSGetL1Key(r['run']))
    fprint("")
    fprint("L1A Physics rate: <++>Hz")
    fprint("")
    fprint("Individual rates:")
    # for k, v in CosmicPlots.items() :
        # fprint("%s: %s" % (k, v[1]))
    fprint(OMSGetCosmicRates(r))
    fprint("")
    fprint("L1T DQM: <++>")
    fprint("L1TEMU DQM: <++>")
    fprint("")
    return True

def PrintSummary(runinfo, runsum):
    fprint("=====================================================================")
    rtype = defaultdict(dict)
    for r in runinfo["L1PFE"]:
        rtype[r['type']][r['run']] = (r['start'], r['stop'])
    for k,v in rtype.items():
        firstrun = min(v.keys())
        lastrun = max(v.keys())
        fprint("First %s run (start time): %d (%s)" % (k, firstrun, v[firstrun][0]))
        fprint("Last %s run (stop time): %d (%s)" % (k, lastrun, v[lastrun][1]))
        fprint("")

    fprint(OMSGetMissingKeys(runinfo))

    fprint("")
    fprint("{:<10} {:<6} {:<25} {:<10} {:<15} {:<10} {:<30}".\
           format("Run", "#LS", "Group", "L1T Online", "L1Tmu Offline", "L1Tcalo", "Comments"))
    fprint("---------------------------------------------------------------------")
    for j in runsum:
        fprint(j)
    fprint("---------------------------------------------------------------------")
    fprint("")

if __name__ == "__main__":
    ## Parse input
    parser = argparse.ArgumentParser(description='Process some runs information.')
    parser.add_argument('json', default="PFE.json", nargs="?",
                        help='run info json for PFE_RR.py')
    args = parser.parse_args()
    json_file = open(args.json, 'r')
    data = json.load(json_file)

    ## Getting the elog file
    now = datetime.datetime.now()
    filename = "Elog_%s_%d%d.log" % (now.strftime("%m%d"), now.hour, now.minute)
    print("Preparing elog file %s : " % filename)

    ## Print out elog file
    runsum =[]
    with open(filename, 'w') as outfile:
        for r in data["L1PFE"]:
            runsum.append("{:<10} {:<6} {:<25} {:<10} {:<15} {:<10}". \
                          format(r['run'], r['lumicount'], r['type'], r['L1T'], "GOOD", "GOOD"))
        PrintSummary(data, runsum)

        for r in data["L1PFE"]:
            if "Cosmics" in r['type']:
                PrintCosmicElog(r)
            if "Collisions" in r['type']:
                PrintCollisionElog(r)
        outfile.write('---------------------------------------------------------------------\n')
        outfile.write('\n')
        outfile.write(CheckPreFiringFill(data))
        outfile.write('\n')
        outfile.write('---------------------------------------------------------------------\n')
        outfile.close()

    print("Elog file %s is ready! Open a new terminal to edit the file... " % filename)

    ## Start the shift
    raw_input("Press Enter to start the shift!")

    for r in data["L1PFE"]:
        raw_input("Ready to certify Run %d? Press Enter to start... " % r['run'] )
        RunWBM(r)
        RunDQM(r)
        raw_input("Done with certify Run %d? Press Enter to start next run." % r['run'] )
    print("You are almost done! Don't forget to post elog and sign off runs")
