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
#Distance
sim = '100'
dis = 100
# Input file
root ='/data/p-one/mirosant/sim_10tev-10pev/'+sim+'/DAQfiles/'
files = os.listdir(root)

#Set number of events in file and set min and max number of DOMS

max_doms = 20
min_doms = 5
pmts=6

#Build dictionaries
DOMtrig = {}
Weights = {}
DOMres = {j: [] for j in range(min_doms, max_doms)}

for j in DOMres:
    DOMtrig[j] = {k: [] for k in range(1, pmts+1)}
    Weights[j] = {k: [] for k in range(1, pmts+1)}

# t is year in seconds. z is max number of doms
z = 0
t=3600*24*365

#Take one event, see if satisfies a multiple DOM trigger, then if stafies a minimum DOM response and then if it satisfies an n-pmt coincidence. Save events that stasfied conditions.


for i in files:
    infile = dataio.I3File(root+i)
    while infile.more():
        try:
            frame = infile.pop_daq()
        except:
            continue
    #n_doms: number of hits in a DOM in the event.
    #weights: weight of the event
    #DOMtrig: list of DOM hits if event triggered.
    #Weights: weight of the event triggered.
        n_doms = frame['DOMTrigger_ncoin']
        weights = frame['weight']
        if len(n_doms) > z:
            z = len(n_doms)
        for j in DOMres:
            if len(n_doms) >= j:
                DOMres[j].append(len(n_doms))
                for k in range(1, pmts+1):
                    count = 0
                    for l in range(len(n_doms.values())):
                        if n_doms.values()[l][0] >= k:
                            flat_list = [item for sublist in n_doms.values() for item in sublist]
                            DOMtrig[j][k].append(flat_list)
                            Weights[j][k].append(weights.value*t/200)
                            break



filee = open('DOMtrig_'+str(dis)+'.pkl', 'wb')
pkl.dump(DOMtrig, filee)
filee.close()

filee = open('Weights_'+str(dis)+'.pkl', 'wb')
pkl.dump(Weights, filee)
filee.close()



