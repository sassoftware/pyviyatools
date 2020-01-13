#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getauditrecords.py January 2020
#
# Extract list of audit records from SAS Infrastructure Data Server using REST API.
#
# Examples:
#
# 1. Return list of audit events from all users and applications 
#        ./getauditrecords.py
#
# Change History
#
# 10JAN2020 Comments added
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

# Import Python modules
import json
import socket
import argparse, sys
from sharedfunctions import callrestapi,getinputjson,simpleresults,getbaseurl,printresult

# Sample reqval="/audit/entries?filter=and(eq(application,'reports'),eq(state,'success'),ge(timeStamp,'2018-11-20'),le(timeStamp,'2020-11-20T23:59:59.999Z'))&sortBy=timeStamp&limit=1000"

# Parse arguments based on parameters that are passed in on the command line
parser = argparse.ArgumentParser()

parser.add_argument("-a","--application", help="Filter by Application or Service name",default=None)
parser.add_argument("-l","--limit", help="Maximum number of records to display",default='1000')
parser.add_argument("-t","--type", help="Filter by entry Type",default=None)
parser.add_argument("-c","--action", help="Filter by entry Action",default=None)
parser.add_argument("-s","--state", help="Filter by entry State",default=None)
parser.add_argument("-u","--user", help="Filter by Username",default=None)
parser.add_argument("-A","--after", help="Filter entries that are created after the specified timestamp. For example: 2020-01-03 or 2020-01-03T18:15Z",default=None)
parser.add_argument("-B","--before", help="Filter entries that are created before the specified timestamp. For example: 2020-01-03 or 2020-01-03T18:15Z",default=None)
parser.add_argument("-S","--sortby", help="Sort the output ascending by this field",default='timeStamp')
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple'],default='csv')

args = parser.parse_args()
appname=args.application
output_style=args.output
sort_order=args.sortby
output_limit=args.limit
username=args.user
entry_type=args.type
entry_action=args.action
entry_state=args.state
ts_after=args.after
ts_before=args.before


# Create list for filter conditions
filtercond=[]
if appname!=None: filtercond.append("eq(application,'"+appname+"')")
if username!=None: filtercond.append("eq(user,'"+username+"')")
if entry_type!=None: filtercond.append("eq(type,'"+entry_type+"')")
if entry_action!=None: filtercond.append("eq(action,'"+entry_action+"')")
if entry_state!=None: filtercond.append("eq(state,'"+entry_state+"')")
if ts_after!=None: filtercond.append("ge(timeStamp,'"+ts_after+"')")
if ts_before!=None: filtercond.append("le(timeStamp,'"+ts_before+"')")

# Construct filter 
delimiter = ','
completefilter  = 'and('+delimiter.join(filtercond)+')'

# Set request
reqtype = 'get'
reqval = "/audit/entries?filter="+completefilter+"&limit="+output_limit+"&sortBy="+sort_order

# Construct & print endpoint URL
baseurl=getbaseurl()
endpoint=baseurl+reqval
# print("REST endpoint: " +endpoint) 

# Make REST API call, and process & print results
files_result_json=callrestapi(reqval,reqtype)
cols=['id','timeStamp','type','action','state','user','remoteAddress','application','description','uri']
printresult(files_result_json,output_style,cols)
