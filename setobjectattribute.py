#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setobjectattribute.py January 2025
#
# Tool to update an attribute on a given object (e.g. change name, add description)
#
#
# Change History
#
# 15JAN2025 Initial commit
#
#
# Copyright © 2025, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either 
#  express or implied. See the License for the specific language governing permissions and limitations under the License.
# 

import argparse 
from sharedfunctions import callrestapi

# setup command-line arguements. In this block which is common to all the tools you setup what parameters
# are passed to the tool

parser = argparse.ArgumentParser() 
parser.add_argument("-u","--uri", help="Specify the URI to update.",required=True)
parser.add_argument("-a","--attribute", help="Specify the attribute to update.",required=True)
parser.add_argument("-v","--value", help="Specify the new value of the attribute.",required=True)
args = parser.parse_args()
uri=args.uri
attribute=args.attribute
value=args.value

# Check if the object exists
reqtype = 'head'
results = None
httpCode = None
results,httpcode = callrestapi(uri,reqtype)
print('Checking if URI',uri,'exists.')
if ( httpcode == 200 ):
    print('URI:',uri, 'exists.')

    # Define request to pull current object json
    reqtype = 'get'
    reqval = uri
    print("Pulling Object Details:",uri)

    # Pull the current object json, also capture the Etag to include in the If-Match header for the update.
    object,etag = callrestapi(reqval,reqtype,returnEtag=True)

    # Check if the URI supports a PUT update. 
    links = object['links']
    for link in links:
        if link.get('rel') == 'update':
            method = link.get('method')
            if method == 'PUT':
                print('URI:',uri,'supports a PUT update. Continuing...')

                # Remove unneeded keys
                delkeys = ['links','creationTimeStamp','modifiedTimeStamp','createdBy','modifiedBy','version']
                for key in delkeys:
                    object.pop(key, None)

                # Add updated key
                object[attribute] = value

                # Update the jobRequest object
                reqtype = 'put'
                results = callrestapi(reqval,reqtype,etagIn=etag,data=object)
            else:
                print('URI:',uri,'does not support update using PUT. Method:',method)
else:
    print('URI:',uri,'does not appear to exist. HTTP response:',httpcode)