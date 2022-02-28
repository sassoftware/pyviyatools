#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getcomputecontextattributes.py
# February 2022
#
# Print compute context attributes.
#
#
# Change History
#
# Copyright © 2022, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
#  OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
#
# Import Python modules
import argparse, sys, os, json
from sharedfunctions import callrestapi

debug=False

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print (exception_type.__name__, exception)

sys.excepthook = exception_handler

# get input parameters
parser = argparse.ArgumentParser(description="List attributes in an existing compute context. If you want to add, remove or update a compute context, use setcomputecontextattributes.py.")
parser.add_argument("-n","--name", help="Compute context name",required='True')
args= parser.parse_args()
contextname=args.name

# get python version
#version=int(str(sys.version_info[0]))
#print("Python version: " + str(version))

# Get compute contexts
reqtype="get"
reqval="/compute/contexts/?filter=eq(name, '"+contextname+"')"
resultdata=callrestapi(reqval,reqtype)
#json_formatted_str = json.dumps(resultdata, indent=2)
#print(json_formatted_str)


if 'items' in resultdata:
    #print(resultdata['items'])
    if resultdata['items']==[]:
        id=None
        raise Exception("Compute context '"+contextname+"' not found.")
    elif len(resultdata['items'])>1:
        id=None
        raise Exception("More than one matching compute context named '"+contextname+"'.!")
    # If we make it this far, we found exactly one compute context
    for i in resultdata['items']:
        id=i['id']
        #print("Compute context: "+contextname+" ["+id+"]")
else:
    id=None
    # Handle the error! Compute context not found...
    raise Exception('Compute context not found.')

if id!=None:

    # Get the details of this compute context
    reqtype="get"
    reqval="/compute/contexts/"+id
    resultdata,etag=callrestapi(reqval,reqtype,returnEtag=True)
    #print("etag: "+etag)
    # Get rid of parts of the context we don't need
    resultdata.pop("links",None)
    resultdata.pop("creationTimeStamp",None)
    resultdata.pop("modifiedTimeStamp",None)
    resultdata.pop("version",None)
    #json_formatted_str = json.dumps(resultdata, indent=2)
    #print(json_formatted_str)

    boolFoundAttribute=False
    if 'attributes' in resultdata:
        # numattributes=len(resultdata['attributes'])
        # print('numattributes='+str(numattributes))
        # print(resultdata['attributes'])
        # print(type(resultdata['attributes']))

        for attributeKey, attributeValue in resultdata['attributes'].items():
            print("Attribute: "+attributeKey+" : "+attributeValue)
    else:
        # No attributes section in results data at all
        print("Compute context '"+contextname+"' has no attributes")

sys.exit()
