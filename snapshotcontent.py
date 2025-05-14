#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# snapshotcontent.py
# Nov 2024
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
from sharedfunctions import getfolderid, callrestapi, getpath, getapplicationproperties, get_valid_filename, createdatefilter,getclicommand, getpath

# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="Export Viya content each to its own unique transfer package")
parser.add_argument("-d","--directory", help="Directory to store report packages",required='True')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
#parser.add_argument("-isf","--includesubfolder", help="Include Sub-folders of the main folder.", action='store_false')
parser.add_argument("-f","--folderpath", help="Folder Path starts with?",required='True')
parser.add_argument("-m","--modifiedinlast", help="Content modified in the last of this number of days.",default='-1')
parser.add_argument("-t","--transferremove", help="Remove transfer file from Infrastructure Data Server after download?", action='store_true')
parser.add_argument("-l","--limit", type=int,help="Specify the number of records to pull. Default is 1000.",default=1000)

args= parser.parse_args()
basedir=args.directory
quietmode=args.quiet
autotranferremove=args.transferremove
folderpath=args.folderpath
limit=args.limit
days=args.days
#includesubfolder=args.includesubfolder

# filtering
datefilter=createdatefilter(olderoryounger="younger",datevar='modifiedTimeStamp',days=days)
print(datefilter)

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

	print(json.dumps(resultdata,indent=2))

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
				itempath=getpath(uri)
				startoffile=itempath.replace("/","_")

				if contenttype != "folder":

					content_exported=content_exported+1

					json_name=get_valid_filename(startoffile+"_"+resultdata['items'][i]["name"].replace(" ","")+'_'+str(i))
					package_name=str(uuid.uuid1())
					command=clicommand+' transfer export -u '+uri+' --name "'+package_name+'"'

					try:
						print(command)
					except UnicodeEncodeError:
						print(command.encode('ascii','replace'))

					subprocess.call(command, shell=True)

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

					#time.sleep(1)
					if autotranferremove:
						print(clicommand+' transfer delete --id '+package_id+"\n")
						remTransferObject = subprocess.Popen(clicommand+' transfer delete --id '+package_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
						remTransferObjectOutput = remTransferObject.communicate(b'Y\n')
						remTransferObject.wait()


			print("NOTE: "+str(content_exported)+" content items exported to json files in "+path)

else:
	 print("NOTE: Operation cancelled")
