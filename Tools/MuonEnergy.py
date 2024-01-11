import numpy as np
import sys
from icecube import icetray,dataio,dataclasses,simclasses,phys_services
'''This class filters events that have at least MinEnergy at the point of closest approach to the origin of the detector.
'''

class MuonEnergy(icetray.I3ConditionalModule):

    def __init__(self,context):
        icetray.I3ConditionalModule.__init__(self,context)
        self.AddParameter('input','Name of inputmap','MMCTrackList')
        self.AddParameter('MinEnergy','Minimum Muon Energy',10000.0)
        self.AddParameter('Output','Name of output','muon_energy')
        self.AddOutBox('OutBox')

    def Configure(self):
        self.input = self.GetParameter('input')
        self.MinEnergy = self.GetParameter('MinEnergy')
        self.Output = self.GetParameter('Output')


    def DAQ(self,frame):

        mctree = frame[self.input]

        muon_energy = mctree[0].Ec

        if muon_energy >= self.MinEnergy:

            energy = dataclasses.I3Double(muon_energy)

            frame[self.Output] = energy

        else:

            return

        self.PushFrame(frame)
