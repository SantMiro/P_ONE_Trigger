#!/usr/bin/env python
import os, sys
import subprocess

opts = {}
sim = '100'
opts["root"] = '/data/p-one/mirosant/sim_10tev-10pev/'
opts["out"] = '/data/p-one/mirosant/sim_10tev-10pev/'+sim+'/Propfiles'
opts["job"] = '/data/p-one/mirosant/sim_10tev-10pev/jobfiles'
opts["in"] = '/data/p-one/mirosant/sim_10tev-10pev/Genfiles'

processfilename = 'prop_sub'
submissionfilename = 'prop_sub.submit'

job_string = '''#!/bin/bash

bash /data/p-one/mirosant/pone_offline/env-shell_Container.sh python {}/PropogatePhotons.py -i {} -o {} -r $1 -g {}

'''.format(opts["root"]+"Eventfiles",
           opts["in"]+"/gen_",
           opts["out"]+"/prop_",
           "/data/p-one/mirosant/pone_offline/GCD/PONE_10spacing100.0String.i3.gz")

with open(opts["job"] + "/" + processfilename + '.sh', 'w') as ofile:
        ofile.write(job_string)
        subprocess.Popen(['chmod','777',opts["job"] + "/" +  processfilename + '.sh'])

submit_string = '''
executable = {}/{}

Arguments = $(Item)
output = {}_$(Item).out
error = {}_$(Item).err
log = {}_$(Item).log

+SingularityImage = "/data/p-one/icetray_offline.sif"

Universe = vanilla
request_memory = 4GB
request_cpus = 1
request_gpus = 1
requirements = HasSingularity
requirements = CUDADeviceName == "NVIDIA TITAN Xp"

notification = never

+TransferOutput=""

queue from seq {} {} |
'''.format(opts["job"],
           processfilename + '.sh',
           opts["root"]+"/logfiles/"+processfilename,
           opts["root"]+"/logfiles/"+processfilename,
           opts["root"]+"/logfiles/"+processfilename,
           1,100)

with open(opts["job"] + '/' + submissionfilename, 'w') as ofile:
        ofile.write(submit_string)

submit = subprocess.Popen(['condor_submit',opts["job"] + '/' + submissionfilename])
