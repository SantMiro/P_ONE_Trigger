import pickle as pkl
import numpy as np
import sys
from icecube import icetray, dataio, dataclasses, simclasses, phys_services, filterscripts, gulliver, recclasses
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import style
#from math import comb
from math import factorial
from collections import Counter
import os


#Combinatory function
def nCr(n,r):
    f = factorial
    return f(n) // f(r) // f(n-r)

# Input file and skip first to frames
root = '/data/p-one/mirosant/sim_10tev_cascade/electron/DAQfiles/'
files = os.listdir(root)

#Set number of events in file and set min and max number of DOMS
#events = 1580
max_doms = 35
min_doms = 5
pmts=6
#Build dictionaries
DOMtrig = {}
neutrino_energy = {}
DOMres = {j: [] for j in range(min_doms, max_doms)}


for j in DOMres:
    DOMtrig[j] = {k: [] for k in range(1, pmts+1)}
    neutrino_energy[j] = {k: [] for k in range(1, pmts+1)}

z = 0
#Take one event, see if satisfies a multiple DOM trigger, then if stafies a minimum DOM response and then if it satisfies an n-pmt coincidence. Save events that stasfied conditions.
for i in files:
    infile = dataio.I3File(root+i)
    while infile.more():
            frame = infile.pop_daq()
        #n_doms: number of hits in a DOM in the event.
            n_doms = frame['DOMTrigger_ncoin']
            neutrino = frame['I3MCTree']
            energy = neutrino[0].energy
            pos = [neutrino[0].pos.x,neutrino[0].pos.y,neutrino[0].pos.z]
            if len(n_doms) > z:
                z = len(n_doms)
    
            for j in DOMres:
                if len(n_doms) >= j:
                    DOMres[j].append(len(n_doms))
                    for k in range(1, pmts+1):
                        count = 0
                        for l in range(len(n_doms.values())):
                            if n_doms.values()[l][0] >= k:
                                r = np.sqrt(pos[1]**2+pos[0]**2)
                                d = np.sqrt(r**2 + pos[2]**2)
                                if r <= 160 and pos[2] <= 500:
                                    flat_list = [item for sublist in n_doms.values() for item in sublist]
                                    DOMtrig[j][k].append(flat_list)
                                    neutrino_energy[j][k].append(energy)
                                    break

print(z)


filee = open('DOMtrig.pkl', 'wb')
pkl.dump(DOMtrig, filee)
filee.close()

########################
## MEASURED EFFICIENCY##

DOMhist = {i: {j: len(DOMtrig[i][j]) for j in DOMtrig[i].keys()} for i in DOMtrig.keys()}
totalDOMS = {i: len(DOMtrig[i][1]) for i in DOMtrig.keys()}


eff = {i: {j: (DOMhist[i][j])/(DOMhist[i][1]) for j in DOMtrig[i].keys()} for i in DOMtrig.keys()}

eff_error = {i: {j: (1/totalDOMS[i])*np.sqrt(DOMhist[i][j]*(1-(DOMhist[i][j]/totalDOMS[i]))) for j in DOMtrig[i].keys()} for i in DOMtrig.keys()}

##STRAW RATES ##

f = open('straw_rates.pkl','rb')
straw_rates = pkl.load(f)
f.close()

## ZERO SUPPRESSION ##

rates = straw_rates['rates']
ctf  = straw_rates['cumulative_time_fraction']

fraction = dict(zip(rates, ctf))

energy_bins = np.logspace(np.log10(100),np.log10(10000000),21)
print(energy_bins)

zero = {2:{i : float() for i in energy_bins},3:{i : float() for i in energy_bins}}
zero_error = {2:{i : float() for i in energy_bins},3:{i : float() for i in energy_bins}}


for n in [2,3]:
    if n == 2:
        time_fraction = ctf[44]
    else:
        time_fraction = ctf[54]
    for i in range(len(energy_bins)-1):
        efficiency = []
        for event in range(len(DOMtrig[5][1])):
            if neutrino_energy[5][1][event] >= energy_bins[i] and neutrino_energy[5][1][event] <= energy_bins[i+1]:
                eff_event = 1 
                for dom in DOMtrig[5][1][event]:
                    if dom >= n:
                        for new_dom in DOMtrig[5][1][event]:
                            if new_dom >= n and new_dom < 8:
                                dead_time = sum(nCr(8,r)*nCr(8,new_dom-r) for r in range(n+1))/nCr(16,new_dom)
                                eff_event = eff_event * (1-time_fraction)*dead_time
                            elif new_dom >= 8:
                                eff_event = eff_event * (1-time_fraction)
                            else:
                                continue
                        break
                    else:
                        continue
                efficiency.append(1-eff_event)
        if len(efficiency) != 0:
            zero[n][energy_bins[i+1]] = (sum(efficiency)/len(efficiency))
            s = [(efficiency[k]-zero[n][energy_bins[i+1]])**2 for k in range(len(efficiency))]
            zero_error[n][energy_bins[i+1]] = np.sqrt(sum(s))/len(efficiency)
            

## FRACTION OF EVENTS ##
f = open('times_half.pkl', 'rb')
times_ind = pkl.load(f)
f.close()

## ADAPTIVE TIGGER ##

adaptive = {31.622776601683793:{},2154.4346900318824:{}}
adaptive_error = {31.622776601683793:{},2154.4346900318824:{}}
for j in adaptive:
    adaptive[j] = {i: float() for i in energy_bins}
    adaptive_error[j] = {i: float() for i in energy_bins}
for key in adaptive:
    for i in range(len(energy_bins)-1):
        efficiency = []
        for event in range(len(DOMtrig[5][1])):
            if neutrino_energy[5][1][event] >= energy_bins[i] and neutrino_energy[5][1][event] <= energy_bins[i+1]:
                eff_event = 1
                for dom in DOMtrig[5][1][event]:
                    if dom > 1 and dom < 6:
                        eff_event = eff_event*(1-sum(times_ind[key][:dom-1]))
                    elif dom >= 6:
                        eff_event= eff_event*0
                    else:
                        eff_event = eff_event*1

                efficiency.append(1-eff_event)
        if len(efficiency) != 0:
            adaptive[key][energy_bins[i+1]]=(sum(efficiency)/len(efficiency))
            s = [(efficiency[n]-adaptive[key][energy_bins[i+1]])**2 for n in range(len(efficiency))]
            adaptive_error[key][energy_bins[i+1]] = np.sqrt(sum(s))/len(efficiency)
    


print('adaptive',adaptive,'zero',zero)


probs = {'eff':eff, 'eff_error':eff_error,'adaptive':adaptive,'adaptive_error':adaptive_error,'zero':zero,'zero_error':zero_error}

f = open('probabilities.pkl', 'wb')
pkl.dump(probs, f)
f.close()

