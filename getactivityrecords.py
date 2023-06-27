#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getactivityrecords.py June 2023
#
# Extract list of activity records from SAS Infrastructure Data Server using REST API.
#
# Examples:
#
# 1. Return list of all activity records 
#        ./getactivityrecords.py
#
# Change History
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

# Import Python modules
import argparse
from sharedfunctions import callrestapi, getbaseurl, printresult

# Parse arguments based on parameters that are passed in on the command line
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--limit", help="Maximum number of records to display", default='1000')
parser.add_argument("-t", "--type", help="Filter by entry Type", default=None)
parser.add_argument("-a", "--application", help="Filter by entry Application", default=None)
parser.add_argument("-c", "--action", help="Filter by entry Action", default=None)
parser.add_argument("-d", "--admin-action", help="Filter by Administrative Action", default=None)
parser.add_argument("-s", "--state", help="Filter by entry State", default=None)
parser.add_argument("-u", "--user", help="Filter by Username", default=None)
parser.add_argument("-A", "--after", help="Filter entries that are created after the specified timestamp. For example: 2020-01-03 or 2020-01-03T18:15Z", default=None)
parser.add_argument("-B", "--before", help="Filter entries that are created before the specified timestamp. For example: 2020-01-03 or 2020-01-03T18:15Z", default=None)
parser.add_argument("-S", "--sortby", help="Sort the output ascending by this field", default='timeStamp')
parser.add_argument("-o", "--output", help="Output Style", choices=['csv', 'json', 'simple', 'simplejson'], default='csv')

args = parser.parse_args()
appname = args.application
username = args.user
entry_type = args.type
entry_state = args.state
entry_action = args.action
admin_action = args.admin_action
ts_after = args.after
ts_before = args.before
sort_order = args.sortby
output_limit = args.limit
output_style = args.output

# Create a dictionary for filter conditions
filter_conditions = {
    'application': appname,
    'user': username,
    'type': entry_type,
    'state': entry_state,
    'action': entry_action,
    'admin_action': admin_action,
    'ts_after': ts_after,
    'ts_before': ts_before
}

# Remove None values from filter_conditions dictionary
filter_conditions = {key: value for key, value in filter_conditions.items() if value is not None}

# Construct the filter string
filter_str = '&'.join("eq({},{})".format(key, value) for key, value in filter_conditions.items())

# Construct the request URL
reqval = "/audit/activities"
reqval += "?limit={}&sortBy={}".format(output_limit, sort_order)
if filter_str:
    reqval += "&filter=" + filter_str

# Construct and print the endpoint URL
baseurl = getbaseurl()
endpoint = baseurl + reqval
#print("REST endpoint:", endpoint)

# Make the REST API call and process & print results
files_result_json = callrestapi(reqval, 'get')
cols = ['id', 'type', 'action', 'administrativeAction', 'state', 'user', 'application', 'timeStamp', 'remoteAddress']
printresult(files_result_json, output_style, cols)
