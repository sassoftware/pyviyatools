#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# importtemplates.py
# March 2021
#
# Pass in a directory and this tool will import all the json files in the directory 
# to the template service. It depends on the admin CLI
#
# Change History
# 12MAR2021 first version
#
# Copyright © 2021, SAS Institute Inc., C#!/usr/bin/python
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


####################################################################
#### COMMAND LINE EXAMPLE                                       ####
####################################################################
#### ./importtemplates.py -                                     ####
####                        -d --directory dir with json files  ####
####                        -q --quiet suppress confirm prompt  ####
####################################################################

import argparse, sys, subprocess, os, json
from sharedfunctions import callrestapi, getapplicationproperties, getinputjson

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)

parser = argparse.ArgumentParser(description="Upload templates")
parser.add_argument("-d","--directory", help="Directory that contains JSON files to import",required='True')
parser.add_argument("-q","--quiet", help="Suppress the confirmation prompt.", action='store_true')

args = parser.parse_args()
basedir = args.directory
quietmode = args.quiet

# get python version
version=int(str(sys.version_info[0]))

# check that directory exists
if os.path.isdir(basedir):
	id=None

	# loop files in the directory
	for filename in os.listdir( basedir ):

		# only process json files
		if filename.lower().endswith('.json'):
			reqfile=os.path.join(basedir,filename)

			#print the json from the upload
			with open(reqfile) as json_file:
				data = json.load(json_file)
			print(json.dumps(data,indent=2))

			if 'name' in data:
				name=data['name']

			# check to see if the json template exists
			# Execute actual code to upload the json template
			reqtype="get"
			reqval="/templates/templates/?filter=eq(name, '"+name+"')"
			reqaccept="application/vnd.sas.collection+json"
			reccontent="application/json"
			resultdata=callrestapi(reqval,reqtype,reqaccept,reccontent,data,stoponerror=0)

			if 'items' in resultdata:
				returned_items=len(resultdata['items'])
				for i in range(0,returned_items):
					id=resultdata['items'][i]['id']
					print("Template already exists - "+name+" ["+id+"]")
			else:
				id=None

			#upload the json template
			# Execute actual code to upload the json template
			if id:
				# if the quiet mode flag is not passed then prompt to continue
				if not quietmode:
					if version  > 2:
						areyousure=input("\nWARNING: Template already exists - "+name+", replace it? (Y)")
					else:
						areyousure=raw_input("\nWARNING:Template already exists - "+name+", replace it?? (Y)")
				else:
					areyousure="Y"

				if areyousure.upper() =='Y':
					reqtype="put"
					reqval="/templates/templates/"+id
				else:
					print("NOTE: Operation cancelled")
			else:
				reqtype="post"
				reqval="/templates/templates/"

			if not id or areyousure.upper() =='Y':
				reqaccept="application/vnd.sas.template+json"
				reccontent="application/json"

				print("Uploading template "+name)
				resultdata=callrestapi(reqval,reqtype,reqaccept,reccontent,data,stoponerror=0)

				print("NOTE: Viya content imported from json file "+filename)
			print("\n")

	print("NOTE: Completed Viya content import from json files in "+basedir)

else: print("ERROR: Directory does not exist")

####################################################################
#### EXAMPLE TEMPLATES                                          ####
####################################################################
#### SAS_Email_Message_text.json                                ####
#### SAS_Email_Message_html.json                                ####
####################################################################
