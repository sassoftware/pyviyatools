#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# exportjobflow.py
# DEC 2025
# pass in a job flow name and export the flow  

import argparse, sys, subprocess, uuid, time, os, glob, json, tempfile, re

from sharedfunctions import getidsanduris, callrestapi, getapplicationproperties, printresult, getclicommand

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

# get input parameters
parser = argparse.ArgumentParser(description="Export a Viya Folder and its sub-folders")

parser.add_argument("-fn","--flowname", help="Folder path to export",default='HRAnalysysProject_Job_Flow_001')
parser.add_argument("--filename", help="Full path to package file. Optional, default name is in temp with the same name as the flow",default="XNOFILENAMEX")
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
parser.add_argument("--debug", action='store_true', help="Debug")

args= parser.parse_args()

filename=args.flowname
flowname=args.flowname
debug=args.debug
filename=args.filename

# create a dictionary that will ultimately create the transfer requests file
data = {}


# get URI of job flow
reqval="/jobFlowScheduling/flows?filter=eq(name,'"+flowname+"')"
flowresult=callrestapi(reqval,'get')

#if debug: print(json.dumps(flowresult, indent=4))

flowid = flowresult['items'][0]['id']

#get details of job flow
reqval="/jobFlowScheduling/flows/"+flowid
flowdetails=callrestapi(reqval,'get',acceptType="application/vnd.sas.schedule.flow+json")
if debug: print(json.dumps(flowdetails, indent=4))

flow_actual_name=flowdetails["name"]

# add top level details
data["version"] = 1
data["name"] = flow_actual_name
data["description"] = "Created from pyviyatools flow name is:"+ flow_actual_name
data["items"] = []
data["items"].append(reqval)

# get job actions from the flow and add them to the requests file
# A job action is created when you add a job request to a flow. Job actions are only visible within flows. 
#The job action references the job request and includes other information related to priority etc.

jobs=flowdetails["jobs"]

for job in jobs:
    data["items"].append(job)

    # for each job action get the job request

    jobactresult=callrestapi(job,"get",acceptType="application/vnd.sas.schedule.job+json")
    jobrequestURI=jobactresult["jobRequestUri"]
    data["items"].append(jobrequestURI)

    jobrequestdetails=callrestapi(jobrequestURI,"get",acceptType="application/vnd.sas.job.execution.job.request+json")
    jobDefinitionUri=jobrequestdetails["jobDefinitionUri"]
    data["items"].append(jobDefinitionUri)

# with debug print the requests file content
if debug: print(json.dumps(data, indent=4))


package_name=flow_actual_name+flowid
request_file_name=package_name+".json"
temp_dir = tempfile.gettempdir() 
requests_full_path = os.path.join(temp_dir, request_file_name)

#Write to requests file
with open(requests_full_path, "w") as f:
    json.dump(data, f, indent=4)


command=clicommand+' transfer export --request @/'+requests_full_path+' --name "'+package_name+'"'
print(command)

# Run the command and capture output
result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

# Get the stdout
output = result.stdout.strip()
print("Command output:", output)

# Extract the ID using regex
match = re.search(r'ID\s([a-f0-9\-]+)', output)
if match:
    package_id = match.group(1)
    print("Captured ID:", package_id)

# if filename does not include .json extension add it

if filename =="XNOFILENAMEX" : completefile=os.path.join(temp_dir, package_name)
else: completefile=filename

if not completefile.lower().endswith(".json"):
    completefile += ".json"

command=clicommand+' transfer download --file '+completefile+' --id '+package_id
print(command)
subprocess.call(command, shell=True)
print("NOTE: Viya Job Flow and dependent objects "+flow_actual_name+ "  exported to json file "+completefile)

""" if autotranferremove:
        print(clicommand+' transfer delete --id '+package_id+"\n")
        remTransferObject = subprocess.Popen(clicommand+' transfer delete --id '+package_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        remTransferObjectOutput = remTransferObject.communicate(b'Y\n')
        remTransferObject.wait()
 """

