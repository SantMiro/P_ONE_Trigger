import argparse
from os.path import expandvars
import os, sys, random
from I3Tray import *
import random
from icecube import icetray, dataclasses, dataio, simclasses
from icecube import phys_services, sim_services
import numpy as np
import LeptonWeighter as LW
from icecube import LeptonInjector

#from Utilities.get_weight import get_weight

class Atm_Weighter(icetray.I3ConditionalModule):

    def __init__(self,context):
        icetray.I3ConditionalModule.__init__(self,context)
        self.AddParameter("fluxConst","Constant for flux parameterization",10**-18)
        self.AddParameter("fluxIndex","Index for flux parameteriazation",-2.53)
        self.AddParameter("fluxScale","Scale for flux parameterization",10**5)
        self.AddParameter('config','LIC file','config_100.lic')
        self.AddParameter('css','Cross-Section Location',"/home/users/mirosant/pone_offline/CrossSectionModels/csms_differential_v1.0")
        self.AddParameter('prop','Event Properties','EventProperties')
        self.AddParameter('astro','Astrophysical Flux','/home/users/mirosant/pone_offline/Weighting/Astrophysical_allsky_100GeV_100PeV.h5')
        self.AddParameter('atm','Atmospheric Conventional Flux','/home/users/mirosant/pone_offline/Weighting/Atmospheric_Conventional_allsky_100GeV_100PeV.h5')
        self.AddParameter('output','Output class','weight')
        self.AddOutBox('OutBox')

    def Configure(self):
        self.fluxConst    = self.GetParameter('fluxConst')
        self.fluxIndex    = self.GetParameter('FluxIndex')
        self.fluxScale    = self.GetParameter('fluxScale')
        self.config       = self.GetParameter('config')
        self.css          = self.GetParameter('css')
        self.atm          = self.GetParameter('atm')
        self.astro        = self.GetParameter('astro')
        self.prop         = self.GetParameter('prop')
        self.output       = self.GetParameter('output')

        self.atmospheric_flux   = LW.nuSQUIDSAtmFlux(self.atm)
        self.astrophysical_flux  = LW.nuSQUIDSAtmFlux(self.astro)

        self.flux       = LW.PowerLawFlux(self.fluxConst, self.fluxIndex, self.fluxScale)

        self.generation = LW.MakeGeneratorsFromLICFile(self.config)

        self.xs         = LW.CrossSectionFromSpline(
                                self.css+"/dsdxdy_nu_CC_iso.fits",
                                self.css+"/dsdxdy_nubar_CC_iso.fits",
                                self.css+"/dsdxdy_nu_NC_iso.fits",
                                self.css+"/dsdxdy_nubar_NC_iso.fits")

        self.weight_event = LW.Weighter([self.astrophysical_flux,self.atmospheric_flux], self.xs, self.generation)
        #self.weight_event = LW.Weighter(self.flux, self.xs, self.generation)

    def DAQ(self,frame):

        mctree = frame['I3MCTree']
        neutrino = mctree[0]
        props = frame[self.prop]
        LWevent = LW.Event()
        LWevent.energy = props.totalEnergy
        LWevent.zenith = props.zenith
        LWevent.azimuth = props.azimuth

        LWevent.interaction_x = props.finalStateX
        LWevent.interaction_y = props.finalStateY
        LWevent.final_state_particle_0 = LW.ParticleType( props.finalType1 )
        LWevent.final_state_particle_1 = LW.ParticleType( props.finalType2 )
        LWevent.primary_type = LW.ParticleType(props.initialType )
        LWevent.radius = props.impactParameter
        LWevent.total_column_depth = props.totalColumnDepth
        LWevent.x = neutrino.pos.x
        LWevent.y = neutrino.pos.y
        LWevent.z = neutrino.pos.z

        weight = self.weight_event(LWevent)
        weightone = self.weight_event.get_oneweight(LWevent)

        frame[self.output]       = dataclasses.I3Double(weight)
        frame['one'+self.output] = dataclasses.I3Double(weightone)
      
        self.PushFrame(frame)
