#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# exportjobflow.py
# DEC 2025
# pass in a job flow name and export the flow  

import argparse, sys, subprocess, uuid, time, os, glob, json

from sharedfunctions import getidsanduris, callrestapi, getapplicationproperties, printresult, getclicommand

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

# get input parameters
parser = argparse.ArgumentParser(description="Export a Viya Folder and its sub-folders")

parser.add_argument("-fn","--flowname", help="Folder path to export",default='HRAnalysysProject_Job_Flow_001')
parser.add_argument("--filename", help="File name and path without extension.",default="/tmp/jobflowrequest.json")
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')

args= parser.parse_args()

filename=args.flowname
flowname=args.flowname
debug=True
#filename=args.filename

# create a dictionary that will ultimately create the transfer requests file

data = {}


data["version"] = 1
data["name"] = flowname
data["description"] = "Created from pyviyatools flow name is:"+ flowname
data["items"] = []

# get URI of job flow
reqval="/jobFlowScheduling/flows?filter=eq(name,'"+flowname+"')"
flowresult=callrestapi(reqval,'get')

#if debug: print(json.dumps(flowresult, indent=4))

flowid = flowresult['items'][0]['id']

#get details of job flow
reqval="/jobFlowScheduling/flows/"+flowid
flowdetails=callrestapi(reqval,'get',acceptType="application/vnd.sas.schedule.flow+json")

data["items"].append(reqval)

if debug: print(json.dumps(flowdetails, indent=4))

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


print(json.dumps(data, indent=4))

#write out requests file

#with open(filename, "w") as f:
#     json.dump(data, f, indent=4)
