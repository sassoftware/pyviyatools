#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# snapshotreports.py
# April 2019
#
# this tool will export all the reports in your viya system to there own
# individual json file in a directory.
#
# The purpose of the tools is to be able to have a granular backup of reports
# so that you could restore an individual report to a system. Something that
# is not currently supported by Viya backup or promotion
#
# example
#
# save each to their own package all reports that have changed in the last 10 days
# snapshotreports.py -c 10 -d ~/snapshot
#
# Change History
#
# 16may2020 add folder path to report name
# 16may2020 allow to subset reports exported by the path of the report folder
# 10aug2020 add option to auto delete transport file after download completes
#
# Copyright Ã‚Â© 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse, sys, subprocess, uuid, time, os, glob
from datetime import datetime as dt, timedelta as td
from sharedfunctions import getfolderid, callrestapi, getpath, get_valid_filename

# get python version
version=int(str(sys.version_info[0]))

# CHANGE THIS VARIABLE IF YOUR CLI IS IN A DIFFERENT LOCATION
clidir='/opt/sas/viya/home/bin/'

# get input parameters
parser = argparse.ArgumentParser(description="Export Viya Reports each to its own unique transfer package")
parser.add_argument("-d","--directory", help="Directory to store report packages",required='True')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
parser.add_argument("-c","--changeddays", help="Reports changed in the how many days (defaults to 1 day)?",default='1')
parser.add_argument("-m","--modifiedby", help="Last modified id equals?",default=None)
parser.add_argument("-n","--name", help="Name contains?",default=None)
parser.add_argument("-f","--folderpath", help="Folder Path starts with?",default="/")
parser.add_argument("-t","--tranferremove", help="Remove transfer file after download?", action='store_true')

args= parser.parse_args()
basedir=args.directory
quietmode=args.quiet
autotranferremove=args.tranferremove

changeddays=args.changeddays
modby=args.modifiedby
nameval=args.name
folderpath=args.folderpath

# calculate time period for files
now=dt.today()-td(days=int(changeddays))
subset_date=now.strftime("%Y-%m-%dT%H:%M:%S")
datefilter="ge(modifiedTimeStamp,"+subset_date+")"

# create a list for filter conditions
filtercond=[]

# there is always a number of days, the default is zero
filtercond.append(datefilter)

if nameval!=None: filtercond.append('contains($primary,name,"'+nameval+'")')
if modby!=None: filtercond.append("eq(modifiedBy,"+modby+")")

# add the start and end and comma delimit the filter
delimiter = ','
completefilter = 'and('+delimiter.join(filtercond)+')'

# prompt if directory exists because existing json files are deleted
if os.path.exists(basedir):

	# if the quiet mode flag is not passed then prompt to continue
	if not quietmode:

		if version  > 2:
			areyousure=input("The folder exists any existing json files in it will be deleted. Continue? (Y)")
		else:
			areyousure=raw_input("The folder already exists any existing json files in it will be deleted. Continue? (Y)")
	else:
		areyousure="Y"

else: areyousure="Y"

# prompt is Y if user selected Y, its a new directory, or user selected quiet mode
if areyousure.upper() =='Y':

	path=basedir

	# create directory if it doesn't exist
	if not os.path.exists(path): os.makedirs(path)
	else:
		filelist=glob.glob(path+"/*.json")
		for file in filelist:
			os.remove(file)

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

			reports_exported=0

			for i in range(0,returned_items):

				id=resultdata['items'][i]["id"]

				path_to_report=getpath("/reports/reports/"+id)

				if path_to_report.startswith(folderpath):

					reports_exported=reports_exported+1

					path_to_report=path_to_report.replace("/","_")

					package_name=str(uuid.uuid1())

					json_name=get_valid_filename(path_to_report+resultdata['items'][i]["name"].replace(" ","")+'_'+str(i))

					command=clidir+'sas-admin transfer export -u /reports/reports/'+id+' --name "'+package_name+'"'
					print(command)
					subprocess.call(command, shell=True)

					reqval='/transfer/packages?filter=eq(name,"'+package_name+'")'
					package_info=callrestapi(reqval,reqtype)

					package_id=package_info['items'][0]['id']

					completefile=os.path.join(path,json_name+'.json')
					command=clidir+'sas-admin transfer download --file '+completefile+' --id '+package_id
					print(command)
					subprocess.call(command, shell=True)
					#time.sleep(1)
					if autotranferremove:
						print(clidir+'sas-admin transfer delete --id '+package_id+"\n")
						remTransferObject = subprocess.Popen(clidir+'sas-admin transfer delete --id '+package_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
						remTransferObjectOutput = remTransferObject.communicate(b'Y\n')
						remTransferObject.wait()


					print("NOTE: "+str(reports_exported)+" report(s) exported to json files in "+path)
			print("NOTE: "+str(total_items)+" total reports found, "+str(reports_exported)+" reports exported to json files in "+path)


else:
	 print("NOTE: Operation cancelled")
