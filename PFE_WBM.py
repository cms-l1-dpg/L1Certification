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
from Config import PUPlots, CosmicPlots

def OpenRunSummary(run):
    wbmurl = 'https://cmswbm.cern.ch/cmsdb/servlet/RunSummary?RUN=%d&SUBMIT=Submit' % run
    webbrowser.open_new_tab(wbmurl)

def OpenL1Summary(run):
    ## It seems WBM can auto retrieve the L1Key from this url
    wbmurl = 'https://cmswbm.cern.ch/cmsdb/servlet/L1Summary?RUN=%d&KEY=l1_trg' % run
    webbrowser.open_new_tab(wbmurl)

def OpenL1withLS(run, fromLS, toLS):
    wbmurl = 'https://cmswbm.cern.ch/cmsdb/servlet/L1Summary?fromLS=%d&toLS=%d&RUN=%d&KEY=l1_trg' % (fromLS, toLS, run)
    webbrowser.open_new_tab(wbmurl)

def OpenL1RatewithLS(run, fromLS, toLS):
    wbmurl = 'https://cmswbm.cern.ch/cmsdb/servlet/ChartTriggerCounters?runID=%d&fromLSNumber=%d&toLSNumber=%d&scalerID4=1' % (run, fromLS, toLS)
    webbrowser.open_new_tab(wbmurl)

def OpenL1PUDepPlot(fill, L1Seed):
    wbmurl = 'https://cmswbm.cern.ch/rateplots/%d/MoreTriggers/png/%s.png' % (fill, L1Seed)
    webbrowser.open_new_tab(wbmurl)

def OpenBunchFill(fill):
    wbmurl = 'https://cmswbm.cern.ch/cmsdb/servlet/BunchFill?FILL=%d' % fill
    webbrowser.open_new_tab(wbmurl)

def OpenL1CosmisRate(run, fromLS, toLS, l1seed, bit):
    wbmurl = 'https://cmswbm.cern.ch/cmsdb/servlet/ChartL1TriggerRates?RUNID=%d&type=0&BITID=%d&LSLENGTH=23.31040958&TRIGGER_NAME=%s&fromLSNumber=%d&toLSNumber=%s&postDeadRatesHLT=1&' % (run, bit, l1seed, fromLS, toLS)
    webbrowser.open_new_tab(wbmurl)

def OpenL1CosmisRateBeforePrescale(run, fromLS, toLS, l1seed, bit):
    wbmurl = 'https://cmswbm.cern.ch/cmsdb/servlet/ChartL1TriggerRates?RUNID=%d&type=0&BITID=%d&LSLENGTH=23.31040958&TRIGGER_NAME=%s&fromLSNumber=%d&toLSNumber=%s&beforePrescale=1&' % (run, bit, l1seed, fromLS, toLS)
    webbrowser.open_new_tab(wbmurl)

def RunWBM(r):
    isCosmics = isCollision = False
    run = r['run']
    LS = eval(r['LS'])
    fill = r['fill']
    if fill == 0:
        isCosmics = True
    else:
        isCollision = True

#============================================================================#
#-------------------------     Start to Open WBM     ------------------------#
#============================================================================#
    ## Check Fill number
    OpenRunSummary(run)
    ## Check L1 Key, GTKeys etc
    ## TODO: Comparing keys to twiki is tedious! Unfortunately ssl
    ## certification is difficult to work with in Python
    # OpenL1Summary(run) 
    ## Check L1Ratew with selected Lumi Section
    OpenL1RatewithLS(run, LS[0], LS[1]) ##


    if isCollision:
        ## Check for PU dependency of Collision
        for l1seed in PUPlots:
            OpenL1PUDepPlot(fill, l1seed)
        ## Check for bunch fill, check pre/post firing with isolated bunch
        # OpenBunchFill(fill)

    if isCosmics:
        ## Check avg rate of cosmic L1Seeds
        for h, bit in CosmicPlots.items():
            if h == "L1_SingleEG8er2p5":
                OpenL1CosmisRateBeforePrescale(run, LS[0], LS[1], h, bit[0])
            else:
                OpenL1CosmisRate(run, LS[0], LS[1], h, bit[0])

if __name__ == "__main__":
    json_file = open("PFE.json", 'r')
    data = json.load(json_file)
    for r in data["L1PFE"]:
        RunWBM(r)
