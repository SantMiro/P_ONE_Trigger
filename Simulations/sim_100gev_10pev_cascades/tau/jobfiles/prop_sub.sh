#!/bin/bash

bash /data/p-one/mirosant/pone_offline/env-shell_Container.sh python /data/p-one/mirosant/sim_10tev_cascade/tau/Eventfiles/PropogatePhotons.py -i /data/p-one/mirosant/sim_10tev_cascade/tau/Genfiles/gen_ -o /data/p-one/mirosant/sim_10tev_cascade/tau/Propfiles/prop_ -r $1 -g /data/p-one/mirosant/pone_offline/GCD/PONE_10spacing80.0String.i3.gz

