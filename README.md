# L1PFE_OMS

**You should follow the instruction twiki for your very first shift to
understand the precedure. Only use this script to speed up the process later.
The output template is need editting to the official format!**

This repository holds the script for the L1 Prompt Feedback Expert (PFE) shifter.
The PFE shifters are required to follow the [instruction](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide). The steps of certify each run involves with steps to retrieve information from run register, WBM, DQM etc. The scripts are designed to help shifter obtain those information easily. The judgement will come from the shifter. If you have problem with these scripts, good luck!


## Pre-requirement

* CERN account to enable you login to lxplus via ssh
* A web browser on your laptop
* git on your laptop to check out code
* ROOT on your laptop
  * You can download the binary version of ROOT from [here](https://root.cern.ch/downloading-root).
* Python on your laptop
  * The scripts only uses Python Standard Library, which should comes with Python. If you have package missing, you can install it with pip.

You can check out the code to your laptop via
`git clone https://github.com/cms-l1-dpg/L1PFE_OMS.git`

## Start of shift
<span style="color:red">You should always follow the instruction twiki.</span>

Follow the twiki to setup your role. Each date, follow [Choosing the runs to certify](https://twiki.cern.ch/twiki/bin/viewauth/CMS/OfflineTriggerShifterGuide#Choosing_the_runs_to_certify) to find out the list of run to certify. This step is intentionally left for shifter to review and decide the priority.

## Start of shift
Once you get the list of runs to certify, you should login to lxplus and follow the below steps
```shell
## Setup a CMSSW environment if you already have one
## Otherwise follow the below steps
cmsrel CMSSW_10_0_0
cd CMSSW_10_0_0/src
cmsenv
## Checkout the code
git clone https://github.com/cms-l1-dpg/L1PFE_OMS.git
cd L1PFE_OMS
```
Run the run register script
`python PFE_RR.py 306091 XXXXXX XXXXXX`

Then you should have a file "PFE.json" produced in the directory.

> We are currently working with OMS development team on the Run Register
> API. Once that is ready, this step can be moved to your laptop and you won't
> need to login to lxplus. Before that happened, you will need to login to
> lxplus for the Run Register API.


## Verify each run
Go to your laptop and make sure you have your grid certificate stored in
~/.globus. If not, please follow the [instruction](https://ca.cern.ch/ca/help/?kbid=024010).
Create a working directory for you and follow the below commends
```shell
git clone https://github.com/cms-l1-dpg/L1PFE_OMS.git
cd L1PFE_OMS
source setup.(c)sh #Depending on your shell
scp lxplus.cern.ch:$PATH_TO_JSON .
```
The setup script will create a key file for grabbing the DQM files. You also
will setup a proxy via lxplus.cern.ch for the OMS API.

Now, to start the certification, you run `python PFE_Shifter.py `. The code
will print out an elog file for you in format as Elog_MMDD_HHMM.log. When it is
ready, you will see the below:
```shell
Elog file Elog_0716_1633.log is ready! Open a new terminate to edit the file...
Press Enter to start the shift!
```
Open a new terminate to edit the file.

You might see something as below:
```
=====================================================================
First Collisions17 run (start time): 306091 (2017-11-02 15:59:38)
Last Collisions17 run (stop time): 306091 (2017-11-02 20:00:14)

Missing keys for Collisions17 runs:

Run    #LS Group         L1T Online L1Tmu Offline L1Tcalo Comments
---------------------------------------------------------------------
306091 585 Collisions17 GOOD GOOD GOOD
---------------------------------------------------------------------
---------------------------------------------------------------------

## Run 306091 (Collisions17, fill 6358) -- L1T GOOD

Detector components: CTPPS EXCLUDED, CASTOR EXCLUDED,
Physically meaningful LS range: 45-629
L1 key 

L1A Physics rate: kHz
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

```
As you can see, it printout a template of the run report and a summary of the
shift at the end. <++> denotes the places you need to modify in the report.
The tool also define the Physically meaningful LS for you. 

When you are ready, follow the instruction by hitting enter. The code will
guide you through the certification of each run, by opening the WBM and DQM
webpages for you. 

### Finish the rest of the shift

Once you go through all the runs, make sure you edit the elog file as the
official template. This code might not be synchronize closely with the twiki. 
Follow the instruction twiki for the rest of steps. If you encounter any
problem or issues with the code, please create an issue on the github and we
will try to follow up as soon as we can.

*That is it! Please follow the twiki for the rest steps and finish your shift for today!*
