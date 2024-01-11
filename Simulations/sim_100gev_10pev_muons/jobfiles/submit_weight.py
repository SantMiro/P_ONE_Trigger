#!/usr/bin/env python
import os, sys
import subprocess

opts = {}
opts["root"]    = '/data/p-one/mirosant/sim051/'
opts["out"]     = '/data/p-one/mirosant/sim051/Weightfiles'
opts["job"]     = '/data/p-one/mirosant/sim051/jobfiles'
opts['in']      = '/data/p-one/mirosant/sim051/Genfiles'

processfilename = 'weight_sub'
submissionfilename = 'weight_sub.submit'

job_string = '''#!/bin/bash

bash /home/users/mirosant/pone_offline/env-shell_Container.sh python {}/Weight_Calculator.py -i {} -o {} -f {} -r $1 

'''.format(opts["root"]+"Eventfiles",
           opts['in']+"/gen_",
           opts["out"]+"/weight_",
           opts['root']+"Configfiles/config_")

with open(opts["job"] + "/" + processfilename + '.sh', 'w') as ofile:
        ofile.write(job_string)
        subprocess.Popen(['chmod','777',opts["job"] + "/" +  processfilename + '.sh'])

submit_string = '''
executable = {}/{}

Arguments = $(Item)
output = {}_$(Item).out
error = {}_$(Item).err
log = {}_$(Item).log

+SingularityImage = "/data/p-one/icetray_offline_lw.sif"

Universe = vanilla
request_memory = 4GB
request_cpus = 1
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
                               
