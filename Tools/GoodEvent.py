import numpy as np
import sys
from icecube import icetray,dataio,dataclasses,simclasses,phys_services

class GoodEvent(icetray.I3ConditionalModule):

    def __init__(self,context):
        icetray.I3ConditionalModule.__init__(self,context)
        self.AddParameter('input','Name of inputmap','triggerpulsemap_nonoise')
        self.AddParameter('MinDoms','Minimum number of DOMs',5)
        self.AddParameter('IntStrings','Internal Strings',True)
        self.AddParameter('Output','Name of output','good_event')
        self.AddOutBox('OutBox')

    def Configure(self):
        self.input = self.GetParameter('input')
        self.MinDoms = self.GetParameter('MinDoms')
        self.IntStrings = self.GetParameter('IntStrings')
        self.Output = self.GetParameter('Output')


    def DAQ(self,frame):

        dom_response = frame[self.input]

        number_doms = len(dom_response)

        if number_doms >= self.MinDoms:
            event = dataclasses.I3Double(number_doms)

            frame[self.Output] = event

        else:

            return

        self.PushFrame(frame)
