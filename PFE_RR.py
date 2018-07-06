#!/usr/bin/env python
# encoding: utf-8

# File        : PFE_RR.py
# Author      : Zhenbin Wu
# Contact     : benwu@fnal.gov
# Date        : 2017 Oct 04
#
# Description : Script to read RR database and provide template for run elog


from __future__ import print_function
import sys
sys.path.append("/afs/cern.ch/user/v/valdo/public/")
from collections import defaultdict
import pprint
import argparse
import json
import io
try:
    import pandas as pd
except ImportError:
    raise ImportError('Need Pandas. Please setup CMSSW')

from rhapi import RhApi
DEFAULT_URL = "http://vocms00170:2113"
api = RhApi(DEFAULT_URL, debug = False)


class RunResgister():
    def __init__(self, run):
        self.run_ = run
        self.fill_ = None
        self.runtype_ = None
        self.L1TOnline_ = None
        self.DetComp_ = ""
        self.lumiRange = None
        self.lumicount = None
        self.createDate_ = None
        self.stopDate_ = None

    def CheckRunTime(self):
        q = "select r.RUNNUMBER, r.STARTTIME, r.STOPTIME from runreg_global.runs r where r.runnumber = :run"
        p = { "run"  : self.run_ }
        oucsv = api.csv(q, p)
        df = pd.read_csv(io.StringIO(oucsv.decode("UTF-8")))
        selrun = df.RUNNUMBER == self.run_
        if selrun.empty:
            print("Can NOT find this run %d! Please double check!" % self.run_)
            return False
        self.createDate_ = df.loc[selrun]['STARTTIME'].values[0]
        self.stopDate_ = df.loc[selrun]['STOPTIME'].values[0]

    def CheckSubSystem(self):
        q ="select r.run_number, r.run_class_name, r.RDA_CMP_CMS, r.RDA_CMP_L1T, r.RDA_CMP_CASTOR, r.RDA_CMP_CSC, \
                r.RDA_CMP_DT, r.RDA_CMP_ECAL, r.RDA_CMP_ES, r.RDA_CMP_HCAL, r.RDA_CMP_PIX, r.RDA_CMP_RPC, r.RDA_CMP_STRIP,  \
                r.RDA_CMP_CTPPS from runreg_global.datasets r where r.run_number = :run"
        p = { "run"  : self.run_ }
        oucsv = api.csv(q, p)
        df = pd.read_csv(io.StringIO(oucsv.decode("UTF-8")))
        return df


    def ParseSysdf(self, df):
        run = self.run_
        selrun = df.RUN_NUMBER == run
        self.runtype_ = df.loc[selrun]['RUN_CLASS_NAME'].values[0]
        self.L1TOnline_ = df.loc[selrun]['RDA_CMP_L1T'].values[0]

        typemap = {}
        for col in df:
            if "CMP" in col:
                if df.loc[selrun][col].values[0] != "GOOD":
                    typemap[col.split('_')[-1]] = df.loc[selrun][col].values[0]
        for k,v in typemap.items():
            if k == "CMS":
                continue
            self.DetComp_ += "%s %s, " % (k, v)


    def CheckRunLS(self):
        q ="select r.RLR_RUN_NUMBER, r.RLR_RANGE, r.RLR_SECTION_FROM, r.RLR_SECTION_TO, r.RLR_SECTION_COUNT, r.LHCFILL, \
                r.CMS_ACTIVE, r.BEAM1_STABLE, r.BEAM2_STABLE,  \
                r.BPIX_READY,  r.FPIX_READY, r.TECM_READY, r.TECP_READY, r.TIBTID_READY,r.TOB_READY,\
                r.CSCP_READY, r.CSCM_READY, r.DT0_READY,  r.DTP_READY, r.DTM_READY, r.RPC_READY \
                from runreg_global.run_lumis r where r.RLR_RUN_NUMBER = :run"
        p = { "run"  : self.run_ }
        oucsv = api.csv(q, p)
        df = pd.read_csv(io.StringIO(oucsv.decode("UTF-8")))
        return df


    def ParseLS(self, df):
        ## Get Fill Number
        if "Collisions" in self.runtype_:
            fills = df[(df.RLR_RUN_NUMBER == self.run_) & (df.BEAM1_STABLE == 1) & (df.BEAM2_STABLE==1)].LHCFILL.unique()
            if len(fills) != 1:
                print("No good! ", fills)
            else:
                self.fill_ = fills[0]

        goodLS = None
        ## Get Cosmics LS
        if "Cosmics" in self.runtype_:
            goodLS = df[ (df.RLR_RUN_NUMBER == self.run_) &
                ##At least one of the muon systems (Csc, Dt, Rpc) is active
               ( ((df.CSCM_READY == 1) & (df.CSCP_READY == 1) )  #CSC on
               | ((df.DT0_READY == 1) & (df.DTP_READY == 1)& (df.DTM_READY == 1))  # DT on
               | (df.RPC_READY == 1))
               ## Silicon strips are on and in
               & ((df.TECM_READY == 1) & (df.TECP_READY == 1)& (df.TIBTID_READY == 1) & (df.TOB_READY == 1))
              ]

        if "Collisions" in self.runtype_:
            goodLS =  df[(df.RLR_RUN_NUMBER == self.run_)
                         ## CMS is active
                         & (df.CMS_ACTIVE == 1)
                         ## Beam is stable
                         &( (df.BEAM1_STABLE == 1) & (df.BEAM2_STABLE==1))
                         ## Tracker is on
                         & ((df.TECM_READY == 1) & (df.TECP_READY == 1)& (df.TIBTID_READY == 1) & (df.TOB_READY == 1))
                        ]
        goodLS = goodLS.sort_values('RLR_RANGE')
        self.lumiRange = self.join_ranges(goodLS.RLR_SECTION_FROM.tolist(),  goodLS.RLR_SECTION_TO.tolist())
        self.lumicount = goodLS.RLR_SECTION_COUNT.sum()



    def join_ranges(self, LSFrom, LSTo):
        LSRange = []
        start = None
        end = None
        for i in xrange(len(LSFrom)):
            if start is None:
                start = LSFrom[i]
                end = LSTo[i]
                continue
            if LSFrom[i] == LSTo[i-1] +1:
                end = LSTo[i]
            else :
                LSRange.append([start, end])
                start = None
                end = None
        LSRange.append([start, end])
        return LSRange

    def PrintElog(self):
        if "Cosmics" in self.runtype_:
            return self.PrintCosmicElog()
        if "Collisions" in self.runtype_:
            return self.PrintCollisionElog()

    def PrintCollisionElog(self):
        print('---------------------------------------------------------------------')
        print('')
        print("## Run %d (%s, fill %d) -- L1T %s" % (self.run_, self.runtype_, self.fill_, self.L1TOnline_) )
        print('')
        print("Detector components: %s" % self.DetComp_)
        if self.lumiRange is None:
            print("No Physically meaningful LS range")
        else:
            print("Physically meaningful LS range: %s" % ", ".join(["%d-%d" % (i[0], i[1])for i in self.lumiRange]))
        print("L1 key <++> ")
        print("")
        print("L1A Physics rate: <++>kHz")
        print("Average PU: <++>")
        # print("")
        # print("Fill %d has no isolated bunch for pre/post firing study." % self.fill_)
        print("")
        print("Rates as a function of pileup:")
        print("- L1_SingleMu22: <++>")
        print("- L1_SingleJet180: <++>")
        print("- L1_ETM100: <++>")
        print("- L1_HTT300er: <++>")
        print("- L1_SingleEG40: <++>")
        print("- L1_SingleIsoEG34: <++>")
        print("- L1_DoubleIsoTau32er2p1: <++>")
        print("")
        print("")
        print("L1T DQM: <++>")
        print("L1TEMU DQM: <++>")
        print("")
        return "%d %d %s %s GOOD GOOD" % (self.run_, self.lumicount, self.runtype_, self.L1TOnline_)

    def PrintCosmicElog(self):
        print('---------------------------------------------------------------------')
        print('')
        print("## %s Run : %d -- L1T %s" % (self.runtype_, self.run_, self.L1TOnline_) )
        print('')
        print("Detector components: %s" % self.DetComp_)
        print("Physically meaningful LS range: %s" % ", ".join(["%d-%d" % (i[0], i[1])for i in self.lumiRange]))
        print("L1 key <++>")
        print("")
        print("L1A Physics rate: <++>kHz")
        print("")
        print("Individual rates:")
        print("L1_SingleMuCosmics: <+110-130Hz+>")
        print("L1_SingleMu7: <+20-25Hz+>")
        print("L1_SingleEG5: <+10-270Hz+>")
        print("L1_SingleJet35: <+0-100Hz+>")
        print("L1_SingleJet20er3p0_NotBptxOR: <+Active+>")
        print("L1_SingleMuOpen_NotBptxOR: <+Active+>")
        print("")
        print("L1T DQM: <++>")
        print("L1TEMU DQM: <++>")
        print("")
        return "%d %d %s %s GOOD GOOD" % (self.run_, self.lumicount, self.runtype_, self.L1TOnline_)

    def ReturnInfo(self):
        remap = {}
        remap['run'] = self.run_
        remap['fill'] = self.fill_ if "Collisions" in self.runtype_ else 0
        remap['LS'] = '[%d, %d]' % (self.lumiRange[0][0], self.lumiRange[-1][-1])
        remap['LSs'] = self.lumiRange
        remap['type'] = self.runtype_
        remap['start'] = self.createDate_
        remap['stop'] = self.stopDate_
        remap['L1T'] = self.L1TOnline_
        remap['DetComp'] = self.DetComp_
        remap['lumicount'] = self.lumicount
        return remap

    def Run(self):
        validrun = self.CheckRunTime()
        if validrun:
            return False
        self.ParseSysdf(self.CheckSubSystem())
        self.ParseLS(self.CheckRunLS())
        return True
        # return self.PrintElog()


def PrintSummary(runinfo, runsum):
    print("=====================================================================")
    rtype = defaultdict(dict)
    for r in runinfo["L1PFE"]:
        rtype[r['type']][r['run']] = (r['start'], r['stop'])
    for k,v in rtype.items():
        firstrun = list(v.keys())[-1]
        lastrun = list(v.keys())[0]
        print("First %s run (start time): %d (%s)" % (k, firstrun, v[firstrun][0]))
        print("Last %s run (stop time): %d (%s)" % (k, lastrun, v[lastrun][1]))
        print("")

    for k in rtype.keys():
        print("Missing keys for %s runs:" % k)

    print("")
    print("Run    #LS Group         L1T Online L1Tmu Offline L1Tcalo Comments")
    print("---------------------------------------------------------------------")
    for j in runsum:
        print(j)
    print("---------------------------------------------------------------------")
    print("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some runs information.')
    parser.add_argument('runs', metavar='N', type=int, nargs='+',
                        help='run numbers for PFE')

    args = parser.parse_args()
    runs = args.runs
    runinfo = defaultdict(list)
    
    for r in runs:
        rr = RunResgister(r)
        validrun = rr.Run()
        if validrun:
            runinfo["L1PFE"].append(rr.ReturnInfo())

    with open('PFE.json', 'w') as f:
        json.dump(runinfo, f)
