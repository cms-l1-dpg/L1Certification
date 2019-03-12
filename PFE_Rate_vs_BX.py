#! /usr/bin/env python
import sys, imp
import os
from string import *
import math

import json
from pprint import pprint
from math import sqrt

import ROOT

from ROOT import TH1F, gDirectory
from ROOT import TCanvas, TLegend, TText
from ROOT import gStyle

#  
#  I use a wget to retrieve the HLT DQM histograms.
#  In order to avoid having to enter the PEM pass phrase each time, one needs
#  to create a key without the password, from the usual key associated with
#  the grid certificate :
#  openssl rsa -in /afs/cern.ch/user/e/eperez/.globus/userkey.pem  -out keyout.pem
#
#  You need to edit this line :
#     os.system("wget --private-key=keyout.pem  --certificate=/afs/cern.ch/user/e/eperez/.globus/usercert.pem " + base + path )
#  in GetFile( run ) and put in the paths of your key and grid certificate.
#


trigger_list = [ "SingleEG38", "HTT380er", "ETMHF120", "ETM120", "SingleIsoEG32", "SingleIsoEG32er2p1", "IsoEG32dif", "DoubleJet112er2p7", "TripleJet_98_83_71_VBF", "QuadJet60er2p7","DoubleJet30_Mass_Min400_dEta_Max1p5" ]


# --------------------------------------------------------------------------------------------------------------

def GetFile( run ) :
    base="https://cmsweb.cern.ch/dqm/online/data/browse/Original/"
    s = str( run )
    path = "000"+s[0]+s[1]+"xxxx/"
    path = path + "000"+s[0]+s[1]+s[2]+s[3]+"xx/"
    path = path + "DQM_V0001_HLTpb_R000"+ s + ".root"
    os.system("wget --private-key=keyout.pem  --certificate=/afs/cern.ch/user/e/eperez/.globus/usercert.pem " + base + path )
    fname = "DQM_V0001_HLTpb_R000"+ s + ".root"
    return fname


# --------------------------------------------------------------------------------------------------------------

def PrePostfiring_fraction( hzb, h ) :

    frac = -1
    err = -1
    post_frac = -1
    post_err = -1
    pre_resu = [ frac, err ]
    post_resu = [ post_frac, post_err ]
    resu = [ pre_resu, post_resu ]

    if hzb == 0 or h == 0 :
	print " --- missing histogram... "
	return resu

    nbins = hzb.GetNbinsX()
    nzero = 0
    nminus = 0
    post_nzero = 0
    post_nplus = 0
    for i in range(nbins) :
	j = i+1
	vzb = hzb.GetBinContent( j )
	vzb_minus = hzb.GetBinContent( j-1 )
        vzb_plus  = hzb.GetBinContent( j+1 )
	if vzb > 0 and vzb_minus == 0 :		# first BX in a train
	    nzero += h.GetBinContent( j )
	    nminus += h.GetBinContent( j-1 )
	if vzb > 0 and vzb_plus == 0 :		# last BX in a train
	    post_nzero += h.GetBinContent( j )
	    post_nplus += h.GetBinContent( j+1 )

    total = float(nminus+nzero)
    if total > 0 :
        frac = float(nminus) / total
        err = math.sqrt( frac * (1.-frac) / total )
    pre_resu = [ frac, err ]
    post_total = float(post_nplus+post_nzero)
    if post_total > 0 :
	post_frac = float(post_nplus) / post_total
	post_err = math.sqrt( post_frac * (1.-post_frac) / post_total )
    post_resu = [ post_frac, post_err ]
    resu = [ pre_resu, post_resu ]
    return resu
 

# --------------------------------------------------------------------------------------------------------------

def ProcessRun( run ) :
    fname = GetFile( run )

    res = { }
    if not os.path.isfile( fname ) :
	return res

    f =  ROOT.TFile(fname,"read")

    f.cd( "DQMData/Run "+str(run)+"/HLT/Run summary/TriggerBx/L1T" )

    hzb = 0
    htriggers = { }
    prepost = { }

    for triggername in trigger_list :
	htriggers[ triggername ] = 0 

    for k in gDirectory.GetListOfKeys() :
   	hname = k.GetName()
	if hname.count("L1_ZeroBias (") and not hname.count("ZeroBias_copy") :
	    hzb = k.ReadObj()
        for triggername in trigger_list :
	    if hname.count("L1_" + triggername + " (") :
		htemp = k.ReadObj()
		htriggers[ triggername ] = htemp

    # --- Difference between EG32 and EG32_er2p1
    ha = htriggers[ "SingleIsoEG32" ]
    hb = htriggers[ "SingleIsoEG32er2p1" ]
    htemp = ha.Clone()
    htemp.SetName("IsoEG32dif")
    htemp.Add( hb, -1. )
    htriggers["IsoEG32dif"] = htemp
    

    if hzb == 0 :
	print " .... no L1_ZeroBias histogram for run = ",run
	return

    for triggername in trigger_list :
	prepost_fraction = PrePostfiring_fraction( hzb, htriggers[ triggername] )
	prepost[ triggername] =  prepost_fraction 

    res = prepost

    os.system("rm " + fname )
    return res

# --------------------------------------------------------------------------------------------------------------

def makePlot( resname ) :
    os.system( "sort -k 1 pre_"+resname + " > sorted_pre_"+resname)
    os.system( "sort -k 1 post_"+resname + " > sorted_post_"+resname)

    pre_fres = open("sorted_pre_"+resname,"r")
    post_fres = open("sorted_post_"+resname,"r")

    ll_pre = pre_fres.readlines() 
    ll_post = post_fres.readlines()
    n = len( ll_pre )

    hres_pre = { }
    hres_post = { }

    for trigger in trigger_list :
	print " ... trigger = ",trigger
	hres_pre[ trigger ] = TH1F("hres_pre_"+trigger," ;run number; pre-firing "+trigger,n,0,n) 
	hres_post[ trigger ] = TH1F("hres_post_"+trigger," ;run number; post-firing "+trigger,n,0,n)


    i = 0
    for al in ll_pre :
	l = al.split()
	i=i+1
	run = l[0]
	for trigger in trigger_list :
	    itrig = trigger_list.index(trigger)
	    hres_pre[trigger].GetXaxis().SetBinLabel(i,"Run "+str(run) )
	    hres_pre[trigger].SetBinContent( i, float(l[ 1 + 2*itrig]) )
	    hres_pre[trigger].SetBinError( i, float(l[ 1 + 2*itrig + 1] ) )

    i = 0
    for al in ll_post :
        l = al.split()
        i=i+1
        run = l[0]
        for trigger in trigger_list :
	    itrig = trigger_list.index(trigger)
            hres_post[trigger].GetXaxis().SetBinLabel(i,"Run "+str(run) )
            hres_post[trigger].SetBinContent( i, float(l[ 1 + 2*itrig]) )
            hres_post[trigger].SetBinError( i, float(l[ 1 + 2*itrig + 1] ) )


    pre_fres.close()
    post_fres.close()
 
    # -- do the plots :
    gStyle.SetOptStat(0)
    leg = TLegend(0.6,0.75,0.95,0.92,"","brNDC")
    leg.SetBorderSize(0)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)

    tt = TText()
    tt.SetTextSize(0.06)

    for trigger in trigger_list :
        hres_pre[trigger].SetMinimum(0)
        hres_post[trigger].SetMinimum(0)
	hres_post[trigger].SetMarkerColor(2)
	hres_post[trigger].SetLineColor(2)
  	c = TCanvas("c_"+trigger,"c_"+trigger)
        hres_pre[trigger].GetYaxis().SetTitle("post/"+hres_pre[trigger].GetYaxis().GetTitle() )
	hres_pre[trigger].Draw("pe")
	hres_post[trigger].Draw("same,pe")
	if trigger_list.index(trigger) == 0 :
	    leg.AddEntry(hres_pre[trigger], "pre-firing","pe")
	    leg.AddEntry(hres_post[trigger], "post-firing","pe")
 	leg.Draw();
	tt.DrawTextNDC(0.25, 0.88, trigger)
	c.SaveAs(trigger+".gif")

    # --- store the histograms 
    hres = ROOT.TFile("all_hres.root","update")
    for trigger in  trigger_list :
	hres_pre[trigger].Write()
	hres_post[trigger].Write()
    hres.Close()

    return
    

# --------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    resname = "results.txt"

    pre_resname = "pre_"+resname
    pre_fres = open(pre_resname,"w")

    post_resname = "post_"+resname
    post_fres = open(post_resname,"w")

    with open('json.txt') as f :
	data = json.load(f)

    irun = 0

    list_of_runs = data.keys()
    for run in list_of_runs :
	irun += 1
	print " irun = ",irun
        #if irun > 2 :		# for testing
	    #break
     	res = ProcessRun( run ) 
        if len(res) == 0 :
	    continue

	sres_pre = str(run) 
        sres_post = str(run)

        for triggername in trigger_list :
	    prepost = res[triggername]
	    pre = prepost[0]
	    post = prepost[1]
	    sres_pre += '\t' + str( pre[0] ) + '\t' + str( pre[1] )
            sres_post += '\t' + str( post[0] ) + '\t' + str( post[1] )
	sres_pre += "\n"
	sres_post += "\n"

	pre_fres.write( sres_pre )
   	post_fres.write( sres_post )

    pre_fres.close()
    post_fres.close()

    makePlot( resname )


	


