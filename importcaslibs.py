#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# importcaslibs.py
# April 2021
#
# Pass in a directory and this tool will import all the json files in the directory. It depends on the admin CLI
# The json files should be standard caslib definitions
#
# File format
#{
#"attributes": { "active": false, "personal": false, "subDirs": false},
#"description": "",
#"name": "Sales2",
# "path": "/tmp/sales",
# "scope": "global",
# "server": "cas-shared-default",
# "type": "PATH"
#}
#
#
# Change History
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
#  OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
#
# Import Python modules
import argparse, sys, subprocess, os, json
from sharedfunctions import callrestapi, getapplicationproperties

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)

# get input parameters
parser = argparse.ArgumentParser(description="Import JSON files that define path-based CASLIBS from directory. All json files in directory will be imported.")
parser.add_argument("-d","--directory", help="Directory that contains JSON caslib dfinition files to import",required='True')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
args= parser.parse_args()
basedir=args.directory
quietmode=args.quiet

# get python version
version=int(str(sys.version_info[0]))

# if the quiet mode flag is not passed then prompt to continue
if not quietmode:

	if version  > 2:
		areyousure=input("WARNING: Are you sure? (Y)")
	else:
		areyousure=raw_input("WARNING:   Are you sure? (Y)")
else:
	areyousure="Y"

if areyousure.upper() =='Y':

	# check that directory exists
	if os.path.isdir(basedir):

		# loop files in the directory
		for filename in os.listdir( basedir ):

			# only process json files
			if filename.lower().endswith('.json'):
                                command=clicommand+'  cas caslibs create path --source-file '+os.path.join(basedir,filename)
				print(command)
				subprocess.call(command, shell=True)

				print("NOTE: Viya Caslib imported attempted from json file "+filename+" in  directory "+basedir  )
            else: print("NOTE: No JSON files in directory")

	else: print("ERROR: Directory does not exist")
else:
	 print("NOTE: Operation cancelled")







