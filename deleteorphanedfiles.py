#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# deleteorphanedfiles.py September 2024
#
# Tool to delete orphaned job files (Files whose parentUri references an undefined object)
#
#
# Change History
#
# 27SEP2024 Initial commit
#
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
# the --output parameter is a common one which supports the three styles of output json, simple or csv

parser = argparse.ArgumentParser() 
parser.add_argument("-f","--filter", help="Set a custom filter for objects, for example eq(createdBy,sasdemo).")
parser.add_argument("-w","--write", help="Make the specified changes.",action="store_true",default=False)
parser.add_argument("-l","--limit", type=int,help="Specify the number of records to pull in each REST API call. Default is 10.",default=10)
parser.add_argument("-p","--pagelimit", type=int,help="Specify the number of pages to pull before stopping. Default is 10.",default=10)
args = parser.parse_args()
filter=args.filter
write=args.write
limit=args.limit
pagelimit=args.pagelimit

# If no filter is set, we should still filter on objects that have a parentUri defined.
if filter is None:
    # Set the filter to not(isNull(parentUri))
    filter = 'not(isNull(parentUri))'
else:
    # If the filter is defined, add not(isNull(parentUri)) to the defined filter.
    filter = 'and(%s,not(isNull(parentUri)))' % (filter)

# Set the request type
reqtype='get'

# Set the endpoint to call
reqval='/files/files?&filter='+filter+'&limit='+str(limit)
print('Calling REST endpoint:',reqval)
# Make the rest call using the callrestapi function.
results=callrestapi(reqval,reqtype)

count=results['count']
print('Found',count,'matching our query.')

# Write the IDs we found to an array
ids = []
for item in results.get("items",[]):
    ids.append(item.get("id"))

# We need to tolerate paged output.
next_link = None
pages = 1

for link in results.get("links",[]):
    if link.get("rel") == "next":
        next_link = link.get("href")
        break

while pages < pagelimit and next_link is not None:
    
    pages += 1

    print('Calling REST endpoint from the "next" link:',next_link)
    # Call the next link
    results=callrestapi(next_link,reqtype)

    # Pull the ids into the array
    for item in results.get("items",[]):
        ids.append(item.get("id"))
    
    # Check for a next link again.
    next_link = None
    for link in results.get("links",[]):
        if link.get("rel") == "next":
            next_link = link.get("href")
            break
print('Pages traversed:',pages)
print('Found ids:',len(ids))

if len(ids) != count:
    print('WARN: Captured IDs does not match total count:',count,'Increase page or limit settings to capture all results.')
# We now have an array "ids" of each ID matching our supplied filter.

# Iterate through the IDs
for id in ids:
    reqtype = 'get'
    reqval = '/files/files/'+id
    
    # Pull the file details
    file = callrestapi(reqval,reqtype)
    # Get the parentUri
    parenturi = file.get("parentUri")
    # Check if the parentUri exists
    reqtype = 'head'
    results = None
    httpcode = None
    results,httpcode = callrestapi(parenturi,reqtype)

    # If it does not exist, delete the file object.
    if (httpcode == 404):
        print("Found orphaned file:",id,"with non-existent parentUri:",parenturi)
        if write:
            print("Deleting file...")
            results = None
            reqtype = 'delete'
            results = callrestapi(reqval,reqtype)
    elif (httpcode == 200):
        print("File:",id,"has existing parentUri:",parenturi)
    else:
        print("File:",id,"parentUri:",parenturi,"returned unexpected return code:",httpcode)    