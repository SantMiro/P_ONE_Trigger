#!/usr/bin/env python

# import required icecube-related stuff
from icecube import icetray, dataclasses, simclasses, dataio
from icecube.icetray import I3Units
from I3Tray import I3Tray
import icecube.MuonGun
# command line options required to configure the simulation
import argparse
from os.path import expandvars
import os, sys
from icecube import phys_services
#from icecube.simprod.modules import Corsika5ComponentGenerator
from segments.GenerateCosmicRayMuons import GenerateSingleMuons, GenerateNaturalRateMuons
from segments import GenerateCosmicRayMuons, PropagateMuons
#from icecube.simprod import segments
from Utilities.GeoUtility import get_geo_from_gcd
from Examples.trackgeo import CylinderIntersection
from Generators import AtmosphericMuons



def printfunc(frame, message = 'test'):
	print(message)
	return True

parser = argparse.ArgumentParser()                                              
parser.add_argument("-o", "--outfile",type = str,default="./test_output.root",help="")
parser.add_argument("-r", "--run",type=int,default=10,help="")                                                       
parser.add_argument("-g", "--gcdfile",default=os.getenv('PONESRCDIR')+"/GCD/PONE_10spacing80.0String.i3.gz", help="Readin GCD file")
parser.add_argument("-n", "--nevents",type=int,default=1000,help="Number of events to run.")

args = parser.parse_args()

tray = I3Tray()
tray.AddModule('I3InfiniteSource',Prefix=args.gcdfile)

radius, height = get_geo_from_gcd(args.gcdfile)
print(radius, height)
randomService = phys_services.I3SPRNGRandomService(
                                  seed = args.run*args.run,
                              nstreams = 100000000,
                              streamnum = args.run)

tray.context['I3RandomService'] = randomService


tray.Add("I3MCEventHeaderGenerator",
               EventID=1,
               IncrementEventID=True)


tray.AddSegment(GenerateSingleMuons,"SingleMuons",
                #Surface = None,
                Surface = icecube.MuonGun.Cylinder(
                    length=height*icecube.icetray.I3Units.m,
                    radius=radius*icecube.icetray.I3Units.m),

                #GCDFile=args.gcdfile,
                GeometryMargin = 100.*I3Units.m,
		NumEvents=args.nevents,
		FromEnergy=10000,
		ToEnergy = 10000,
                BreakEnergy=700,
                GammaIndex = 2.,
                ZenithRange = [0.,180.*I3Units.deg]
                )

_kwargs = {"PROPOSAL_config_file":os.getenv('PONESRCDIR')+"/configs/PROPOSAL_config.json"}

tray.Add(PropagateMuons, 'ParticlePropagators',
                                  RandomService=randomService,
                                  SaveState=True,
                                  InputMCTreeName="I3MCTree_preMuonProp",
                                  OutputMCTreeName="I3MCTree",
                                  PROPOSAL_config_file=os.getenv('PONESRCDIR')+"/configs/PROPOSAL_config.json")



#tray.AddModule(CylinderIntersection, 'CylInt',
                #rad = radius,
                #track = 200.0)


tray.AddModule('I3Writer',   
                'writer',
                Streams=[icetray.I3Frame.Stream('S'),
                icetray.I3Frame.TrayInfo,
                icetray.I3Frame.DAQ],
                filename=args.outfile+".i3.gz")


tray.Execute()
tray.Finish()
