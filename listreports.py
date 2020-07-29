#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listtreports.py
# June 2020
#
# this tool will list all the reports in your viya system
#
# Change History
#
# Copyright Â© 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse, sys, subprocess, uuid, time, os, glob
from datetime import datetime as dt, timedelta as td
from sharedfunctions import getfolderid, callrestapi, getpath

# get python version
version=int(str(sys.version_info[0]))

# CHANGE THIS VARIABLE IF YOUR CLI IS IN A DIFFERENT LOCATION
clidir='/opt/sas/viya/home/bin/'

# get input parameters
parser = argparse.ArgumentParser(description="List Viya Reports")
parser.add_argument("-n","--name", help="Name contains?",default=None)
parser.add_argument("-f","--folderpath", help="Folder Path starts with?",default="/")

args= parser.parse_args()
basedir=args.directory
quietmode=args.quiet

nameval=args.name
folderpath=args.folderpath


# create a list for filter conditions
filtercond=[]

# there is always a number of days, the default is zero

if nameval!=None: filtercond.append('contains($primary,name,"'+nameval+'")')

# add the start and end and comma delimit the filter
delimiter = ','
completefilter = 'and('+delimiter.join(filtercond)+')'

# retrieve all reports in the system
reqtype='get'
reqval='/reports/reports?filter='+completefilter+'&limit=10000'

resultdata=callrestapi(reqval,reqtype)

# loop root reports
if 'items' in resultdata:

	total_items=resultdata['count']

	returned_items=len(resultdata['items'])

	if total_items == 0: print("Note: No items returned.")
	else:
		# export each folder and download the package file to the directory

		for i in range(0,returned_items):

			id=resultdata['items'][i]["id"]

			path_to_report=getpath("/reports/reports/"+id)

			if path_to_report.startswith(folderpath):

				path_to_report=path_to_report.replace("/","_")

				print(path_to_report)
				print(resultdata)

else:
	 print("NOTE: Operation cancelled.")

