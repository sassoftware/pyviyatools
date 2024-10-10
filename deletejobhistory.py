#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# jobdelete.py September 2024
#
# Tool to delete jobExecution jobs (execution history displayed in the "Monitoring" tab of the Jobs and Flows page in Env Mgr) 
# without an expiration timestamp set, or that match a given filter.
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
parser.add_argument("-e","--empty", help="Filter on objects without an expiration set.",action="store_true",default=False)
parser.add_argument("-f","--filter", help="Set a custom filter for objects, for example eq(createdBy,sasdemo).")
parser.add_argument("-w","--write", help="Make the specified changes.",action="store_true",default=False)
parser.add_argument("-l","--limit", type=int,help="Specify the number of records to pull in each REST API call. Default is 10.",default=10)
parser.add_argument("-p","--pagelimit", type=int,help="Specify the number of pages to pull before stopping. Default is 10.",default=10)
args = parser.parse_args()
empty=args.empty
filter=args.filter
write=args.write
limit=args.limit
pagelimit=args.pagelimit

# If empty is set and filter is not, the filter will just be empty durations
if empty:
    if filter is None:
        # Set the filter to isNull(expirationTimeStamp)
        filter = 'isNull(expirationTimeStamp)'
    else:
        # If the filter is defined and empty is set, add isNull(expirationTimeStamp) to the defined filter.
        filter = 'and(%s,isNull(expirationTimeStamp))' % (filter)

# Set the request type
reqtype='get'

# Set the endpoint to call
if filter is None:
    reqval='/jobExecution/jobs?&limit='+str(limit)
else:
    reqval='/jobExecution/jobs?&filter='+filter+'&limit='+str(limit)
print('Calling REST endpoint:',reqval)
# Make the rest call using the callrestapi function.
results=callrestapi(reqval,reqtype)

count=results['count']
print('Found',count,'matching our query.')

print('Job ID','\t','Created','\t','Expiration',"\t",'Job Name')
# Write the IDs we found to an array
ids = []
for item in results.get("items",[]):
    print(item.get("id"),"\t",item.get("creationTimeStamp"),"\t",item.get("expirationTimeStamp"),"\t",item['jobRequest'].get("name"))
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

    print('Calling REST endpoint:',next_link)
    # Call the next link
    results=callrestapi(next_link,reqtype)
    
    # Pull the ids into the array
    for item in results.get("items",[]):
        print(item.get("id"),"\t",item.get("creationTimeStamp"),"\t",item.get("expirationTimeStamp"),"\t",item['jobRequest'].get("name"))
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

# If write is turned on, iterate through the IDs
if write:
    for id in ids:
        reqtype = 'delete'
        reqval = '/jobExecution/jobs/'+id
        print("Deleting Job ID:",id)
        # Delete the ID
        results = callrestapi(reqval,reqtype)