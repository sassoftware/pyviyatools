#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# importfoldertree.py March 2018
#
# Pass in a directory and this tool will import all the json files in the directory. It depends on the admin CLI
#
# Change History
#
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS 
#  OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
# Import Python modules
import argparse, sys, subprocess, os, json 
from sharedfunctions import callrestapi

# CHANGE THIS VARIABLE IF YOUR CLI IS IN A DIFFERENT LOCATION
clidir='/opt/sas/viya/home/bin/'

# get input parameters
parser = argparse.ArgumentParser(description="Import JSON files from directory. All json files in directory will be imported.")
parser.add_argument("-d","--directory", help="Directory that contains JSON files to import",required='True')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
args= parser.parse_args()
basedir=args.directory
quietmode=args.quiet

# get python version  
version=int(str(sys.version_info[0]))


# if the quiet mode flag is not passed then prompt to continue
if not quietmode:

	if version  > 2:
		areyousure=input("WARNING: If content from the packages already exists in folders it will be replaced. Continue? (Y)")
	else:
		areyousure=raw_input("WARNING:If content from the packages already exists in folders it will be replaced. Continue? (Y)") 
else:
	areyousure="Y"

if areyousure.upper() =='Y':

	# check that directory exists
	if os.path.isdir(basedir):

		# loop files in the directory
		for filename in os.listdir( basedir ):

			# only process json files
			if filename.lower().endswith('.json'):

				#upload the json package
				command=clidir+'sas-admin transfer upload --file '+os.path.join(basedir,filename)+'> /tmp/packageid.json'
				print(command)
				subprocess.call(command, shell=True)

				#print the json from the upload
				with open('/tmp/packageid.json') as json_file:
					package_data = json.load(json_file)

				print(json.dumps(package_data,indent=2))

				# get the packageid and import the package
				packageid=package_data["id"]
				command=clidir+'sas-admin -q transfer import --id '+packageid
				print(command)

				subprocess.call(command, shell=True)
				print("NOTE: Viya root folders imported from json files in "+basedir)

	else: print("ERROR: Directory does not exist")
else:
	 print("NOTE: Operation cancelled")


