#!/bin/bash

bash /data/p-one/mirosant/pone_offline/env-shell_Container.sh python /data/p-one/mirosant/sim_10tev/Eventfiles/DAQSim.py -i /data/p-one/mirosant/sim_10tev/Propfiles/prop_ -o /data/p-one/mirosant/sim_10tev/DAQfiles/daq_ -r $1 -g /data/p-one/mirosant/pone_offline/GCD/PONE_10spacing50.0String.i3.gz 

