#!/usr/bin/env python
# encoding: utf-8

# File        : Config.py
# Author      : Zhenbin Wu
# Contact     : zhenbin.wu@gmail.com
# Date        : 2018 Jul 05
#
# Description : 


from collections import OrderedDict

PUPlots = [
    'L1_SingleMu22',
    'L1_SingleJet180',
    'L1_ETMHF120',
    'L1_HTT360er',
    # 'L1_SingleEG40',
    'L1_SingleEG40er2p5',
    # 'L1_SingleIsoEG34',
    'L1_SingleIsoEG32er2p5',
    'L1_DoubleIsoTau32er2p1'
]

CosmicPlots = OrderedDict([
    ('L1_SingleMuCosmics'           , [0  , "<+110-130Hz+>"]),
    ('L1_SingleMu7'                 , [12 , "<+20-25Hz+>"])  ,
    ('L1_SingleEG8er2p5'            , [56 , "<+10-270Hz+>"]) ,
    ('L1_SingleJet35'               , [120, "<+0-100Hz+>"])  ,
    ('L1_SingleJet20er2p5_NotBptxOR', [230, "<+Active+>"])   ,
    ('L1_SingleMuOpen_NotBptxOR'    , [222, "<+Active+>"])
])

PrefiringSeeds = [
    "L1_SingleMu22_BMTF",
    "L1_SingleMu22_OMTF",
    "L1_SingleMu22_EMTF",
    "L1_SingleIsoEG32er2p5",
    "L1_SingleEG40er2p5",
    "L1_SingleTau120er2p1",
    "L1_SingleJet180"
]

OMSObjectName = {
    "run" : "runs/{}",
    "l1configurationKeys" : "runs/{}/l1configurationKeys",
    "l1algorithmtriggers" : "runs/{}/l1algorithmtriggers",
    "l1algoRateLS" : "l1algorithmtriggers/{}_{}/relationships/l1AlgorithmTriggersPerLumisection"
}
## Valid L1T from https://twiki.cern.ch/twiki/bin/viewauth/CMS/OnlineWBL1TriggerKeys2018
## Current version r168, 2018-07-04
ValidL1Keys = set([
    # uGT
    "ugt_pp2018_v1_0_0/v2",
    "ugt_pp2018_v0_0_1/v1",
    "ugt_rs_collisions2018/v44",
    "ugt_rs_circulating2018/v11",
    "ugt_rs_cosmics2018/v17",
    # uGMT
    "ugmt_base/v45",
    "ugmt_bottomonly/v45",
    "ugmt_basenozs/v12",
    "ugmt_bottomonlynozs/v13",
    "ugmt_rs_base/v12 ugmt_rs_bottomOnly/v5 ugmt_rs_noratemoni/v4",
    # CALOL2
    "calol2_collisions2018/v21",
    "calol2_rs_tmtMode-MP9-out/v2",
    # CALOL1
    "calol1_base/v20",
    "calol1_base/v21",
    "calol1_rs_base/v17",
    "calol1_rs_BeamSplash/v1",
    # BMTF
    "bmtf_collisions_zs_2018/v6",
    "bmtf_cosmics_2018/v2",
    "bmtf_cosmics_zs_2018/v10",
    # OMTF
    "omtf_base/v27",
    "omtf_rs_daq_enabled/v18",
    # EMTF
    "emtf_base/v83",
    "emtf_single_hits/v88",
    "emtf_local_runs/v54",
    "emtf_rs_base/v10",
    # TWINMUX
    "twinmux_2018_rpconly/v4",
    "twinmux_rs_nodtmasked/v1",
    # CPPF
    "cppf_base/v25",
    "cppf_rs_base/v7",
    "cppf_rs_base/v6",
    # DT
    "Collisions18_1",
    # RPC
    "LHC10",
    "LHC10_BOTTOM",
    # ECAL
    "BEAMV6_TRANS_SPIKEKILL",
    "BEAM_HI_noFG_2017",
    "ET_Hardcoded",
    # HCAL
    "Physics2018v5",
])
