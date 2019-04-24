# script to plot the histograms from different input files in one single plot
import ROOT
import math
import os, sys

import argparse



def styleHisto(histo, color, xtit, ytit, filled=True):
    histo.SetMarkerStyle(20)
    histo.SetMarkerSize(0.7)
    histo.SetMarkerColor(color)
    histo.SetLineColor(color)
    histo.SetLineWidth(2)
    histo.GetXaxis().SetTitle(xtit);
    histo.GetYaxis().SetTitle(ytit);
    histo.GetXaxis().SetTitleSize(0.048)
    histo.GetYaxis().SetTitleSize(0.048)
    histo.GetXaxis().SetTitleOffset(1.2);
    histo.GetYaxis().SetTitleOffset(1.2);
    histo.GetXaxis().SetLabelSize(0.03);
    histo.GetYaxis().SetLabelSize(0.03);
    histo.GetXaxis().SetLabelOffset(0.015);
    histo.GetYaxis().SetLabelOffset(0.015);

    if (filled):
      histo.SetFillColor(color)
      histo.SetLineColor(ROOT.kBlack)
      histo.SetLineWidth(1)
      histo.SetFillStyle(3002)

####################################################################################################    

# Style root
# https://root.cern.ch/doc/master/classTStyle.html
#ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetFrameFillColor(10)
ROOT.gStyle.SetTitleFillColor(0)
ROOT.gStyle.SetTitleBorderSize(1)
ROOT.gStyle.SetPadTopMargin(0.10)
ROOT.gStyle.SetPadBottomMargin(0.12)
ROOT.gStyle.SetPadRightMargin(0.05)
ROOT.gStyle.SetPadLeftMargin(0.15)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetPaperSize(ROOT.TStyle.kA4)
ROOT.gStyle.SetHatchesSpacing(4.0)
#ROOT.gStyle.SetHatchesLineWidth()



parser = argparse.ArgumentParser(description='Plotting of Z events.')
parser.add_argument('-d', metavar='path_data', type=str, nargs=1, help='Input Data file', required=True)
parser.add_argument('-e', metavar='path_ee', type=str, nargs=1, help='Input MC Zee file', required=False)
parser.add_argument('-m', metavar='path_mm', type=str, nargs=1, help='Input MC Zmumu file', required=False)
parser.add_argument('-t', metavar='path_tt', type=str, nargs=1, help='Input MC Ztautau file', required=False)

args = parser.parse_args()

path_d = args.d[0]
if args.e != None:
  path_e = args.e[0]
else:
  path_e = None
if args.m != None:
  path_m = args.m[0]
else:
  path_m = None
if args.t != None:
  path_t = args.t[0]
else:
  path_t = None



#Scaling is done by calculating the luminosity scale factor of the sample via xsec/sumw and multiplying the target luminosity
#target luminosity = 1000 pb^-1 for all samples
#The sumw variable assumes you have processed all events in the sample.

xsec_e = 8175.7172
sumw_e = 203795455568148
xsec_m = 9953.0232
sumw_m = 225316022111048
xsec_t = 1346.6041
sumw_t = 31508540303680.9
lumi   = 1000

#open the input files
print path_d
print path_e
print path_m
print path_t


if os.path.isfile(path_d) and os.access(path_d, os.R_OK):
    file_d = ROOT.TFile(path_d, "READ")
else:
    sys.exit("Error: File " + path_d + " does not exist or is not readable")

if path_e:
    if os.path.isfile(path_e) and os.access(path_e, os.R_OK):
        file_e = ROOT.TFile(path_e, "READ")
    else:
        sys.exit("Error: File " + path_e + " does not exist or is not readable")

if path_m:
    if os.path.isfile(path_m) and os.access(path_m, os.R_OK):
        file_m = ROOT.TFile(path_m, "READ")
    else:
        sys.exit("Error: File " + path_m + " does not exist or is not readable")

if path_t:
    if os.path.isfile(path_t) and os.access(path_t, os.R_OK):
        file_t = ROOT.TFile(path_t, "READ")
    else:
        sys.exit("Error: File " + path_t + " does not exist or is not readable")


# Create a legend to label the different components of the plot
# canvas.BuildLegend() would do the same, but is not as customizable
# https://root.cern.ch/doc/master/classTLegend.html
legend = ROOT.TLegend(0.70, 0.60, 0.85, 0.85);
legend.SetFillColor(0)
legend.SetLineColor(0)


# Read the histogram we want to draw
# First read the data 
histname = "hInvariantMassDist"
h_d = file_d.Get(histname) 
styleHisto(h_d, ROOT.kBlack, "M_{ll} [GeV]", "Entries")
legend.AddEntry(h_d, "Data", "lep")

#MC ee
h_e = file_e.Get(histname) 
h_e.Scale(lumi*xsec_e/sumw_e)
styleHisto(h_e, ROOT.kBlue, "M_{ll} [GeV]", "Entries")
legend.AddEntry(h_e, "MC Z #rightarrow ee", "f")

#MC mumu
h_m = file_m.Get(histname) 
h_m.Scale(lumi*xsec_m/sumw_m)
styleHisto(h_m, ROOT.kRed, "M_{ll} [GeV]", "Entries")
legend.AddEntry(h_m, "MC Z #rightarrow #mu#mu", "f")

#MC tautau
h_t = file_t.Get(histname) 
h_t.Scale(lumi*xsec_t/sumw_t)
styleHisto(h_t, ROOT.kGray, "M_{ll} [GeV]", "Entries")
legend.AddEntry(h_t, "MC Z #rightarrow #tau#tau", "f")

# Open the MC files analogously if the corresponding flag is set.
# They need to be scaled by a scalefactor=lumi*xsec/sumw
# This is done by h_xyz.Scale(scalefactor)
# To plot them added on top of each other, you can use a THStack
# https://root.cern.ch/doc/master/classTHStack.html
stack = ROOT.THStack("stackname", "stacktitle")

#adding the histograms to the stack
stack.Add(h_e)
stack.Add(h_m)
stack.Add(h_t)


# Create a canvas to draw on later
canvas = ROOT.TCanvas("myCanvas", 'Analysis Plots', 200, 10, 700, 500 )
canvas.cd()




if stack.GetNhists()>0:
  #unlike TH1, a THStack needs to be drawn first, then styled and then redrawn
  stack.Draw("hist")
  stack.GetXaxis().SetRangeUser(70,115)
  stack.GetXaxis().SetTitleSize(0.048)
  stack.GetXaxis().SetTitle("M_{ll} [GeV]")
  stack.GetYaxis().SetTitleSize(0.048)
  stack.GetYaxis().SetTitle("Entries")
  stack.GetXaxis().SetTitleOffset(1.2);
  stack.GetYaxis().SetTitleOffset(1.5);
  stack.GetXaxis().SetLabelSize(0.04);
  stack.GetYaxis().SetLabelSize(0.04);
  stack.GetXaxis().SetLabelOffset(0.015);
  stack.GetYaxis().SetLabelOffset(0.01);
  stack.Draw("hist")

h_d.Draw("same")
h_d.GetXaxis().SetRangeUser(70,115)

# Draw the legend
legend.Draw()



ROOT.TPython.Prompt()  

file_d.Close()

if path_e:
  file_e.Close()

if path_m:
  file_m.Close()

if path_t:
  file_t.Close()
