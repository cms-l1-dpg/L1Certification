## Script to open AutoDQM pages for multiple runs
## Suggest to open a new browser window before running,
## and also open a new browser after reference DQM pages open
## python3 URL_AutoDQM.py

import sys
import argparse
import subprocess
import select
import re
import webbrowser
import time


##############################################################
###  Default options, can be modified at the command line  ###
##############################################################

URL_BASE = 'https://cmsweb-testbed.cern.ch/dqm/autodqm/plots'
# URL_BASE = 'http://abrinke1autodqm.cern.ch:8083/dqm/autodqm/plots'
SOURCE    = 'Online'
SUBSYSTEM = 'L1T_shift'
DATA_ERA = 'Run2022'
REF_ERA  = 'Run2018'
DATASET  = 'SingleMuon'
## Long runs from the end of July 2022
## https://cmsoms.cern.ch/cms/fills/summary?cms_date_to=2022-07-31&cms_date_from=2022-07-01&cms_fill_stableOnly=true&cms_fill_protonsOnly=true
DATA_RUNS = '356071, 356077, 356323, 356378, 356381'
## 10 hour run from the end of 2018
REF_RUN = '325022'
## 10 "good" runs from last 5 fills in 2018 (7324, 7328, 7331, 7333, 7334)
## https://cmsoms.cern.ch/cms/fills/summary?cms_date_to=2018-10-31&cms_date_from=2018-10-20&cms_fill_stableOnly=true&cms_fill_protonsOnly=true
## https://docs.google.com/spreadsheets/d/1KS-mHbLVmxiocp4PnWI6V-epQy9pJnHFUhu-8uEBODM
REF_RUNS = '324997, 325001, 325022, 325057, 325097, 325099, 325117, 325159, 325170, 325172'

## Mapping of subsystem to locations in Online DQM
DQM_MAP = {
    #'L1T_shift': 'L1T;root=Quick%20collection',
    'L1T_shift'    : 'Shift;size=L;root=00%20Shift/L1T',
    'L1TEMU_shift' : 'Shift;size=L;root=00%20Shift/L1TEMU',
    'L1T_shift/Efficiency'    : 'Shift;size=XL;root=00%20Shift/L1T/Efficiency',
    'L1T_shift/Resolution'    : 'Shift;size=XL;root=00%20Shift/L1T/Resolution',
    'EMTF'         : 'Everything;root=L1T/L1TStage2EMTF',
    'DT'           : 'Everything;root=DT/02-Segments',
    'NULL'         : 'Everything'
}


## *** Supporting functions for constructing Online and Offline DQM URLs ***

def form_online_dqm_url(dRun, rRun, subsystem, refNormalize=True):
    if not subsystem in DQM_MAP.keys():
        subsystem = 'NULL'
    dqm_url = 'https://cmsweb.cern.ch/dqm/online/start?runnr=%s;' % dRun
    dqm_url += 'dataset=/Global/Online/ALL;sampletype=online_data;filter=all;'
    dqm_url += 'referencepos=overlay;referenceshow=all;referencenorm=%s;' % (refNormalize)
    for iRef in range(min(4, len(rRun.split('_')))):
        dqm_url += 'referenceobj%d=other%%3A%s%%3A%%3A%%3A;' % (iRef+1, rRun.split('_')[iRef])
    dqm_url += 'search=;striptype=object;stripruns=;stripaxis=run;stripomit=none;'
    dqm_url += 'workspace=%s;focus=;zoom=no;' % DQM_MAP[subsystem]

    return dqm_url


# ## Not yet ready (AWB 2022.07.29)
# def form_offline_dqm_url(dRun, rRun, dataset, subsystem):
#     dqm_url = 'https://cmsweb.cern.ch/dqm/offline/start?runnr=%s;' % dRun
#     dqm_url += 'dataset=/%s/Run2018D-PromptReco-v2/DQMIO;sampletype=offline_data;filter=all;' % dataset
#     dqm_url += 'referencepos=overlay;referenceshow=all;referencenorm=True;'
#     for iRef in range(min(4, len(rRun.split('_')))):
#         dqm_url += 'referenceobj%d=other%%3A%s%%3A%%3A%%3A/%s/Run2018D-PromptReco-v2/DQMIO%%3A%%3A;' % (iRef+1, rRun.split('_')[iRef])
#     dqm_url += 'search=;striptype=object;stripruns=;stripaxis=run;stripomit=none;'
#     dqm_url += 'workspace=%s;size=M;root=Quick%%20collection;focus=;zoom=no;' % subsystem.split('_')[0]

#     return dqm_url

def form_offline_dqm_url(dRun, rRun, dRun_dataset, rRun_dataset, dRun_era, rRun_era, workspace, refNormalize=True):
    
    # https://cmsweb.cern.ch/dqm/offline/start?runnr=367355;dataset=/Muon0/Run2023C-PromptReco-v1/DQMIO;sampletype=offline_data;filter=all;referencepos=overlay;referenceshow=customise;referencenorm=True;referenceobj1=other%3A362696%3A/Muon/Run2022G-PromptReco-v1/DQMIO%3A%3A;referenceobj2=other%3A325170%3A/SingleMuon/Run2018D-PromptReco-v2/DQMIO%3A%3A;referenceobj3=none;referenceobj4=none;search=;striptype=object;stripruns=;stripaxis=run;stripomit=none;workspace=Shift;size=XL;root=00%20Shift/L1T/Efficiency;focus=;zoom=no;.
    
    dRun_era_1             = dRun_era.replace('-', '_')
    dRun_era_toUse         = dRun_era_1.split('_')[0]
    dRun_era_version_toUse = dRun_era_1.split('_')[-1] if '_' in dRun_era_1 else 'v1'
    #print(f"{dRun_era = }, {dRun_era_toUse = }, { = }, ")
    
    rRun_list = rRun.split('_')
    rRun_list_toUse = [
        #['362696', '/%s/Run2022G-PromptReco-v1/DQMIO' % ('Muon'       if 'Mu' in dataset else 'EGamma')],
        #['325170', '/%s/Run2018D-PromptReco-v2/DQMIO' % ('SingleMuon' if 'Mu' in dataset else 'EGamma')]
    ]
    if len(rRun_list) > 0:
        rRun_era_1             = rRun_era.replace('-', '_')
        rRun_era_toUse         = rRun_era_1.split('_')[0]
        rRun_era_version_toUse = rRun_era_1.split('_')[-1] if '_' in rRun_era_1 else 'v1'
        for iRefRun in range(len(rRun_list)):
            rRun_list_toUse.append([str(rRun_list[iRefRun]), '/%s/%s-PromptReco-%s/DQMIO' % (rRun_dataset, rRun_era_toUse, rRun_era_version_toUse)])
    
    dqm_url = 'https://cmsweb.cern.ch/dqm/offline/start?runnr=%s;' % dRun
    dqm_url += 'dataset=/%s/%s-PromptReco-%s/DQMIO;sampletype=offline_data;filter=all;' % (dRun_dataset, dRun_era_toUse, dRun_era_version_toUse)
    dqm_url += 'referencepos=overlay;referenceshow=all;referencenorm=%s;' % (refNormalize)
        
    #for iRef in range(min(4, len(rRun.split('_')))):
    #    dqm_url += 'referenceobj%d=other%%3A%s%%3A%%3A%%3A/%s/Run2018D-PromptReco-v2/DQMIO%%3A%%3A;' % (iRef+1, rRun.split('_')[iRef])    
    for iRef in range(min(4, len(rRun_list_toUse))):
        dqm_url += 'referenceobj%d=other%%3A%s%%3A%s%%3A%%3A;' % (iRef+1, rRun_list_toUse[iRef][0], rRun_list_toUse[iRef][1])
        
    dqm_url += 'search=;striptype=object;stripruns=;stripaxis=run;stripomit=none;'
    dqm_url += 'workspace=%s;focus=;zoom=no;' % DQM_MAP[workspace] 
    
    return dqm_url



## Online Monitoring System (OMS) url
def form_oms_url(dRun):
    # https://cmsoms.cern.ch/cms/triggers/l1_rates?cms_run=367267&props.11273_11270.selectedCells=L1A%20physics:2&props.11275_11270.selectedCells=Total:2&props.11274_11270.selectedCells=24:512,63:512,101:512,168:512,194:512,206:512,226:512,270:512,309:512,313:512,336:512,386:512,404:512
    #oms_url = f'https://cmsoms.cern.ch/cms/triggers/l1_rates?cms_run={str(dRun)}&props.11273_11270.selectedCells=L1A%20physics:2&props.11275_11270.selectedCells=Total:2&props.11274_11270.selectedCells=24:512,63:512,101:512,168:512,194:512,206:512,226:512,270:512,309:512,313:512,336:512,386:512,404:512'
    oms_url = f'https://cmsoms.cern.ch/cms/triggers/l1_rates?cms_run={str(dRun)}&props.11273_11270.selectedCells=L1A%20physics:2&props.11275_11270.selectedCells=Total:2&props.11274_11270.selectedCells=24:512,63:512,101:512,168:512,194:512,206:512,226:512,270:512,309:512,313:512,336:512,386:512,404:512&props.19391_19388.selectedCells=L1A%20physics:2&props.19393_19388.selectedCells=Total:2'

    return oms_url
    

## Online Monitoring System (OMS) url
def form_oms_dcs_url(dRun):
    # https://cmsoms.cern.ch/cms/triggers/l1_rates?cms_run=367267&props.11273_11270.selectedCells=L1A%20physics:2&props.11275_11270.selectedCells=Total:2&props.11274_11270.selectedCells=24:512,63:512,101:512,168:512,194:512,206:512,226:512,270:512,309:512,313:512,336:512,386:512,404:512
    # https://cmsoms.cern.ch/cms/runs/lumisection?cms_run=368229&cms_run_sequence=GLOBAL-RUN
    oms_url = f'https://cmsoms.cern.ch/cms/runs/lumisection?cms_run={str(dRun)}&cms_run_sequence=GLOBAL-RUN' 

    return oms_url

## Online Monitoring System (OMS) url
def form_oms_runreport_url(dRun):
    # https://cmsoms.cern.ch/cms/runs/report?cms_run=370307&cms_run_sequence=GLOBAL-RUN
    oms_url = f'https://cmsoms.cern.ch/cms/runs/report?cms_run={str(dRun)}&cms_run_sequence=GLOBAL-RUN'

    return oms_url



###############################################################
###  Open AutoDQM web pages according to specified options  ###
###############################################################

if __name__ == '__main__':

    print('\n\n*** Inside URL_AutoDQM.py ***\n')

    ## Parse command line options
    parser = argparse.ArgumentParser(description='To open AutoDQM pages for multiple runs, run: python3 URL_AutoDQM.py')
    parser.add_argument('-url',  '--url_base',  type=str, default=URL_BASE,  help='AutoDQM web address')
    parser.add_argument('-src',  '--source',    type=str, default=SOURCE,    help='DQM source (Online or Offline)')
    parser.add_argument('-sub',  '--subsystem', type=str, default=SUBSYSTEM, help='Subsystem configuration (e.g. CSC, EMTF)')
    parser.add_argument('-eraD', '--data_era',  type=str, default=DATA_ERA,  help='Era ("series") for data run (e.g. Run2022)')
    parser.add_argument('-eraR', '--ref_era',   type=str, default=REF_ERA,   help='Era ("series") for reference run (e.g. Run2018)')
    parser.add_argument('-pd',   '--dataset',   type=str, default=DATASET,   help='Primary dataset ("sample") (e.g. SingleMuon)')
    parser.add_argument('-runD', '--data_runs', type=str, default=DATA_RUNS, help='Data run(s), separated by , or _ (no spaces!)')
    parser.add_argument('-runR', '--ref_runs',  type=str, default=REF_RUN,   help='Reference run(s), separated by , or _ (no spaces!)')
    parser.add_argument('-maxR', '--max_ref',   type=int, default=-1,        help='Maximum number of reference runs to use for each data run')
    parser.add_argument('-slp',  '--sleep',     type=int, default=15,        help='Wait time between opening new tabs')
    
    parser.add_argument('-mult', '--multiref',  action='store_true', help='Compare each data run to multiple references simultaneously')
    parser.add_argument('-rec',  '--recursive', action='store_true', help='Use other data runs as reference runs')
    parser.add_argument('-pre',  '--prev_ref',  action='store_true', help='Use only reference runs prior to data run')
    parser.add_argument('-dqmD', '--dqm_data',  action='store_true', help='Open Online or Offline DQM pages for each data run')
    parser.add_argument('-dqmR', '--dqm_ref',   action='store_true', help='Open Online or Offline DQM pages for each reference run')
    parser.add_argument('-NoDqmOf', '--NoDqm_offline',  action='store_true', help='Do not open Offline DQM pages for each data run')
    parser.add_argument('-omsD', '--oms_data',  action='store_true', help='Open OMS page for each data run')
    parser.add_argument('-deb',  '--debug',     action='store_true', help='Only print URLs and do not open them')
    parser.add_argument('-vrb',  '--verbose',   action='store_true', help='Include verbose printouts')

    args = parser.parse_args()

    ## Extract data and reference run lists
    data_run_str = args.data_runs
    ref_run_str  = args.ref_runs if not args.recursive else args.data_runs
    ## When running "recursively", include a few extra reference runs to validate the first data runs
    if args.recursive and args.ref_runs != REF_RUN:
        ref_run_str += (','+args.ref_runs)

    data_runs, ref_runs = None, None
    ## If list has a '.' in it, probably an input file
    for in_run_str in [data_run_str, ref_run_str]:
        if '.' in in_run_str or '/' in in_run_str:
            try:
                print('\nReading input file %s' % in_run_str)
                with open(in_run_str) as in_file:
                    in_text = in_file.readlines()
                    in_runs = [re.sub("[^0-9]", "", r) for r in in_text]
                    in_file.close()
                if in_run_str == data_run_str:
                    data_runs = [r for r in in_runs if len(r) == 6 and int(r) > 100000]
                    if args.prev_ref:
                        data_runs.sort()
                else:
                    ref_runs = [r for r in in_runs if len(r) == 6 and int(r) > 100000]
                if args.recursive:
                    ref_runs = data_runs.copy()
                    break
            except:
                print('\nCannot parse input file %s, or file does not exist.' % in_run_str)
                print('"data_runs" or "ref_runs" contained a "." or "/", so it is a file, right?')
                sys.exit()

    ## Otherwise, parse input runs as a list from the command line
    try:
        if not data_runs: data_runs = [r for r in re.split('\W+|_', data_run_str) if len(r) == 6 and int(r) > 100000]
        if not ref_runs:  ref_runs  = [r for r in re.split('\W+|_', ref_run_str)  if len(r) == 6 and int(r) > 100000]
        if args.multiref and args.ref_runs == REF_RUN and not args.recursive:
            ref_runs = [r for r in re.split('\W+|_', REF_RUNS)  if len(r) == 6 and int(r) > 100000]
    except:
        print('\nCannot parse data_runs (%s) or ref_runs (%s or %s)' % (data_run_str, ref_run_str, REF_RUNS))
        print(re.split('\W+|_', data_run_str))
        print(re.split('\W+|_', ref_run_str))
        print(re.split('\W+|_', REF_RUNS))
        sys.exit()

    print('\nFull list of data runs is:')
    print(data_runs)
    print('\nFull list of reference runs is:')
    print(ref_runs)

    ## Warnings about opening central DQM pages (AWB 2022.07.29)
    if args.dqm_data or args.dqm_ref:
        if not args.subsystem in DQM_MAP.keys():
            print('\nWARNING: dqm_data and dqm_ref options do not work for %s subsystem! Will open top level page instead.' % args.subsystem)
        if args.source != 'Online':
            print('\nWARNING: dqm_data and dqm_ref only work for Online DQM. Will open Online DQM page.')

    ## Open DQM pages for reference runs
    if args.dqm_ref and not args.recursive:
        print('\n\n***** PLEASE OPEN A NEW BROWSER WINDOW NOW! *****')
        print('Will wait 15 seconds, or until you hit "Enter"')
        try:
            #aa, bb, cc = select.select( [sys.stdin], [], [], 15 )
            #[line.readline() for line in aa]  ## Necessary for second select.select below to work  # Siddhesh: Does not work on Windows OS
            subprocess.call('read -t 15', shell=True)
        except:
            print('Skipped "reading input from perminal with timeout"')

        for rRun in ref_runs:
            ## For now, only open Online DQM even if AutoDQM is running on Offline DQM (AWB 2022.07.29)
            firstRun = (1 if rRun == ref_runs[0] else 0)
            dqm_url = form_online_dqm_url(rRun, '', args.subsystem)
            print('\n*** Opening Online DQM for reference run %s ***' % rRun)
            print(dqm_url)
            if not args.debug:
                webbrowser.open(dqm_url, new=firstRun, autoraise=False)
                time.sleep(1)


    print('\n\n***** PLEASE OPEN A NEW BROWSER WINDOW NOW! *****')
    print('Will wait 15 seconds, or until you hit "Enter"')
    try:
        #xx, yy, zz = select.select( [sys.stdin], [], [], 15 ) # Siddhesh: Does not work on Windows OS
        subprocess.call('read -t 15', shell=True)
    except:
        print('Skipped "reading input from perminal with timeout"')


    # https://stackoverflow.com/questions/60647891/wsastartup-error-10093-when-calling-exiftool-through-pyexiftool
    # https://stackoverflow.com/questions/1335507/keyboard-input-with-timeout
    
    ## *** Loop over data runs and open web pages *** 
    for dRun in data_runs:

        ## Pick one or more reference runs
        if args.prev_ref:
            ## Select only reference runs earlier than data, sorted highest to lowest
            ref_runs_int = [int(r) for r in ref_runs if int(r) < int(dRun)]
            ref_runs_int.sort(reverse=True)
            if len(ref_runs_int) == 0:
                print('\n*** Found no reference runs prior to %s - skipping ***' % dRun)
                continue
            if args.multiref:
                rRun = '_'.join([str(r) for r in ref_runs_int])
            else:
                rRun = str(ref_runs_int[0])
        elif args.multiref:
            ## Concatenate all reference runs
            rRun = '_'.join([r for r in ref_runs if r != dRun])
        elif args.prev_ref:
            ## Choose closest earlier run as reference
            rRun = str(ref_RunsI[0])
        elif args.recursive:
            ## Choose previous run in list as reference
            rRun = ref_runs[ref_runs.index(dRun) - 1]
        else:
            ## Choose reference run with same position in list as data run
            rRun = ref_runs[data_runs.index(dRun) % len(ref_runs)]

        ## If numer of reference runs is limited, truncate to first N in list
        if args.max_ref > 0:
            rRun = rRun[:(7*args.max_ref - 1)]

        if args.verbose:
            print('\nComparing dRun %s vs. rRun %s' % (dRun, rRun))

        ## Define the series and sample strings
        if args.source == 'Online':
            dSer  = '000'+dRun[:2]+'xxxx'
            dSamp = '000'+dRun[:4]+'xx'
            rSer  = '000'+rRun[:2]+'xxxx'
            rSamp = '000'+rRun[:4]+'xx'
        else:
            dSer  = args.data_era
            dSamp = args.dataset
            rSer  = args.ref_era if not args.recursive else args.data_era
            rSamp = args.dataset
            if (dSer[:6] == 'Run202' and int(dRun) < 350000) or (dSer[:6] == 'Run201' and int(dRun) > 330000):
                print('\n\nERROR! data_era %s does not seem to match run %s. Quitting.\n\n' % (dSer, dRun))
                sys.exit()
            if (rSer[:6] == 'Run202' and int(rRun[:6]) < 350000) or (rSer[:6] == 'Run201' and int(rRun[:6]) > 330000):
                print('\n\nERROR! ref_era %s does not seem to match run %s. Quitting.\n\n' % (rSer, rRun))
                sys.exit()

        ## Construct the AutoDQM URL and open the web browser
        auto_url = '/'.join( [args.url_base, args.source, args.subsystem,
                              rSer, rSamp, rRun, dSer, dSamp, dRun] )

        
        firstRun = (1 if dRun == data_runs[0] else 0)
        print('\n\n***** Opening Monitoring links for data run %s, reference run(s) %s ***' % (dRun, rRun.replace('_', ', ')))

        ## Construct OMS url and open the web browser for data runs            
        if args.oms_data:
            oms_runreport_url = form_oms_runreport_url(dRun)
            print('\n*** Opening Online OMS Run Report for data run %s' % (dRun))
            print(oms_runreport_url)
            if not args.debug:
                webbrowser.open(oms_runreport_url, new=firstRun, autoraise=False)
                firstRun=0
                
            oms_dcs_url = form_oms_dcs_url(dRun)
            print('\n*** Opening Online OMS DCS status for data run %s' % (dRun))
            print(oms_dcs_url)
            if not args.debug:
                webbrowser.open(oms_dcs_url, new=firstRun, autoraise=firstRun)

            oms_url = form_oms_url(dRun)
            print('\n*** Opening Online OMS for data run %s' % (dRun))
            print(oms_url)
            if not args.debug:
                webbrowser.open(oms_url, new=firstRun, autoraise=firstRun)
                

        print('\n*** Opening AutoDQM for data run %s, reference run(s) %s ***' % (dRun, rRun.replace('_', ', ')))
        print(auto_url)        
        if not args.debug:
            webbrowser.open(auto_url, new=firstRun, autoraise=firstRun)

        ## Construct the central DQM URL and open the web browser for data runs
        if args.dqm_data:
            ## For now, only open Online DQM even if AutoDQM is running on Offline DQM (AWB 2022.07.29)
            dqm_url = form_online_dqm_url(dRun, rRun, args.subsystem)
            print('\n*** Opening Online DQM for data run %s, reference run(s) %s ***' % (dRun, ', '.join(rRun.split('_')[:4])))
            print(dqm_url)
            if not args.debug:
                webbrowser.open(dqm_url, new=0, autoraise=False)

            if 'L1T' in args.subsystem:
                dqm_url_L1TEmu = form_online_dqm_url(dRun, rRun, 'L1TEMU_shift', refNormalize=False)  
                print(dqm_url_L1TEmu)
                if not args.debug:
                    webbrowser.open(dqm_url_L1TEmu, new=0, autoraise=False)

                if not args.NoDqm_offline:
                    
                    # set dataset name - part1
                    dRun_dataset_Mu = rRun_dataset_Mu = 'Muon'
                    dRun_dataset_EG = rRun_dataset_EG = 'EGamma'
                    dRun_dataset_Ext = rRun_dataset_Ext = ''
                    for era_toCheck in [
                            'Run2023A','Run2023B','Run2023C','Run2023D','Run2023G',
                            'Run2024B','Run2024C','Run2024D']:
                        if era_toCheck in args.data_era:
                            dRun_dataset_Ext = '0'
                        if era_toCheck in args.ref_era:
                            rRun_dataset_Ext = '0'

                    # ppRef runs Run2023F
                    for era_toCheck in ['Run2023F']:
                        # HLTPhysics
                        if era_toCheck in args.data_era:
                            dRun_dataset_Mu = 'HLTPhysics'
                            dRun_dataset_EG = 'PPRefHardProbes0'
                        if era_toCheck in args.ref_era:
                            rRun_dataset_Mu = 'HLTPhysics'
                            rRun_dataset_EG = 'PPRefHardProbes0'

                    # HI runs
                    for era_toCheck in ['HIRun2023A']:
                        # HLTPhysics
                        if era_toCheck in args.data_era:
                            dRun_dataset_Mu = 'HIHLTPhysics'
                            dRun_dataset_EG = 'HIHLTPhysics'
                            dRun_dataset_Ext = ''
                        if era_toCheck in args.ref_era:
                            rRun_dataset_Mu = 'HIHLTPhysics'
                            rRun_dataset_EG = 'HIHLTPhysics'
                            rRun_dataset_Ext = ''

                    # ppRef runs Run2023F
                    for era_toCheck in ['Run2024A']:
                        # HLTPhysics
                        if era_toCheck in args.data_era:
                            dRun_dataset_Mu = 'HLTPhysics'
                            dRun_dataset_EG = 'HLTPhysics'
                        if era_toCheck in args.ref_era:
                            rRun_dataset_Mu = 'Muon'
                            rRun_dataset_EG = 'EGamma'
                            
                    dRun_dataset_Mu = '%s%s' % (dRun_dataset_Mu, dRun_dataset_Ext)
                    rRun_dataset_Mu = '%s%s' % (rRun_dataset_Mu, rRun_dataset_Ext)
                    dRun_dataset_EG = '%s%s' % (dRun_dataset_EG, dRun_dataset_Ext)
                    rRun_dataset_EG = '%s%s' % (rRun_dataset_EG, rRun_dataset_Ext)


                    dqm_url_L1TEffi_Mu = form_offline_dqm_url(dRun, rRun, dRun_dataset=dRun_dataset_Mu, rRun_dataset=rRun_dataset_Mu, dRun_era=args.data_era, rRun_era=args.ref_era, workspace='L1T_shift/Efficiency', refNormalize=False)
                    dqm_url_L1TReso_Mu = form_offline_dqm_url(dRun, rRun, dRun_dataset=dRun_dataset_Mu, rRun_dataset=rRun_dataset_Mu, dRun_era=args.data_era, rRun_era=args.ref_era, workspace='L1T_shift/Resolution', refNormalize=True)
                    dqm_url_L1TEffi_EG = form_offline_dqm_url(dRun, rRun, dRun_dataset=dRun_dataset_EG, rRun_dataset=rRun_dataset_EG, dRun_era=args.data_era, rRun_era=args.ref_era, workspace='L1T_shift/Efficiency', refNormalize=False)
                    dqm_url_L1TReso_EG = form_offline_dqm_url(dRun, rRun, dRun_dataset=dRun_dataset_EG, rRun_dataset=rRun_dataset_EG, dRun_era=args.data_era, rRun_era=args.ref_era, workspace='L1T_shift/Resolution', refNormalize=True)


                    '''
                    dqm_url_L1TEffi_Mu = form_offline_dqm_url(dRun, rRun, dataset='Muon0', workspace='L1T_shift/Efficiency', dRun_era=args.data_era, rRun_era=args.ref_era, refNormalize=False)
                    dqm_url_L1TReso_Mu = form_offline_dqm_url(dRun, rRun, dataset='Muon0', workspace='L1T_shift/Resolution', dRun_era=args.data_era, rRun_era=args.ref_era, refNormalize=True)
                    dqm_url_L1TEffi_EG = form_offline_dqm_url(dRun, rRun, dataset='EGamma0', workspace='L1T_shift/Efficiency', dRun_era=args.data_era, rRun_era=args.ref_era, refNormalize=False)
                    dqm_url_L1TReso_EG = form_offline_dqm_url(dRun, rRun, dataset='EGamma0', workspace='L1T_shift/Resolution', dRun_era=args.data_era, rRun_era=args.ref_era, refNormalize=True)
                    '''
                    print(dqm_url_L1TEffi_Mu)
                    print(dqm_url_L1TReso_Mu)
                    print(dqm_url_L1TEffi_EG)
                    print(dqm_url_L1TReso_EG)
                    if not args.debug:
                        webbrowser.open(dqm_url_L1TEffi_Mu, new=0, autoraise=False)
                        webbrowser.open(dqm_url_L1TReso_Mu, new=0, autoraise=False)
                        webbrowser.open(dqm_url_L1TEffi_EG, new=0, autoraise=False)
                        webbrowser.open(dqm_url_L1TReso_EG, new=0, autoraise=False)
            

                    
        ## Give AutoDQM server some time to process run before moving on to next run
        if dRun != data_runs[-1] and not args.debug:
            time.sleep(args.sleep)

    ## End loop: for dRun in data_runs

    print('\n\n*** Completed running URL_AutoDQM.py ***\n\n')

## End function: if __name__ == '__main__':
