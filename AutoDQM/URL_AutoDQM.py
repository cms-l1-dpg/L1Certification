## Script to open AutoDQM pages for multiple runs
## python3 URL_AutoDQM.py

import sys
import argparse
import re
import webbrowser
import time


##############################################################
###  Default options, can be modified at the command line  ###
##############################################################

URL_BASE = 'https://cmsweb-testbed.cern.ch/dqm/autodqm/plots'
# URL_BASE = 'http://abrinke1autodqm.cern.ch:8083/dqm/autodqm/plots'
SOURCE    = 'Offline'
SUBSYSTEM = 'L1T_shift'
DATA_ERA = 'Run2022'    if SOURCE == 'Offline' else None
REF_ERA  = 'Run2018'    if SOURCE == 'Offline' else None
DATASET  = 'SingleMuon' if SOURCE == 'Offline' else None
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
DQM_MAP = {'L1T_shift': 'L1T;root=Quick%20collection',
           'EMTF': 'Everything;root=L1T/L1TStage2EMTF'}


## *** Supporting functions for constructing Online and Offline DQM URLs ***

def form_online_dqm_url(dRun, rRun, subsystem):
    dqm_url = 'https://cmsweb.cern.ch/dqm/online/start?runnr=%s;' % dRun
    dqm_url += 'dataset=/Global/Online/ALL;sampletype=online_data;filter=all;'
    dqm_url += 'referencepos=overlay;referenceshow=all;referencenorm=True;'
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
    parser.add_argument('-slp',  '--sleep',     type=int, default=15,        help='Wait time between opening new tabs')
    
    parser.add_argument('-mult', '--multiref',  action='store_true', help='Compare each data run to all references simultaneously')
    parser.add_argument('-rec',  '--recursive', action='store_true', help='Use other data runs as reference runs')
    parser.add_argument('-dqm',  '--open_dqm',  action='store_true', help='Open Online or Offline DQM pages for each data run')
    parser.add_argument('-deb',  '--debug',     action='store_true', help='Only print URLs and do not open them')
    parser.add_argument('-vrb',  '--verbose',   action='store_true', help='Include verbose printouts')

    args = parser.parse_args()

    ## Extract data and reference run lists
    data_run_str = args.data_runs
    ref_run_str  = args.ref_runs if not args.recursive else args.data_runs
    try:
        data_runs = [r for r in re.split('\W+|_', data_run_str) if len(r) == 6 and int(r) > 100000]
        ref_runs  = [r for r in re.split('\W+|_', ref_run_str)  if len(r) == 6 and int(r) > 100000]
        if args.multiref and len(ref_runs) < 2:
            ref_runs = [r for r in re.split('\W+|_', REF_RUNS)  if len(r) == 6 and int(r) > 100000]
    except:
        print('Cannot parse data_runs (%s) or ref_runs (%s or %s)' % (data_run_str, ref_run_str, REF_RUNS))
        print(re.split('\W+|_', data_run_str))
        print(re.split('\W+|_', ref_run_str))
        print(re.split('\W+|_', REF_RUNS))
        sys.exit()

    print('\nFull list of data runs is:')
    print(data_runs)
    print('\nFull list of reference runs is:')
    print(ref_runs)

    ## Warnings about opening central DQM pages (AWB 2022.07.29)
    if args.open_dqm:
        if not args.subsystem in DQM_MAP.keys():
            print('\nWARNING: open_dqm option does not work for %s subsystem! Will skip.' % args.subsystem)
        if args.source != 'Online':
            print('\nWARNING: open_dqm only works for Online DQM. Will open Online DQM page.')


    ## *** Loop over data runs and open web pages ***
    for dRun in data_runs:

        ## Pick one or more reference runs
        if args.multiref:
            rRun = '_'.join([r for r in ref_runs if r != dRun])
        elif args.recursive:
            rRun = ref_runs[ref_runs.index(dRun) - 1]
        else:
            rRun = ref_runs[data_runs.index(dRun) % len(ref_runs)]

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
            rSer  = args.ref_era
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

        print('\n\n*** Opening AutoDQM for data run %s, reference run(s) %s ***' % (dRun, rRun.replace('_', ', ')))
        print(auto_url)
        firstRun = (1 if dRun == data_runs[0] else 0)
        if not args.debug:
            webbrowser.open(auto_url, new=firstRun, autoraise=firstRun)

        ## Construct the central DQM URL and open the web browser
        if args.open_dqm:
            if args.subsystem in DQM_MAP.keys():
                ## For now, only open Online DQM even if AutoDQM is running on Offline DQM (AWB 2022.07.29)
                dqm_url = form_online_dqm_url(dRun, rRun, args.subsystem)
                print('\n*** Opening Online DQM for data run %s, reference run(s) %s ***' % (dRun, ', '.join(rRun.split('_')[:4])))
                print(dqm_url)
                if not args.debug:
                    webbrowser.open(dqm_url, new=0, autoraise=False)

        ## Give AutoDQM server some time to process run before moving on to next run
        if dRun != data_runs[-1] and not args.debug:
            time.sleep(args.sleep)

    ## End loop: for dRun in data_runs

    print('\n\n*** Completed running URL_AutoDQM.py ***\n\n')

## End function: if __name__ == '__main__':
