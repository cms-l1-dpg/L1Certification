#!/usr/bin/env python

# File        : PFE_Prefiring.py
# Author      : Zhenbin Wu
# Contact     : zhenbin.wu@gmail.com
# Date        : 2018 Jul 05
#
# Description : This script is for the pre firing study
# Accessing the DQM file is herited from Emmanuel Francois Perez

from os.path import expanduser
from Config import PrefiringSeeds
from PFE_OMS import OMSGetRate
from collections import defaultdict

import subprocess
import os
import ROOT

def GetFile( run ) :
    base= "https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OnlineData/original/"
    s = str( run )
    fname = "DQM_V0001_L1T_R000"+ s + ".root"
    path = "000"+s[0]+s[1]+"xxxx/"
    path = path + "000"+s[0]+s[1]+s[2]+s[3]+"xx/" + fname
    cmd = "wget -c --no-check-certificate --private-key=keyout.pem  --certificate=%s/.globus/usercert.pem " % expanduser("~") \
            + base + path + " -O ./tmp/DQM_%s.root" % s
    os.system( cmd)

def ParseROOTFile(run):
    fname = "./tmp/DQM_%s.root" % run
    f =  ROOT.TFile(fname,"read")
    f.cd( "DQMData/Run "+str(run)+"/L1T/Run summary/L1TStage2uGT/" )
    g = ROOT.gDirectory.Get("Ratio_Unprescaled_First_Bunch_In_Train")
    ratemap = {}
    bitmap = {}
    for x in PrefiringSeeds:
        for i in range(1, g.GetNbinsY()+1):
            ybin = g.GetYaxis().GetBinLabel(i)
            if x in ybin:
                bitmap[x] = int(ybin[ybin.find("(")+1:ybin.find(")")])
                ratemap[x] = ""
                for j in range(1, g.GetNbinsX()+1):
                    ratemap[x] += " {:<10.3f}".format(g.GetBinContent(j, i))
                break
    omsrate = OMSGetRate(run, bitmap)
    for k in ratemap.keys():
        ratemap[k]+=" {:<25}".format(omsrate[k])

    # returnstr = "Timing studies for fill NNNN \n"
    # returnstr = "Run %d \n" % run
    returnstr ="{:<25} {:<10} {:<10} {:<10} {:<10} {:<10} {:<25}\n".\
            format("L1Seed", "-2 BX", "-1 BX", "0 BX", "1 BX", "2 BX", "Pre-DT rate before PS")
    for k,v in ratemap.items():
        returnstr += "{:<25}{}\n".format(k, v)
    return returnstr


def CheckPreFiringRun(run):
    GetFile(run)
    return ParseROOTFile(run)

def CheckPreFiringFill(data):
    if not os.path.exists("./tmp"):
        os.makedirs("./tmp")
    fillrun = defaultdict(list)
    outstr = ""
    for r in data["L1PFE"]:
        if "Collisions" in r['type']:
            fillrun[r['fill']].append(r['run'])
    fillcnt=0
    for f, runs in fillrun.items():
        fillcnt += 1
        outstr += "%d. Timing studies for fill %d \n" % (fillcnt, f)
        rcnt = 0
        for r in sorted(runs):
            rcnt += 1
            outstr += "%d.%d Run %d \n" % (fillcnt, rcnt, r)
            outstr += CheckPreFiringRun(r)
            outstr += "\n"
        outstr += "\n"
    return outstr


if __name__ == "__main__":
    GetFile(319254)
    t=ParseROOTFile(319254)
    print(t)
