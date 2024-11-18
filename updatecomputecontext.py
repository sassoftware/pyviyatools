#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# updatecomputecontext.py
# November 2024
#
# Update an existing compute context from a JSON file.
#
#
# Change History
#
# Copyright © 2024, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
#  OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
#
# Import Python modules
import argparse, sys, json
from sharedfunctions import callrestapi,getinputjson,file_accessible

debug=False

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print (exception_type.__name__, exception)

sys.excepthook = exception_handler

# get input parameters
parser = argparse.ArgumentParser(description="Update an existing compute context from a JSON file.")
parser.add_argument("-n","--name", help="Compute context name",required='True')
parser.add_argument("-f","--file", help="JSON file containing updated definition of existing compute context.",required='True')
args= parser.parse_args()
contextname=args.name
contextdefinitionfilename=str(args.file)

# get python version
#version=int(str(sys.version_info[0]))
#print("Python version: " + str(version))

# Get compute contexts
reqtype="get"
reqval="/compute/contexts/?filter=eq(name, '"+contextname+"')"
resultdata=callrestapi(reqval,reqtype)
#json_formatted_str = json.dumps(resultdata, indent=2)
#print(json_formatted_str)

# This tool is intended to update an existing context, so check it exists and get its id
id=None
if 'items' in resultdata:
    #print(resultdata['items'])
    if resultdata['items']==[]:
        raise Exception("Compute context '"+contextname+"' not found.")
    elif len(resultdata['items'])>1:
        raise Exception("More than one matching compute context named '"+contextname+"'")
    # If we make it this far, we found exactly one compute context
    for i in resultdata['items']:
        id=i['id']
        print("Compute context: '"+contextname+"' found in SAS Viya deployment with id: "+id)
else:
    # Handle the error! Compute context not found...
    raise Exception('Compute context not found.')

# Check the file passed in contains valid JSON for the same compute context
# Load the fine into a python dictionary
check=file_accessible(contextdefinitionfilename,'r')
if check:
    inputcontextdict=getinputjson(contextdefinitionfilename)
else:
    raise Exception("Cannot open input file '"+contextdefinitionfilename+"'")

if 'name' in inputcontextdict:
    #print(inputcontextdict['name'])
    if inputcontextdict['name']==contextname:
        print("Found '"+contextname+"' in input file '"+contextdefinitionfilename+"'")
        if inputcontextdict['id']==id:
            print("The compute context id '"+id+"' in the input file matches the one in the SAS Viya deployment.")
        else:
            raise Exception("Input JSON file does define a context named '"+contextname+"', but the context ID does not match.")
    else:
        raise Exception("Input JSON file does not appear to define context named '"+contextname+"'. It defines a context named '"+inputcontextdict['name']+"'.")
else:
    # Handle the error! Compute context not found...
    raise Exception('Compute context name not found in input file - check it contains a JSON definition of a compute context.')

if id!=None:

    # Get the details of this compute context
    reqtype="get"
    reqval="/compute/contexts/"+id
    # reqaccept="application/vnd.sas.compute.context.summary+json"
    # reccontent="application/vnd.sas.collection+json"
    resultdata,etag=callrestapi(reqval,reqtype,returnEtag=True)
    #print("etag: "+etag)

    # Update compute contexts
    # Instead of passing in a (modified) resultdata dict, substitute that for the inputcontextdict
    # See http://swagger.na.sas.com/swagger-ui/?url=/apis/compute/v10/openapi-all.json#/Contexts/updateContext
    ##########################################################################
    # Updates a context definition. Changing a context does not affect any
    # sessions that are currently running on the server that is instantiated
    # by that context. Servers that are created after updating the context
    # use the current definition. If the contextId matches the ID of an
    # existing context, that context is updated. Otherwise, an error is
    # returned. The request must include the current ETag of the context as
    # the value of the If-Match request header to prevent concurrent updates.
    # The current ETag of the context is provided in the value of the ETag
    # response header of any endpoint that produces
    # application/vnd.sas.compute.context.
    ##########################################################################
    reqtype="put"
    reqval="/compute/contexts/"+id
    reqaccept="application/vnd.sas.compute.context+json"
    reccontent="application/vnd.sas.compute.context+json"
    resultdata_after_update=callrestapi(reqval,reqtype,reqaccept,reccontent,data=inputcontextdict,stoponerror=False,etagIn=etag)
    json_formatted_str = json.dumps(resultdata_after_update, indent=2)
    # Uncomment this to see the final resulting context JSON after it is updated
    #print(json_formatted_str)
    print("Context updated.")

sys.exit()
