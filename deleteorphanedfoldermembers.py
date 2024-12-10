#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# deleteorphanedfoldermembers.py December 9 2024
#
# Tool to identify and remove folder members that no longer exist.
#
# Change History
#
# 09DEC2024 Initial commit
#
# Copyright © 2024, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#  express or implied. See the License for the specific language governing permissions and limitations under the License.

import argparse 
from sharedfunctions import callrestapi,getfolderid

parser = argparse.ArgumentParser() 
parser.add_argument("-f","--folder", help="Specify the folder to search for orphaned memberships.",required=True)
parser.add_argument("-d","--delete", help="Delete the members found.",action="store_true",default=False)
parser.add_argument("-l","--limit", type=int,help="Specify the number of records to pull in each REST API call. Default is 10.",default=10)
parser.add_argument("-p","--pagelimit", type=int,help="Specify the number of pages to pull before stopping. Default is 10.",default=10)
args = parser.parse_args()
folder=args.folder
write=args.delete
limit=args.limit
pagelimit=args.pagelimit

objectlimit=limit * pagelimit

if not folder.endswith('/'):
    folder=folder+'/'
print("Analyzing Folder:",folder)
fid = getfolderid(folder)
reqtype = 'get'
reqval = fid[1]+'/members?recursive=true&limit='+str(limit)
print('Calling REST endpoint: ',reqval)
results=callrestapi(reqval,reqtype)

count=results['count']
print('Found',count,'matching our query.')
if count > objectlimit:
    print("WARN: The configured page size (--limit) and maximum pages (--pagelimit) will only allow processing of",objectlimit,"objects of the total",count)
# Write the URIs to an array.
members = []
for item in results["items"]:
    if item["type"] == "child":
        uri = item["uri"]
        href = next((link["href"] for link in item["links"] if link["rel"] == "delete"), None)
        members.append([uri,href])

# Paged output handling
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

    for item in results["items"]:
        if item["type"] == "child":
            uri = item["uri"]
            href = next((link["href"] for link in item["links"] if link["rel"] == "delete"), None)
            members.append([uri,href])

    # Check for a next link again.
    next_link = None
    for link in results.get("links",[]):
        if link.get("rel") == "next":
            next_link = link.get("href")
            break
print('Pages traversed:',pages)
print('After filtering non-child objects, found members to check:',len(members))

# Iterate through the URIs to see if they exist

for member in members:
    reqtype = 'head'
    results = None
    results,httpcode = callrestapi(member[0],reqtype)
    # If it does not exist, delete the file object.
    if (httpcode == 404):
        print("WARN: Found orphaned member",member[0])
        if write:
            print("Delete option set, attempting to delete member.")
            results = None
            reqtype = 'delete'
            results = callrestapi(member[1],reqtype)
        else:
            print("Rerun with --delete to remove this object or call this URI with the DELETE HTTP method",member[1])
    elif (httpcode == 200):
        print("Member", member[0],"exists. HTTP response code:", httpcode)
    else:
        print("Member",member[0],"returned unexpected return code:", httpcode)   