from icecube import icetray, dataclasses, dataio, simclasses
from icecube.icetray import I3Units, OMKey, I3Frame
from icecube.dataclasses import ModuleKey
import numpy as np
from math import sqrt
from copy import deepcopy
import collections
from time import process_time

class DOMTrigger_miro(icetray.I3ConditionalModule):
    """
    Simple Implementation of the PMT response.
    """

    def __init__(self, context):
        icetray.I3ConditionalModule.__init__(self, context)
        self.AddParameter("output","Append the outputs",'')
        self.AddParameter("inputmap","Name of the Physics I3MCTree name","I3RecoPulseSeriesMap")
        #self.AddParameter("PEthreshold"," Pulse charge threshold",0.25)
        #self.AddParameter("CutOnTrigger","Cut events that do not trigger.",False)
        self.AddParameter("ncoin","",3)
        self.AddParameter("TimeWindow","",10)
        #self.AddParameter("SingleStringNRows","",3)
        #self.AddParameter("ForceAdjacency","Require adjacency ",True)
        self.AddOutBox("OutBox")

    def Configure(self):

        self.output = self.GetParameter("output")
        self.inputmap = self.GetParameter("inputmap")
        self.ncoin = self.GetParameter("ncoin")
        self.TimeWindow = self.GetParameter("TimeWindow")
        #self.PEthreshold = self.GetParameter("PEthreshold")
        #self.SingleDOMCoincidenceN = self.GetParameter("SingleDOMCoincidenceN")
        #self.SingleDOMCoincidenceWindow = self.GetParameter("SingleDOMCoincidenceWindow")

    def Geometry(self,frame):
        self.domsUsed = frame['I3Geometry'].omgeo
        self.PushFrame(frame)


    def Simulation(self,frame) :

        frame["SingleDOMCoincidenceN"+self.output] = dataclasses.I3Double(self.ncoin)
        frame["SingleDOMCoincidenceWindow"+self.output] = dataclasses.I3Double(self.TimeWindow)
        self.PushFrame(frame)

    def DAQ(self,frame) :

        #print("DOM Trigger Start")

        #Select key
        triggermap = frame[self.inputmap]
        #frame['triggerpulsemap']

        #Create variables
        DOM = {}
        PMT = {}
        event = {}
        coin = {}
        times = {}
        ezlist = {}

        DOMcoin = dataclasses.I3MapKeyVectorInt()

        #Fill lists with pulses
        for omkey in triggermap.keys():
            DOM[omkey] = {}
            PMT[omkey] = set()

            event[omkey] = list()
            pulses = triggermap[omkey]
            times[omkey] = list()

            for i, pulse in enumerate(pulses):
                time = int(pulse.time)
                if time not in DOM[omkey].keys():
                    DOM[omkey][time] = {int(pulse.width)}
                    times[omkey].append(time)
                    PMT[omkey].add(int(pulse.width))
                else:
                    DOM[omkey][time].add(int(pulse.width))
                    PMT[omkey].add(int(pulse.width))

            #Go through lists of event for "N"ns event.
            sel_event = list()
            for i in range(len(DOM[omkey])):
              coin[omkey] = list()
                for j in range(self.TimeWindow):
                    if times[omkey][i] + j in times[omkey]:
                        t = times[omkey][i] + j
                        coin[omkey].append(list(DOM[omkey][t]))

                sel_event.append(coin[omkey])

            #Selection of true event
            event[omkey] = set([item for sublist in sel_event[0] for item in sublist])

            #Iteration between pulses
            for k in range(len(sel_event)):
                ezlist[omkey] = [item for sublist in sel_event[k] for item in sublist]
                prefin = event[omkey] & set(ezlist[omkey])

                if len(event[omkey]) >= len(ezlist[omkey]) and len(prefin) > 0:
                    continue
                elif len(event[omkey]) >= len(ezlist[omkey]) and len(prefin) == 0:
                    continue
                elif len(event[omkey]) < len(ezlist[omkey]) and len(prefin) > 0:
                    event[omkey] = set(ezlist[omkey])
                else:
                    event[omkey] = set(ezlist[omkey])

            doms = list()
            #if len(event[omkey]) >= self.ncoin:
            doms.append(len(event[omkey]))
            DOMcoin[omkey] = doms
        #frame["DOMTrigger_time"+self.output] = DOMCoincidence_time
        frame["DOMTrigger_ncoin"+self.output] = DOMcoin
        #frame["DOMTrigger_pmts"+self.output] = DOMCoincidence_pmts
        #print("DOM Trigger End")
        self.PushFrame(frame)


