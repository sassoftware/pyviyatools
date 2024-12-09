#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getimportresults.py November 2024
#
# Tool to get detailed results from import history
#
#
# Change History
#
# 27NOV2024 Initial commit
#
#
# Copyright © 2024, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

parser = argparse.ArgumentParser() 
parser.add_argument("-i","--id", help="Specify the package ID being imported.")
parser.add_argument("-f","--filter", help="Set a custom filter for objects, for example eq(createdBy,sasdemo).")
parser.add_argument("-l","--limit", type=int,help="Specify the number of records to pull in each REST API call. Default is 10.",default=10)
parser.add_argument("-p","--pagelimit", type=int,help="Specify the number of pages to pull before stopping. Default is 10.",default=10)
args = parser.parse_args()
packageid=args.id
filter=args.filter
limit=args.limit
pagelimit=args.pagelimit

# Build our filter:
if filter is None:
    if packageid is None:
        reqval = '/transfer/importJobs?limit='+str(limit)
    else:
        filter = 'eq(packageUri,"/transfer/packages/%s")' % (packageid)
        reqval = '/transfer/importJobs?filter='+filter+'&limit='+str(limit)
else:
    if packageid is not None:
        filter = 'and(%s,eq(packageUri,"/transfer/packages/%s"))' % (filter,packageid)
        reqval = '/transfer/importJobs?filter='+filter+'&limit='+str(limit)

# Step 1: Get the import jobs
reqtype = 'get'
print('Calling REST endpoint:',reqval)

# Make the rest call using the callrestapi function.
results=callrestapi(reqval,reqtype)

count=results['count']
print('Found',count,'matching our query.')

# Step 2: Pull each importJob ID into an array
ids = []
for item in results.get("items",[]):
    ids.append(item.get("id"))

# Step 3: If we have mulitple pages, traverse them.
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
        ids.append(item.get("id"))
    
    # Check for a next link again.
    next_link = None
    for link in results.get("links",[]):
        if link.get("rel") == "next":
            next_link = link.get("href")
            break
print('Pages traversed:',pages)
print('Captured ids:',len(ids))
if len(ids) != count:
    print('WARN: Captured IDs does not match total count:',count,'Increase page or limit settings to capture all results.')

# We now have an array "ids" of all the importJob ids we need to process.

# Step 4: Iterate through the Ids to display the import job details and the results of each task

# Create an array we can use for a table of results
data = [["Task Name","Resource Type","State","Message"]]

for id in ids:
    # Get the details of the import job
    reqtype = 'get'
    reqval = '/transfer/importJobs/'+id
    results=callrestapi(reqval,reqtype)
    print()
    print("------------------------------------")
    print("Import Job ID: ",results.get("id"))
    print("Import Job Name: ",results.get("name"))
    print("Import Job State: ",results.get("state"))
    # Get the details on the individual tasks
    reqval = '/transfer/importJobs/'+id+'/tasks'
    results=callrestapi(reqval,reqtype)
    # Each tasks results are in the items array response here.
    print()
    for task in results.get("items",[]):
        name = task.get("name")
        rtype = task.get("resourceType")
        state = task.get("state")
        message = task.get("message")
    data.append([name,rtype,state,message])

    # Define a length for each column
    column_length = [0,0,0,0]

    # Update the length based on the maximum length for each column.
    for row in data:
        for i in range(4):
            if len(row[i])+2 > column_length[i]:
                column_length[i] = len(row[i])+2

    # Print each row using our max column length values to make a readable table.
    for row in data:
        formatted_row="".join("%-*s" % (width,value) for value, width in zip(row, column_length))

        print(formatted_row)