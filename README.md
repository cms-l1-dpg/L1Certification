# L1PFE_OMS

**You should follow the instruction twiki for your very first shift to
understand the precedure. Only use this script to speed up the process later.
The output template is need editting to the official format!**

This repository holds the script for the L1 Prompt Feedback Expert (PFE) shifter.
The PFE shifters are required to follow the [instruction](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide). The steps of certify each run involves with steps to retrieve information from run register, WBM, DQM etc. The scripts are designed to help shifter obtain those information easily. The judgement will come from the shifter. If you have problem with these scripts, good luck!


## Prerequiremnt

* CERN account to enable you login to lxplus via ssh
* A web browser on your laptop
* git on your laptop to check out code
* Python on your laptop
  * The scripts only uses Python Standard Library, which should comes with Python. If you have package missing, you can install it with pip.

You can check out the code to your laptop via
`git clone https://github.com/cms-l1-dpg/L1PFE_OMS.git`

## Start of shift
<span style="color:red">You should always follow the instruction twiki.</span>

Follow the twiki to setup your role. Each date, follow [Choosing the runs to certify](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#Choosing_the_runs_to_certify) to find out the list of run to certify. This step is intentionally left for shifter to review and decide the priority.

### [The physically meaningful LS range](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#Active_subsystems_and_the_physic)
One you get the list of runs to certify, you should login to lxplus and follow the below steps
```shell
## Setup a CMSSW environment if you already have one
## Otherwise follow the below steps
cmsrel CMSSW_10_0_0
cd CMSSW_10_0_0
cmsenv
## Checkout the code
git clone https://github.com/cms-l1-dpg/L1PFE_OMS.git
```
Run the run register script
`python PFE_RR.py 306091 XXXXXX XXXXXX`

Then you should have a print out of a template for your shifter report
```
---------------------------------------------------------------------

## Run 306091 (Collisions17, fill 6358) -- L1T GOOD

Detector components: CTPPS EXCLUDED, CASTOR EXCLUDED,
Physically meaningful LS range: 45-629
L1 key <++>

L1A Physics rate: <++>kHz
Average PU: <++>

Fill 6358 has no isolated bunch for pre/post firing study.

Rates as a function of pileup:
- L1_SingleMu22: <++>
- L1_SingleJet180: <++>
- L1_ETM100: <++>
- L1_HTT300er: <++>
- L1_SingleEG40: <++>
- L1_SingleIsoEG34: <++>
- L1_DoubleIsoTau32er2p1: <++>


L1T DQM: <++>
L1TEMU DQM: <++>

=====================================================================
First Collisions17 run (start time): 306091 (2017-11-02 15:59:38)
Last Collisions17 run (stop time): 306091 (2017-11-02 20:00:14)

Missing keys for Collisions17 runs:

Run    #LS Group         L1T Online L1Tmu Offline L1Tcalo Comments
---------------------------------------------------------------------
306091 585 Collisions17 GOOD GOOD GOOD
---------------------------------------------------------------------
```

As you can see, it printout a template of the run report and a summary of the shift at the end. <++> denotes the places you need to modify in the report. The tool also define the Physically meaningful LS for you. Copy the printout into a text file in your laptop, as you will be editing the file while you going through the steps.

It also produce a PFE.json file in the same directory, which store all the information of the runs.

### [Trigger Keys](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#Trigger_keys)
Once you get the report template and the json file, you can proceed to the next steps on your laptop.

```shell
git clone https://github.com/cms-l1-dpg/L1PFE_OMS.git
cd L1PFE_OMS
scp lxplus.cern.ch:~/PFE.json . ##Correct path to json
## step the OMS proxy for OMS API
source setupProxy.csh
python PFE_OMS.py
```

The PFE_OMS.py will print out the uniq trigger keys for cosmic runs and collision runs separately. You can then proceed to compare them with the official trigger keys twiki and report the missing keys.

> Note: It is tricky to get the twiki page via SSL. So yeah, you still have to compare by eyes for each trigger Keys

### Trigger Rate

The next steps include [L1A Physics rate](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#L1A_Physics_rate), [Individual trigger rates (only for cosmics)](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#Individual_trigger_rates_only_fo), [Rate vs. PU plots (only for collisions)](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#Rate_vs_PU_plots_only_for_collis). These steps require you to open WBM pages for each run and report. The script will open these WBM pages for you, with each page a new tab. Please make sure your browser is clean and your laptop have sufficient memory for them.

Simply run the below script. Once webpages are open, you can go through the steps for validating the rate and closing the tabs.
`python PFE_WBM.py`

> Note: the code won't check the [Pre/post-firing fractions for L1 seeds (only for collisions)](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#Pre_post_firing_fractions_for_L1). You still need to work on this by hand.

### [L1T and L1TEMU Online DQM plots](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#L1T_and_L1TEMU_Online_DQM_plots)

`python PFE_DQM.py` will open the tabs of three DQM webpage per run: Summary, Shift/L1T, Shift/L1TEMU. You will need to accept the certification to enable DQM webpage to load at first. As the DQM server is slow, the code will sleep for 10 section before opening the next DQM page. Probabily this is a good time for your break of the shift.

### Finish the rest of the shift

*That is it! Please follow the twiki for the rest steps and finish your shift for today!*
