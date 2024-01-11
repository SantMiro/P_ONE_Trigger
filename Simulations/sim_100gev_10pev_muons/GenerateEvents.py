from I3Tray import *
from icecube import icetray, dataio, dataclasses
from icecube import phys_services
from icecube import LeptonInjector
from icecube.icetray import I3Units
from icecube import PROPOSAL
from segments import PropagateMuons
import os
from os.path import expandvars
import numpy as np
import argparse
from Trigger.MuonEnergy import MuonEnergy

parser = argparse.ArgumentParser(description = "A scripts to run the neutrino generation simulation step using Neutrino Generator")

parser.add_argument('-emin', '--energyMin', default = 2.0,                                            help="the minimum energy")
parser.add_argument('-emax', '--energyMax', default = 7.0,                                            help="the maximum energy")
parser.add_argument('-n',    '--numEvents', default = 1000,                                           help="number of events produced by the simulation")
parser.add_argument('-o',    '--outfile',   default = "/data/p-one/mirosant/sim005/Genfiles/output",                                    help="name and path of output file")
parser.add_argument('-r',    '--runNum',    default = 0,                                              help="run Number")
parser.add_argument("-c",    "--crossdir",  default=os.getenv('PONESRCDIR')+"/CrossSectionModels/csms_differential_v1.0",    help='path to cross section models')
parser.add_argument("-x",    "--config",    default="",help="")

args = parser.parse_args()

emin = float(args.energyMin)
emax = float(args.energyMax)
numEvents = int(args.numEvents)
runNum = int(args.runNum)

tray = I3Tray()

#Random
randomService = phys_services.I3GSLRandomService(seed=10*int(args.runNum))
tray.context["I3RandomService"] = randomService
tray.AddModule("I3InfiniteSource", "TheSource", Stream=icetray.I3Frame.DAQ)

tray.Add("I3EarthModelServiceFactory", "Earth",
                EarthModels = ['../'*20+'data/p-one/icetray_offline/src/earthmodel-service/resources/earthparams/densities/PREM_pone'],
                MaterialModels = ["Standard"],
                IceCapType = "IceSheet",
                DetectorDepth = (2600-500)*I3Units.m,
                PathToDataFileDir = "")


injector_list = []
injector_list.append(
    LeptonInjector.injector(
        NEvents         = numEvents,
        FinalType1      = dataclasses.I3Particle.ParticleType.MuMinus,
        FinalType2      = dataclasses.I3Particle.ParticleType.Hadrons,
        DoublyDifferentialCrossSectionFile  = args.crossdir + "/dsdxdy_nu_CC_iso.fits",
        TotalCrossSectionFile               = args.crossdir + "/sigma_nu_CC_iso.fits",
        Ranged = True)
    )

tray.AddModule("MultiLeptonInjector",
    EarthModel      = "Earth",
    Generators      = injector_list,
    MinimumEnergy   = (10.0**(args.energyMin)) * I3Units.GeV,
    MaximumEnergy   = (10.0**(args.energyMax)) * I3Units.GeV,
    MinimumZenith   = 0. * I3Units.deg,
    MaximumZenith   = 180. * I3Units.deg,
    PowerLawIndex   = 1.,
    InjectionRadius = 600 * I3Units.meter,
    EndcapLength    = 700 * I3Units.meter,
    #CylinderRadius  = 700 * I3Units.meter,
    #CylinderHeight  = 1000 * I3Units.meter,
    MinimumAzimuth  = 0. * I3Units.deg,
    MaximumAzimuth  = 360. * I3Units.deg,
    RandomService   = "I3RandomService")



#tray.AddModule(MuonEnergy,'MuonEnergy')

tray.Add(PropagateMuons, 'ParticlePropagators',
         RandomService=randomService,
         SaveState=True,
         InputMCTreeName="I3MCTree",
         OutputMCTreeName="I3MCTree_postprop",
         PROPOSAL_config_file=os.getenv('PONESRCDIR')+"/configs/PROPOSAL_config.json")

#tray.AddModule(MuonEnergy,'MuonEnergy')

event_id = 1
def get_header(frame):
    global event_id
    header          = dataclasses.I3EventHeader()
    header.event_id = event_id
    header.run_id   = int(args.runNum)
    frame["I3EventHeader"] = header

    event_id += 1

tray.AddModule(get_header, streams = [icetray.I3Frame.DAQ])

tray.Add("I3Writer", filename = args.outfile+"_"+str(args.runNum)+".i3.gz",
        streams = [icetray.I3Frame.TrayInfo, icetray.I3Frame.Simulation, icetray.I3Frame.DAQ],)

tray.Execute()
