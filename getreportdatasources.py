#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getreportdatasources.py
# Jul 2026
# Developed on SAS Viya Version: 2026.03
#
# this tool will print data source information for a provided VA report.
#
# The purpose of the tool is to help with VA report management.
#
# example
#
# getreportdatasources.py -p "/Products/SAS Visual Analytics/Samples/Warranty Analysis" -o csv
#
# 
# Change History
#
# 30may2026 initial coding
#
# Copyright Ã‚Â© 2025, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# Import Python modules
import re
import argparse, sys, subprocess, os, glob, ast
from sharedfunctions import callrestapi, printresult, getapplicationproperties,getclicommand,getbaseurl,getpath,getfolderid
import json


# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="List a Visual Analytics report's datasources")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-r", "--reportId", help="ID of the report to export")
group.add_argument("-p", "--reportPath", help="The full path to the report")
parser.add_argument("-o", "--output", default="simple", choices=["simple", "simplejson", "csv"], help="The type of output to receive (default: simple)")
parser.add_argument("-i", "--info", action="store_true", default=False, help="Print report info to console")
 
args = parser.parse_args()
 
output = args.output
info = args.info
 
# Initialize variables
folder_path = None
report_name = None
reporturi = None

# Get the report ID and folder path based on the provided input
if args.reportId:
    reporturi = args.reportId
    report_id = reporturi.split("/")[-1]

    # Ensure report exists for id specified
    checkRepExistance = f'/reports/reports?filter=eq(id,"{report_id}")'

    checkRepExistanceRep = callrestapi(checkRepExistance, "get")
    if checkRepExistanceRep["count"] == 0:
        print(f"Report with ID {reporturi} does not exist.")
        sys.exit(1)
    
    # get full path of this report as well as its containing folder
    fullPath = getpath(reporturi)
    folderId = getfolderid(fullPath)
    getRepInfo = callrestapi(reporturi, "get")

    report_name = getRepInfo["name"]
    folder_path = fullPath

elif args.reportPath:
    reportPath = args.reportPath
    report_name = reportPath.split("/")[-1]
    folder_path = reportPath.rsplit("/", 1)[0]
    folderId = getfolderid(folder_path)
    reqval = f"/folders/folders/{folderId[0]}/members?filter=eq(name,'{report_name}')"

    getRepInfo = callrestapi(reqval, "get")
 
    # check for report existence at this path
    if getRepInfo["count"]>0:
        reporturi = getRepInfo["items"][0]["uri"]
        if info:
            print("Report ID: "+getRepInfo["items"][0]["id"])
    else:
        print(f"Report '{reportPath}' Not found")
        sys.exit(1)

# print info if running verbose
if info:
    print(f"Report Name: {report_name}")
    print(f"Report Path: {folder_path}")
    print(f"Report ID: {reporturi}")

# retrieve data sources for this reporturi
reqtype='get'
reqval= reporturi+'/content'

resultdata=callrestapi(reqval,reqtype,acceptType="application/vnd.sas.report.content+json")

# Extract all casResource items from dataSources
if 'dataSources' in resultdata:
    all_datasources = []
    total_items = len(resultdata['dataSources'])
    if info:
        print(f"Total datasources found: {total_items}")

    if info and total_items == 0:
        print("Note: No items returned.")
    else:
        for source in resultdata['dataSources']:
            if 'casResource' in source:
                cas_resource = source['casResource']
                # Construct the cas resource path
                server = cas_resource.get('server')
                library = cas_resource.get('library')
                table = cas_resource.get('table')
                cas_path = f"cas~fs~{server}~fs~{library}/tables/{table}"
                
                # Make API call to get table state and source table name
                reqtype = 'get'
                reqval = '/casManagement/dataSources/' + cas_path

                resultdataTBL = callrestapi(reqval, reqtype)
                
                table_state = resultdataTBL['attributes']['state']
                source_table_name = resultdataTBL['attributes']['sourceTableName']
                
                # update object with relevant fields for printresult
                all_datasources.append({
                    "report_name": report_name,
                    "folder_path": folder_path,
                    "report_uri": reporturi,
                    "server": server,
                    "library": library,
                    "table": table,
                    "cas_path": cas_path,
                    "table_state": table_state,
                    "source_table_name": source_table_name
                })

        # After the loop, create datasource_object with all items
        datasource_object = {
            "count": len(all_datasources),
            "items": all_datasources
        }

        # Define the columns you want to display
        cols = ['report_name', 'folder_path', 'report_uri', 'server', 'library', 'table', 'table_state', 'source_table_name']
        # Use printresult to display it
        printresult(datasource_object, output, cols)
