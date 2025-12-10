#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# exportjobflow.py
# DEC 2025
# pass in a job flow name or a JSON file with a list of flows and export the flow(s)
# to create a flow file for input use the sas-viya CLI
# sas-viya --output json job flows list > /tmp/flowlist.json
# Example usage:
# python exportjobflow.py -fn "My Job Flow Name" -d /my/export/directory
# python exportjobflow.py -ff /tmp/flowlist.json -d /my/export/directory --transferremove

import argparse, sys, subprocess, uuid, time, os, glob, json, tempfile, re

from sharedfunctions import getidsanduris, callrestapi, getapplicationproperties, printresult, getclicommand, file_accessible

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

# get input parameters
parser = argparse.ArgumentParser(description="Export a Viya Job Flow or Flows to packages.")

# Mutually exclusive: exactly one must be provided
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "-fn", "--flowname",
    help="Flow name to export (Viya Job Flow object name). Choose this or pass a flowfile."
)
group.add_argument(
    "-ff", "--flowfile",
    help="Path to an existing flow definition file to export. Choose this or pass a flowname."
)

parser.add_argument("-d","--directory", help="Directory to store Export Packages",required='True',default="TEMP")
parser.add_argument("-t","--transferremove", help="Remove transfer package from SAS Viya after download to JSON file", action='store_true')
parser.add_argument("--debug", action='store_true', help="Debug: shows the requests file created")

# parse the arguments
args= parser.parse_args()

flowname=args.flowname
flowfile=args.flowfile
directory=args.directory
debug=args.debug
autotransferremove=args.transferremove

if flowfile is not None: 
    check=file_accessible(flowfile,'r')
    if not check:
        print("ERROR: Flow definition file "+flowfile+" does not exist or not accessible. Please check the path and try again.")
        sys.exit()

# create directory if it doesn't exist
if not os.path.exists(directory) and directory != "TEMP" : os.makedirs(directory)


def exportflow(flowname):

    # create a dictionary that will ultimately create the transfer requests file
    data = {}
    # get URI of job flow
    reqval="/jobFlowScheduling/flows?filter=eq(name,'"+flowname+"')"
    flowresult=callrestapi(reqval,'get')

    #check how many flows returned and print the names  
    # if debug: print("Number of flows found with name "+flowname+" is "+str(flowresult['count']))
    if flowresult['count'] == 0:
        print("ERROR: No job flow found with name "+flowname+'. Please check the name and try again.')
        sys.exit()
    elif flowresult['count'] > 1:
        print("ERROR: More than one job flow found with name "+flowname+", please make the name is unique")
        for item in flowresult['items']:
            print("  ID: "+item['id']+"  Name: "+item['name'])
        sys.exit()  

    if debug: print(json.dumps(flowresult, indent=4))

    flowid = flowresult['items'][0]['id']

    #get details of job flow
    reqval="/jobFlowScheduling/flows/"+flowid
    flowdetails=callrestapi(reqval,'get',acceptType="application/vnd.sas.schedule.flow+json")
    
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

    # get jobs in the flow
    jobs=flowdetails["jobs"]
   
    # for each job in the flow get the job action details
    for job in jobs:
        
        if "/flows/" in job:
        # if the job is a flow skip for now
            print("WARNING: Nested flows are not currently supported. Skipping nested flow "+job)
            continue

        data["items"].append(job)
    
        # for each job action get the job request 
        jobactresult=callrestapi(job,"get",acceptType="application/vnd.sas.schedule.job+json")

        if debug: print(json.dumps(jobactresult, indent=4))

        # get job request URI and add to requests file if present
        if "jobRequestUri" in jobactresult:
            jobrequestURI=jobactresult["jobRequestUri"]
            data["items"].append(jobrequestURI)

            jobrequestdetails=callrestapi(jobrequestURI,"get",acceptType="application/vnd.sas.job.execution.job.request+json")
            
            # get job definition URI and add to requests file if present
            if "jobDefinitionUri" in jobactresult:
               
                jobDefinitionUri=jobrequestdetails["jobDefinitionUri"]
                data["items"].append(jobDefinitionUri)

    # create a temp file to hold the requests file that we build
    package_name=flow_actual_name+flowid
    request_file_name=package_name+".json"
    temp_dir = tempfile.gettempdir() 
    requests_full_path = os.path.join(temp_dir, request_file_name)

    #Write to requests file
    with open(requests_full_path, "w") as f:
        json.dump(data, f, indent=4)

    # build the export command
    command=clicommand+' transfer export --request @"'+requests_full_path+'" --name "'+package_name+'"'
    print(command)

    # Run the command and capture output 
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Get the stdout
    output = result.stdout.strip()
    #print("Command output:", output)

    # Extract the ID using regex
    match = re.search(r'ID\s([a-f0-9\-]+)', output)
    if match:
        package_id = match.group(1)
        print("Captured ID:", package_id)

    # if no directory specified create one in the temp directory with the flow name
    if directory =="TEMP" : completefile=os.path.join(temp_dir, flowname)
    else: completefile=os.path.join(directory, flowname)

    # if filename does not include .json extension add it
    if not completefile.lower().endswith(".json"):
        completefile += ".json"

    # download the package to a file
    command=clicommand+' transfer download --file "'+completefile+'" --id '+package_id
    print(command)
    rc=subprocess.call(command, shell=True)

    # if autotranferremove is set remove the transfer package from Viya infrastructure data server
    if autotransferremove:
        print(clicommand+' transfer delete --id '+package_id+"\n")
        remTransferObject = subprocess.Popen(clicommand+' transfer delete --id '+package_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        remTransferObjectOutput = remTransferObject.communicate(b'Y\n')
        remTransferObject.wait()

    # with debug print the requests file content
    if debug: print(json.dumps(data, indent=4))

    if rc == 0:
        print("NOTE: Viya Job Flow "+flow_actual_name+ " and dependent objects exported to json file "+completefile)
    else:
        print("WARNING: there may be a problem exporting Viya Job Flow "+flow_actual_name+ " to json file "+completefile)

if flowfile is not None:
    # read the flow definition file and get the flow name
    print("NOTE: Reading flow list file "+flowfile)
    with open(flowfile, "r") as f:
        data = json.load(f)
    
    for item in data["items"]:
        flowname=item["name"]
        exportflow(flowname)
else:
    print("NOTE: Export a singleflow  "+flowname)
    exportflow(flowname)
