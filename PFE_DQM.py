#!/usr/bin/env python
# encoding: utf-8

# File        : PFE_DQM.py
# Author      : Zhenbin Wu
# Contact     : zhenbin.wu@gmail.com
# Date        : 2018 May 10
#
# Description : 

import json
from time import sleep
import webbrowser

DQMPath = "https://cmsweb.cern.ch/dqm/online/start?runnr={};dataset=/Global/Online/ALL;sampletype=online_data;filter=all;referencepos=overlay;referenceshow=customise;referencenorm=True;referenceobj1=refobj;referenceobj2=none;referenceobj3=none;referenceobj4=none;search=;striptype=object;stripruns=;stripaxis=run;stripomit=none;workspace=Shift;size=M;root=00%20Shift/{};focus=;zoom=no;"
SummaryPath = "https://cmsweb.cern.ch/dqm/online/start?runnr={};dataset=/Global/Online/ALL;sampletype=online_data;filter=all;referencepos=overlay;referenceshow=customise;referencenorm=True;referenceobj1=refobj;referenceobj2=none;referenceobj3=none;referenceobj4=none;search=;striptype=object;stripruns=;stripaxis=run;stripomit=none;workspace=Summary"

if __name__ == "__main__":
    run_json = open("PFE.json", 'r')
    data = json.load(run_json)
    print("Launching DQM pages, take a break and come back for plots!")
    for r in data["L1PFE"]:
        print("Openning Run ", r['run'])
        dqmurl = SummaryPath.format(r['run'])
        webbrowser.open_new_tab(dqmurl)
        sleep(10)
        for folder in ["L1T", "L1TEMU"]:
            dqmurl = DQMPath.format(r['run'], folder)
            webbrowser.open_new_tab(dqmurl)
            sleep(10)
