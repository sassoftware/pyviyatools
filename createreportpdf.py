#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# createreportpdf.py
# Jan 2025
# Developed on SAS Viya Version: 2024.12
#
# this tool will generate a pdf of a visual analytics report and save it to 
# the requested viya content folder
#
# The purpose of the tool is to be able programatically archive a report in pdf format
#
# example
#
# export the visual analytcs report 12345678-1234-1234-1234-123456789abc to the users "My Folder" as
# vaReportArchive.pdf
#
# createreportpdf.py -r 12345678-1234-1234-1234-123456789abc -n vaReportArchive
#
# Change History
#
# 14jan2025 initial coding
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
import argparse, sys, subprocess, os, glob, json
from sharedfunctions import callrestapi, getapplicationproperties,getclicommand

# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="Generate a pdf from a Visual Analytics Report")
parser.add_argument("-r","--reportId", help="ID of the report to export",required='True')
parser.add_argument("-f","--folderid", help="Enter the viya folder id for the output to be placed in.",default="@myFolder")
parser.add_argument("-n","--filename", help="Name the path of the Viya Folder.",required='True')
parser.add_argument("-c", "--nameConflict", help="The strategy for handling name collision when saving the result file: replace or rename", choices=['replace', 'rename'], default='replace')
parser.add_argument("-w","--wait", type=int,help="Specify the number of seconds to wait for the job to complete. Default is 30.",default=30)
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')

# pare args
args= parser.parse_args()
reporturi=args.reportId
resultfolderid=args.folderid
outputfilename=args.filename
nameConflictChoice=args.nameConflict
quietmode=args.quiet
waitseconds=args.wait

# if the quiet mode flag is not passed then prompt to continue
if not quietmode and nameConflictChoice == 'replace':

	if version  > 2:
		areyousure=input("If the file: " +outputfilename+ ".pdf exists in the requested viya folder, will be overwritten. Continue? (Y)")
	else:
		areyousure=raw_input("If the file: " +outputfilename+ ".pdf exists in the requested viya folder, will be overwritten. Continue? (Y)")
else:
	areyousure="Y"

if areyousure.upper() =='Y':

	# Delcare request type
	reqtype='post'
	# Generate payload
	data= {
	"resultFolder": resultfolderid,
	"resultFilename": outputfilename,
	"nameConflict": nameConflictChoice,
	"options": {},
	"timeout": 60,
	"wait": waitseconds
	}

	# Make request and process results
	reqvalImg='/visualAnalytics/reports/'+reporturi+'/exportPdf'
	resultdata=callrestapi(reqvalImg,reqtype,data=data,acceptType='application/json')
	resultstate = resultdata.get("state")
	resultjob=resultdata.get("links")[0]['uri']
	if resultstate == "running": 
		print("Warning: The job is taking longer than the requested wait time.  Access the following URI for job details: ")
	elif resultstate == "failed": 
		print("Error: The job state is failed.  Access the following URI for job details: ")
	else:
		print("Job Completed.  Access the following URI for job details: ")
	print(resultjob)

else:
	 print("NOTE: Operation cancelled")
