#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# snapshotcontent.py
# Nov 2024
#
# MAy 2025 added changedays, consistent with snapshotreport.py
# IMPORTANT: this is a breaking change, the default is now 1 day
# returning content modified in the last 1 day 
# to get original beavhours behaviour use -c 25000
#
# this tool will export all the content in a specified folder to
# individual json file in a directory.
#
# Folders themselves are not exported but content in sub-folders is exported.
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
import argparse, sys, subprocess, uuid, time, os, glob, json
from datetime import datetime, timedelta
from sharedfunctions import getfolderid, callrestapi, getpath, getapplicationproperties, get_valid_filename, createdatefilter,getclicommand, getpath

# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="Export Viya content each piece of content to its own unique transfer package.")
parser.add_argument("-d","--directory", help="Directory to store report packages.",required='True')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
#parser.add_argument("-isf","--includesubfolder", help="Include Sub-folders of the main folder.", action='store_false')
parser.add_argument("-f","--folderpath", help="Folder Path starts with.",required='True')
parser.add_argument("-c","--changeddays", help="Content changed in the how many days (defaults to 1 day)?",default='1')
#parser.add_argument("--types", help="Content Type in.",default=None)
parser.add_argument("-t","--transferremove", help="Remove transfer file from Infrastructure Data Server after download.", action='store_true')
parser.add_argument("-l","--limit", type=int,help="Specify the number of records to pull. Default is 1000.",default=1000)

args= parser.parse_args()


basedir=args.directory
quietmode=args.quiet
autotranferremove=args.transferremove
folderpath=args.folderpath
limit=args.limit
days_delta=args.changeddays
#type=args.type
#includesubfolder=args.includesubfolder

try:
    days_delta = int(days_delta)
except ValueError:
    print("ERROR: changeddays must be an integer.")
    sys.exit(1)

today = datetime.now().date()
modifiedafter_dt = datetime.combine(today - timedelta(days=days_delta), datetime.min.time())

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

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

	folderresult=getfolderid(folderpath)
	if folderresult[0] is not None:
		folderid=folderresult[0]
		folderuri=folderresult[1]

	else:
		print("ERROR: could not locate folder")
		sys.exit()

	# create directory if it doesn't exist
	if not os.path.exists(path): os.makedirs(path)
	else:
		filelist=glob.glob(path+"/*.json")
		for file in filelist:
			os.remove(file)

	# retrieve all content under the folder
	reqtype='get'
	reqval='/folders/folders/'+folderid+'/members?recursive=true&followReferences=true&limit='+str(limit)
	
	resultdata=callrestapi(reqval,reqtype)

	#print(json.dumps(resultdata,indent=2))

	# loop content
	if 'items' in resultdata:

		total_items=resultdata['count']

		returned_items=len(resultdata['items'])

		if total_items == 0: print("Note: No items returned.")
		else:
			# export each folder and download the package file to the directory

			content_exported=0

			for i in range(0,returned_items):

				id=resultdata['items'][i]["id"]
				uri=resultdata['items'][i]["uri"]
				contenttype=resultdata['items'][i]["contentType"]
				modified=resultdata['items'][i]["modifiedTimeStamp"]
				created=resultdata['items'][i]["creationTimeStamp"]
				name=resultdata['items'][i]["name"]

				itempath=getpath(uri)
				startoffile=itempath.replace("/","_")
				# Parse ISO 8601 dates for comparison
				try:
					# If modified only has the date part, treat it as the end of that day (23:59:59.999999)
					if len(modified) == 10:  # format: YYYY-MM-DD
						modified_dt = datetime.strptime(modified, "%Y-%m-%d")
						modified_dt = modified_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
					else:
						modified_dt = datetime.strptime(modified, "%Y-%m-%dT%H:%M:%S.%fZ")
				except ValueError:
					try:
						modified_dt = datetime.strptime(modified, "%Y-%m-%dT%H:%M:%SZ")
					except ValueError:
						modified_dt = None

				if contenttype != "folder":

					if (modified_dt >= modifiedafter_dt):
				
						json_name=get_valid_filename(startoffile+"_"+resultdata['items'][i]["name"].replace(" ","")+'_'+str(i))
						package_name=str(uuid.uuid1())
						command=clicommand+' transfer export -u '+uri+' --name "'+package_name+'"'

						try:
							print(command)
						except UnicodeEncodeError:
							print(command.encode('ascii','replace'))

						rc=subprocess.call(command, shell=True)
						
						# if the export command fails then skip to the next item
						if rc != 0:
							print("ERROR: There was a problem exporting content '"+ name + "', command returned code "+str(rc))
							continue

						content_exported=content_exported+1	
						reqval='/transfer/packages?filter=eq(name,"'+package_name+'")'
						package_info=callrestapi(reqval,reqtype)

						package_id=package_info['items'][0]['id']

						completefile=os.path.join(path,json_name+'.json')
						command=clicommand+' transfer download --file '+completefile+' --id '+package_id

						try:
							print(command)
						except UnicodeEncodeError:
							print(command.encode('ascii','replace'))

						subprocess.call(command, shell=True)

						print("NOTE: "+contenttype+" '"+ name + "' was exported to " + completefile + " (modified: " + str(modified) + ", after: " + str(modifiedafter_dt) + ")")
						time.sleep(1)
						if autotranferremove:
							print(clicommand+' transfer delete --id '+package_id+"\n")
							remTransferObject = subprocess.Popen(clicommand+' transfer delete --id '+package_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
							remTransferObjectOutput = remTransferObject.communicate(b'Y\n')
							remTransferObject.wait()
					else:
						if contenttype != "folder":
							print("NOTE: " +contenttype+" '"+ name + "' was modified on "+str(modified)+", which is before "+str(modifiedafter_dt)+", content not exported.")


			print("NOTE: "+str(content_exported)+" content items exported to json files in "+path)

else:
	 print("NOTE: Operation cancelled")
