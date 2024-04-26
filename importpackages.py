#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# importpackages.py
# March 2018
#
# Pass in a directory and this tool will import all the json files in the directory. It depends on the admin CLI
#
# Change History
#
# 12feb2020 added --output text to the import command so that status will show
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
#  OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
# change log
# renamed to importpackages.py to be more descriptive of actual usage
# DEC202023 added the ability to use a mapping file
# APR2024 remove hardcoding of /tmp
#
# Import Python modules
import argparse, sys, subprocess, os, json, tempfile
from sharedfunctions import callrestapi, getapplicationproperties,getclicommand



# get input parameters
parser = argparse.ArgumentParser(description="Import JSON files from directory. All json files in directory will be imported.")
parser.add_argument("-d","--directory", help="Directory that contains JSON files to import",required='True')
parser.add_argument("-m","--mapping", help="A mapping file to use with the import.",default=None)
parser.add_argument("-ea","--excludeauthorization", help="Exclude the import of authorization rules.", action='store_true')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')

args= parser.parse_args()
basedir=args.directory
quietmode=args.quiet
noauth=args.excludeauthorization
mapping=args.mapping

# get python version
version=int(str(sys.version_info[0]))

tempfilepath=tempfile.gettempdir()
#build tempfile names
tmppackageidfile=os.path.join(tempfilepath,"packageid.json")
tmpmappingfile=os.path.join(tempfilepath,"mapping_json.json")

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

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
				command=clicommand+' --output fulljson transfer upload --file "'+os.path.join(basedir,filename)+'" > '+tmppackageidfile
				print(command)
				subprocess.call(command, shell=True)

				# create or use mapping file if we need to

				# no mapping required
				if not mapping and not noauth:
					mapping_options=""
				# create mapping file to exclude authorization
				elif not mapping and noauth:
					
					#create no authorization mapping file 
					mappingdict={"version": 1,"options": {"promoteAuthorization":False}}
					json_object = json.dumps(mappingdict, indent=4)
					with open (mapping_file,'w') as outfile:
						outfile.write(json_object)				
					mapping_options=" --mapping "+tmpmappingfile

				# need to merge mapping file and noauth	
				elif noauth and mapping:

					mappingdict={"version": 1,"options": {"promoteAuthorization":False}}
					json_object = json.dumps(mappingdict, indent=4)
					with open(mapping) as map_file:
						map_dict = json.load(map_file)
					
					#newmap={**mappingdict,**map_dict} #only in python3
					newmap=map_dict.copy()
					newmap.update(mappingdict)
					print(newmap)

					json_map = json.dumps(newmap, indent=4)					
					with open (mapping_file,'w') as outfile:
						outfile.write(json_map)
					mapping_options=" --mapping "+tmpmappingfile
				
				elif mapping and not noauth:
					mapping_options=" --mapping "+mapping
				
							
				#print the json from the upload
				with open(tmppackageidfile) as json_file:
					package_data = json.load(json_file)

				print(json.dumps(package_data,indent=2))

				# get the packageid and import the package
				packageid=package_data["id"]

				command=clicommand+' --output text -q transfer import --id '+packageid+' '+mapping_options
				print(command)

				subprocess.call(command, shell=True)
				print("NOTE: Viya content imported from json files in "+basedir)

				if noauth:	os.remove(tmpmappingfile)
					
				os.remove(tmppackageidfile)

	else: print("ERROR: Directory does not exist")
else:
	 print("NOTE: Operation cancelled")


