#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getschedulehistory.py October 2024
#
# Tool to pull most recent job history for each scheduler job
#
#
# Change History
#
# 29OCT2024 Initial commit
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
parser.add_argument("-l","--limit", type=int,help="Specify the number of records to pull in each REST API call. Default is 10.",default=10)
parser.add_argument("-p","--pagelimit", type=int,help="Specify the number of pages to pull before stopping. Default is 10.",default=10)
args = parser.parse_args()
filter=args.filter
limit=args.limit
pagelimit=args.pagelimit

# Set the request type
reqtype='get'

# Set the endpoint to call
if filter is None:
    reqval='/scheduler/jobs?limit='+str(limit)
else:
    reqval='/scheduler/jobs?&filter='+filter+'&limit='+str(limit)

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

# Print a header of detail we want to return
#print('Job Name','\t','Job Fired','\t','Job Status','\t','Response Code')

data = [["Job Name","Job Fired", "Job Status", "Response Code"]]

# Iterate through the IDs, only pulling one element
for id in ids:
    reqtype = 'get'
    reqval = '/scheduler/jobs/'+id
    job = callrestapi(reqval,reqtype)
    jobname = job.get("name")

    # Reset the history details in case there is no history
    jobfire = ""
    jobstatus = ""
    statuscode = ""

    reqval = '/scheduler/jobs/'+id+'/history?limit=1&sortBy=jobFireTimeStamp:descending'
    
    # Pull the history details
    print('NOTE: Pulling history for job '+jobname)
    history = callrestapi(reqval,reqtype)
    for item in history.get("items",[]):
        jobfire = item.get("jobFireTimeStamp")
        jobstatus = item.get("jobStatus")
        statuscode = item.get("httpStatusCode")

    data.append([jobname,jobfire,jobstatus,statuscode])

# Define a length for each column
column_length = [0,0,0,15]

# Update the length based on the maximum length for each column.
for row in data:
    for i in range(3):
        if len(row[i])+2 > column_length[i]:
            column_length[i] = len(row[i])+2

# Print each row using our max column length values to make a readable table.
for row in data:
    formatted_row="".join("%-*s" % (width,value) for value, width in zip(row, column_length))

    print(formatted_row)