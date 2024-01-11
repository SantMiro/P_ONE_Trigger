#!/bin/sh 

from os.path import expandvars
import os, sys, random
from DOM.PONEDOMLauncher import SimpleDOMSimulation
from DOM.WaveformBuilder import WaveformBuilder
from PulseCleaning.TimeShifted import timeShift
from I3Tray import *                                                            
import random                                                                   
from icecube import icetray, dataclasses, dataio, simclasses                    
from icecube import phys_services, sim_services           
import argparse  
from Reconstruction.Linefit.LineFitReco import LineFitReco
from Reconstruction.Track.TrackReco import TrackReco
from PulseCleaning.SignificantHitPulseCleaning import SignificantHitPulseCleaning
from PulseCleaning.CausalHits import CausalPulseCleaning
#from Reconstruction.Cascade.CascadeReco import CascadeReco
from Trigger.DOMTrigger_miro import DOMTrigger_miro
from Trigger.DetectorTrigger import DetectorTrigger
from Trigger.GoodEvent import GoodEvent
#from Weighting.LeptonWeighter import LeptonWeighter

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outfile",type = str, default="./test_output.i3", help="Write output to OUTFILE (.i3{.gz} format)")
parser.add_argument("-i", "--infile",type=str, default="./test_input.i3", help="Read input from INFILE (.i3{.gz} format)")
parser.add_argument("-r", "--runnumber", type=int, default="10", help="The run/dataset number for this simulation, is used as seed for random generator")
parser.add_argument("-l", "--filenr",type=int,default=1, help="File number, stream of I3SPRNGRandomService")
parser.add_argument("-g", "--gcdfile",default=os.getenv('PONESRCDIR')+"/GCD/PONE_10spacing80.0String.i3.gz", help="Read in GCD file")
parser.add_argument("-t", "--pulsesep",default=0.2,help="Time needed to separate two pulses. Assume that this is 3.5*sample time.")
parser.add_argument("-e", "--ext",default=".zst",help="compression extension")
parser.add_argument("-s", "--dropstrings",nargs="+",default=[],help="Strings to exclude from geometry")
parser.add_argument("-n", "--nDOMs",type=int,default=2, help="Number of DOMs for detector trigger")
parser.add_argument("-f", "--LICconfig",type=str,default="",help="Path to the LIC configuration file for Lepton Injection events.")
parser.add_argument("-c", "--crossdir",  default=os.getenv('PONESRCDIR')+"/CrossSectionModels/csms_differential_v1.0",    help='path to cross section models')

tray = I3Tray()
#tray.AddService("I3EarthModelServiceFactory", "Earth")
args = parser.parse_args()
photon_series = "I3Photons"
#tray = I3Tray()

dropstrings = []
for string in args.dropstrings :
    dropstrings.append(int(string))

#from globals import max_num_files_per_dataset
randomService = phys_services.I3SPRNGRandomService(
                                                   seed = 1234567,
                                                   nstreams = 1000000,
                                                   streamnum = args.runnumber
                                                   )

tray.context['I3RandomService'] = randomService

infile = args.infile +str(args.runnumber)+".i3.gz"
outfile = args.outfile +str(args.runnumber)+".i3.gz"

tray.AddModule('I3Reader', 'reader',
            FilenameList = [args.gcdfile, infile]
            )

print(args.gcdfile)
gcd_file = dataio.I3File(args.gcdfile)


tray.AddModule(SimpleDOMSimulation, 'DOMLauncher',
               inputmap = photon_series,
               outputmap = 'PMTResponse',
               trueoutputmap = "triggerpulsemap_nonoise",
               RandomService = randomService,
               minTsep = args.pulsesep,
               SplitDoms = True,
               dropstrings = dropstrings,
               add_noise = False
              )


tray.AddModule(GoodEvent,'GoodEvent')

tray.AddModule(DOMTrigger_miro,"DOMTrigger_miro",
                inputmap = "triggerpulsemap_nonoise",
              )


tray.AddModule("I3Writer","writer",
               #SkipKeys = ["I3Photons","I3Photons_PMTResponse","TimeShiftedMCPEMap"],
               Filename = outfile,
               Streams = [icetray.I3Frame.DAQ, icetray.I3Frame.Physics, icetray.I3Frame.TrayInfo],
              )

tray.AddModule("TrashCan","adios")

tray.Execute()
tray.Finish()
