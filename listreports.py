#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listtreports.py
# June 2020
#
# this tool will list all the reports in your viya system. It will show
# the full path to the report
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
from sharedfunctions import getfolderid, callrestapi, getpath, printresult, getapplicationproperties

# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="List Viya Reports and their folder path.")
parser.add_argument("-n","--name", help="Name contains?",default=None)
parser.add_argument("-f","--folderpath", help="Folder Path starts with?",default="/")
parser.add_argument("-c","--changeddays", help="Reports changed in the how many days (defaults to 5 years)?",default='1825')
parser.add_argument("-m","--modifiedby", help="Last modified id equals?",default=None)
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple'],default='csv')

args= parser.parse_args()
nameval=args.name
folderpath=args.folderpath
changeddays=args.changeddays
modby=args.modifiedby
output_style=args.output

# calculate time period for files
now=dt.today()-td(days=int(changeddays))
subset_date=now.strftime("%Y-%m-%dT%H:%M:%S")
datefilter="ge(modifiedTimeStamp,"+subset_date+")"

# create a list for filter conditions
filtercond=[]

# there is always a number of days, the default is 1825
filtercond.append(datefilter)
if modby!=None: filtercond.append("eq(modifiedBy,'"+modby+"')")


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

	itemlist=resultdata['items']
	returned_items=len(itemlist)

	if total_items == 0: print("Note: No items returned.")
	else:
		# get the path for each report and add it to the result set
		# this is not very efficient. I will try to improve it

		for i in range(0,returned_items):

			id=itemlist[i]["id"]
			name=itemlist[i]["name"]
			path_to_report=getpath("/reports/reports/"+id)

			# add the path as an attribute of flag for delete
			if path_to_report.startswith(folderpath): itemlist[i]["fullreport"]=path_to_report+name
			else: itemlist[i]["fullreport"]='delete'

     	# remove non matches before printing
		newlist = [i for i in itemlist if not (i['fullreport'] == 'delete')]
		resultdata['items']=newlist
		resultdata['count']=len(newlist)

		printresult(resultdata,output_style,colsforcsv=["id","fullreport","type","description","creationTimeStamp","modifiedTimeStamp"])

