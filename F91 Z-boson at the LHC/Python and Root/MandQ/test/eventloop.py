# Lines beginning with "#" are comments in python.
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
outfile = ROOT.TFile.Open("analysis_"+myfile.GetName().split('/')[-1], "RECREATE")
outfile.cd()

# Book histograms within the output file
hVertexDist        = ROOT.TH1D("hVertexDist",   "Distribution of the interaction vertex along the z-axis; z [mm]; Entries", 1000, -500, 500)

#adding the distributions for the other important parameters
hNLeptonsDist        = ROOT.TH1D("hNLeptonsDist",   "Distribution of the preselected lepton number; N_{lep}; Entries", 6, 0,  6)
hTransverseMomDist       = ROOT.TH1D("hTransverseMomDist",   "Distribution of the transverse momenta; p_{t} [GeV]; Entries", 100, 0,  200)
hPseudoRapidityDist       = ROOT.TH1D("hPseudoRapidityDist",   "Distribution of the Pseudorapidity #eta; pseudorapidity #eta; Entries", 100, -3,  3)
hInvariantMassDist   =  ROOT.TH1D("hInvariantMassDist",   "Distribution of the Invariant Masses M (from geometry); mass M [GeV]; Entries", 1000, 0.5, 150)
hTLorentzMassDist   =  ROOT.TH1D("hTLorentzMassDist",   "Distribution of the Invariant Masses M (from TLorentzVector); mass M [GeV]; Entries", 1000, 0.5, 150)

#For testing the Isolation
hEIsolationDist = ROOT.TH1D("hEIsolationDist",   "Distribution of the E Isolation in a cone of R = 0.2; z position; Isolation", 100, -1,  1)
hpIsolationDist = ROOT.TH1D("hpIsolationDist",   "Distribution of the p Isolation in a cone of R = 0.3; z position; Isolation", 100, 0,  1)


#Implementing the cut flow and filters
hCutFlow = ROOT.TH1D("hCutFlow",   "Cut Flow diagram; ; Events", 13, 0, 13)

#Preparing the diagram
hCutFlow.GetXaxis().FindBin("All")
hCutFlow.GetXaxis().FindBin("Weights")
hCutFlow.GetXaxis().FindBin("Trigger")
hCutFlow.GetXaxis().FindBin("GRL")
hCutFlow.GetXaxis().FindBin("Vertex")
hCutFlow.GetXaxis().FindBin("2 Leptons")
hCutFlow.GetXaxis().FindBin("PDGID")
hCutFlow.GetXaxis().FindBin("Charge")
hCutFlow.GetXaxis().FindBin("p_{t} Cut")
hCutFlow.GetXaxis().FindBin("E_{t} Isolation")
hCutFlow.GetXaxis().FindBin("p_{t} Isolation")
hCutFlow.GetXaxis().FindBin("Tight ID")
hCutFlow.GetXaxis().FindBin("Z Mass")

# To look at each entry in the tree, loop over it.
# Either loop over a fixed amount of events, or over all entries (nEntries)
if numEvents<0:
    nEntries = myChain.GetEntriesFast()
else:
    nEntries = numEvents 
    
for jentry in range(0, nEntries):

    
    nb = myChain.GetEntry(jentry)
    if nb <= 0: continue

    #Separating between real data and MC
    if 'Data' in myfile.GetName().split('/')[-1]:
        weight = 1
    else:
        weight =  myChain.mcWeight
    
    #Appending all entries to the Cut Flow diagram
    hCutFlow.Fill("All", weight)
    hCutFlow.Fill("Weights", weight)
    
    if (myChain.trigE or myChain.trigM):
        hCutFlow.Fill("Trigger", weight)
    else:
        continue
  
  
    if myChain.passGRL:
        hCutFlow.Fill("GRL", weight)
    else:
        continue
    
    if myChain.hasGoodVertex:
        hCutFlow.Fill("Vertex", weight)
    else:
        continue
    
    #We are looking for dilepton final states
    if myChain.lep_n == 2:
        hCutFlow.Fill("2 Leptons", weight)
    else:
        continue
        
    if myChain.lep_type[0] in [11, 13, 15] and myChain.lep_type[0] == myChain.lep_type[1]:    # Electron, Muon, Tauon in this order
        hCutFlow.Fill("PDGID", weight)
    else:
        continue

    if (myChain.lep_charge[0] + myChain.lep_charge[1]) == 0:
        hCutFlow.Fill("Charge", weight)
    else:
        continue

    if (myChain.lep_pt[0] > 25000 and myChain.lep_pt[1] > 25000):
        hCutFlow.Fill("p_{t} Cut", weight)
    else:
        continue
    
    if (myChain.lep_etcone20[0] / myChain.lep_pt[0] < 0.1) and (myChain.lep_etcone20[1] / myChain.lep_pt[1] < 0.1):
        hCutFlow.Fill("E_{t} Isolation", weight)
    else:
        continue
    
    if (myChain.lep_ptcone30[0] / myChain.lep_pt[0] < 0.1) and (myChain.lep_ptcone30[1] / myChain.lep_pt[1] < 0.1):
        hCutFlow.Fill("p_{t} Isolation", weight)
    else:
        continue
    
    num1 = str(bin(myChain.lep_flag[0]))
    num2 = str(bin(myChain.lep_flag[1]))
    
    if (num1[-9] == "1" and num2[-9] == "1"):
        hCutFlow.Fill("Tight ID", weight)
    else:
        continue
    
   #Extracting important parameters from input
    vertexZ = myChain.vxp_z
    hVertexDist.Fill(vertexZ, weight)
    
    NLep = myChain.lep_n
    hNLeptonsDist.Fill(NLep, weight)
    
    TransverseMom = myChain.lep_pt
    AzimutalComp = myChain.lep_phi
    PseudoRapidity = myChain.lep_eta
    Energy = myChain.lep_E

    
    
    # Some entries are stored in vectors, meaning they have several entries themselves
    # another loop is needed for these objects
    
    #improved output using a loop to evaluate all entries and fill single elements
    print"---------- EVENT {}".format(jentry +1 ),  "----------"
    print "Leptons found:",   NLep
    print 

    ZMass = 0
    #empty list to store the results from both leptons 
    storeRes = []
    for i in range(NLep):
        if NLep < 2: #only relevant for the first part of the lab course, later the filter mechanisms only accept dilepton events
            print "Could not compute the invariant mass, at least 2 leptons required!"
            print 
        else:
            print "Important parameters for Lepton {}".format(i+1)
            
            pfrac = myChain.lep_ptcone30[i] / myChain.lep_pt[i]
            hpIsolationDist.Fill(pfrac, weight)
            Efrac = myChain.lep_etcone20[i] / myChain.lep_pt[i]
            hEIsolationDist.Fill(Efrac, weight)
        
            #Calculating the momentum components
            pt = TransverseMom[i] / 1000 #converting result into GeV
            print "p_t{} = ".format(i + 1), pt  , " GeV" 
        
            phi = AzimutalComp[i]
            eta = PseudoRapidity[i]
        
            E = Energy[i] / 1000
            print "E{} = ".format(i + 1), E  , " GeV" 
        
            #absolute momentum from collider geometry
            px = pt * cos(phi)
            py = pt * sin(phi)
            pz = pt * sinh(eta)
            
            pvec = [px, py, pz]
        
            p_abs = pt * cosh(eta)
            print "p_abs{} = ".format(i+1), p_abs , " GeV" 
            print 
            
            #using ROOTs TLorentzVector to compare the result
            Lvec = TLorentzVector()
            Lvec.SetPtEtaPhiE(pt,eta,phi,E)
            
            #Storing the result to analyze the distributions
            hTransverseMomDist.Fill(TransverseMom[i] / 1000, weight) #Can only fill a single element not a vector ..
            hPseudoRapidityDist.Fill(PseudoRapidity[i], weight)
            
            #Storing the parameters for both leptons
            storeRes.append([pvec, E, Lvec])
            
        
    #calculating the invariant mass 
    if len(storeRes) > 0:
        ptot = []
        for i in range(len(storeRes[0][0])):
            ptot.append(storeRes[0][0][i] + storeRes[1][0][i])
        Etot = storeRes[0][1] + storeRes[1][1]
        
        #using ROOTs TLorentzVector to compare the result
        Lvec_tot = storeRes[0][2] + storeRes[1][2]
        MLorentz = Lvec_tot.M()
        if abs(MLorentz - 91) < 20:
            hCutFlow.Fill("Z Mass", weight)
        else:
            continue
        hTLorentzMassDist.Fill(MLorentz, weight)
        
        print "Invariant mass M:", MLorentz , " GeV (calculated using TLorentzVector)"
        print
    
        #discarding unphysical data
        if SquaredList(ptot) < Etot**2:
            M = sqrt(Etot**2 - SquaredList(ptot))
            hInvariantMassDist.Fill(M, weight)
            
            print "Invariant mass M:", M , " GeV (calculated using geometry)"
            print
        else:
            print "Unphysical sign of the invariant mass"
            print 
        


    # might be helpful, to access all 32 bits of a 32 bit integer flag individually:

    # for bit in range ( 32 ):
    #     flagBit = lep_flag & (1 << bit)
    #     print flagBit


##########################################################################
#end of the event loop
##########################################################################


### The Wrap-up code (writing the files, etc) goes here
# Let's look at the histogram; create a canvas to draw it on
canvas = ROOT.TCanvas("myCanvas", 'Analysis Plots', 200, 10, 700, 500 )
canvas.cd()
hInvariantMassDist.SetMarkerStyle(3)
hInvariantMassDist.SetMarkerColor(ROOT.kRed)

#log axes
canvas.SetLogx()
canvas.SetLogy()

#hVertexDist.Draw()
#hNLeptonsDist.Draw()
#hTransverseMomDist.Draw()
#hPseudoRapidityDist.Draw()
hInvariantMassDist.Draw("p hist")#hTLorentzMassDist.Draw("same")
#hpIsolationDist.Draw()
#hEIsolationDist.Draw()
#hCutFlow.Draw()


#########################################################################

outfile.cd()
print "Writing output to %s"%outfile.GetName()

#Writing all created files
hVertexDist.Write()
hNLeptonsDist.Write()
hTransverseMomDist.Write()
hPseudoRapidityDist.Write()
hInvariantMassDist.Write()
hTLorentzMassDist.Write()
hpIsolationDist.Write()
hEIsolationDist.Write()
hCutFlow.Write()



canvas.Write()
#outfile.Write()

#useful command to pause the execution of the code. Allows to see the plot before python finishes
ROOT.TPython.Prompt()
