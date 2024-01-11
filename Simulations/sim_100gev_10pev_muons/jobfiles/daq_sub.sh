#!/bin/bash

bash /data/p-one/mirosant/pone_offline/env-shell_Container.sh python /data/p-one/mirosant/sim_100gev-10pev/Eventfiles/DAQSim.py -i /data/p-one/mirosant/sim_100gev-10pev/Propfiles/prop_ -o /data/p-one/mirosant/sim_100gev-10pev/DAQfiles/daq_ -r $1 -g /data/p-one/mirosant/pone_offline/GCD/PONE_10spacing80.0String.i3.gz 

