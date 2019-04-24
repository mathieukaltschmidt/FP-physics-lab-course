 #Lines beginning with "#" are comments in python.
# Start your program by importing Root and some other handy modules
import ROOT 
from ROOT import TLorentzVector

import math
from math import sin, cos, sinh, cosh, sqrt

import sys
import os
import os.path

# The argparse module makes it easy to write user-friendly command-line interfaces. 
import argparse

#Taking the absolute value of a vector formatted as list
def SquaredList(list):
    abs_list = 0
    for i in range(len(list)):
        abs_list += list[i]**2
    return abs_list
    

# we add the flags -f and -n to the scripts, so we can pass arguments in the command line:
# e.g.   python eventloop.py -f someFile.root -n 10
parser = argparse.ArgumentParser(description='Analysis of Z events.')
parser.add_argument('-f', metavar='inputFile', type=str, nargs=1, help='Input ROOT file', required=True)
parser.add_argument('-n', metavar='numEvents', type=int, nargs=1, help='Number of events to process (default all)')

args = parser.parse_args()
fileName = str(args.f[0])
numEvents = -1
if args.n != None :
    numEvents = int(args.n[0])

# from now on, fileName contains the string with the path to our input file and 
# numEvents the integer of events we want to process



# Some ROOT global settings and styling
ROOT.TH1.SetDefaultSumw2()

# The execution starts here
print "Starting the analysis"

# Open the input file. The name can be hardcoded, or given from commandline as argument
myfile = None
if os.path.isfile(fileName) and os.access(fileName, os.R_OK):
    myfile = ROOT.TFile(fileName)
else:
    sys.exit("Error: Input file does not exist or is not readable")

print "Openend file %s"%myfile.GetName()

# Now you have access to everything you can also see by using the TBrowser
# Load the tree containing all the variables
myChain = ROOT.gDirectory.Get( 'mini' )

# Open an output file to save your histograms in (we build the filename such that it contains the name of the input file)
# RECREATE means, that an already existing file with this name would be overwritten
outfile = ROOT.TFile.Open("efficiency_"+myfile.GetName().split('/')[-1], "RECREATE")
outfile.cd()

# Book histograms within the output file
hAllProbes       = ROOT.TH1D("hAllProbes",   "Tag-electrons found; p_{t} [GeV]; Entries", 100, 0, 200)
hPassProbe        = ROOT.TH1D("hPassProbe",   "Passed probes; p_{t} [GeV]; Entries", 100, 0,200)
hEfficiency  = ROOT.TH1D("hEfficiency",   "Efficiency of the e^{-} detection; p_{t} [GeV]; Entries", 100, 0, 200)

def tagElectron(lepton, i):
    if not lepton.lep_type[i] == 11:
        return False
    if not (lepton.lep_pt[i] > 25000):
        return False
    if not (myChain.lep_etcone20[i] / myChain.lep_pt[i] < 0.1):
        return False
    if not (myChain.lep_ptcone30[i] / myChain.lep_pt[i] < 0.1):
        return False
    return True

def inv2(lepton):
    pt = lepton.lep_pt
    eta = lepton.lep_eta
    phi = lepton.lep_phi
    E = lepton.lep_E
    Lvec1 = TLorentzVector()
    Lvec1.SetPtEtaPhiE(pt[0], eta[0], phi[0], E[0])
    Lvec2 = TLorentzVector()
    Lvec2.SetPtEtaPhiE(pt[1], eta[1], phi[1], E[1])
    Lvec = Lvec1 + Lvec2
    return Lvec.M()/1000
    
    

# To look at each entry in the tree, loop over it.
# Either loop over a fixed amount of events, or over all entries (nEntries)
if numEvents<0:
    nEntries = myChain.GetEntriesFast()
else:
    nEntries = numEvents 
    
for jentry in range(0, nEntries):
    
    nb = myChain.GetEntry(jentry)
    if nb <= 0: continue
    
    if 'Data' in myfile.GetName().split('/')[-1]:
        weight = 1
    else:
        weight =  myChain.mcWeight
        
    #We are looking for dilepton final states
    if not myChain.lep_n == 2:
        continue
    
    if not (myChain.trigE):
        continue
    
    if not myChain.passGRL:
        continue
    
    if not myChain.hasGoodVertex:
        continue
    
    if not ((myChain.lep_charge[0] + myChain.lep_charge[1]) == 0):
        continue
    
    if not (abs(inv2(myChain) - 91) < 20):
        continue
    
    print "Preselection successfull"
    
    tag = 0
    
    if tagElectron(myChain, 0):
        tag = 1
    else:
        if tagElectron(myChain, 1):
            tag = 2
        
    if not tag:
        print "No Tag found"
        continue
    
    probe = (tag) % 2
    
    probe_pt = myChain.lep_pt[probe]/1000
    
    hAllProbes.Fill(probe_pt, weight)
    
    num = str(bin(myChain.lep_flag[probe]))
    if not num[-10] == "1":
        continue
    hPassProbe.Fill(probe_pt, weight)
    print "Probe"


##########################################################################
#end of the event loop
##########################################################################

hEfficiency.Divide(hPassProbe, hAllProbes, 1, 1, "b")

### The Wrap-up code (writing the files, etc) goes here
# Let's look at the histogram; create a canvas to draw it on
canvas = ROOT.TCanvas("myCanvas", 'Analysis Plots', 200, 10, 700, 500 )
canvas.cd()

hAllProbes.Draw()
hPassProbe.Draw()
hEfficiency.Draw()


#########################################################################

outfile.cd()
print "Writing output to %s"%outfile.GetName()

#Writing all created files
hEfficiency.Write()




canvas.Write()
#outfile.Write()

#useful command to pause the execution of the code. Allows to see the plot before python finishes
ROOT.TPython.Prompt()
