#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# exportgeoproviders.py
# April 2019
#
# this tool will export all the geographic data providers in your viya system
# to there own individual json file in a directory.
#
# The purpose of the tools is to be able to have a sweeping but also granular
# backup of geographic data providers so that you could restore an individual 
# provider to a system.
#
# example
#
# save all geographic providers, each to their own package
# exportgeoproviders.py -d ~/geoProviders/
#
# Change History
#
# 12dec2022 initial coding
#
# Copyright Ã‚Â© 2022, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse, sys, subprocess, os, glob
from sharedfunctions import callrestapi, getapplicationproperties,getclicommand


# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()


# get input parameters
parser = argparse.ArgumentParser(description="Export each geo providers to it's own unique transfer package")
parser.add_argument("-d","--directory", help="Directory to store report packages",required='True')
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')

args= parser.parse_args()
basedir=args.directory
quietmode=args.quiet

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

	# retrieve all geographic providers in the system
	reqtype='get'
	reqval='/maps/providers?limit=10000'

	resultdata=callrestapi(reqval,reqtype)
	# loop root proviers
	if 'items' in resultdata:

		total_items=resultdata['count']

		returned_items=len(resultdata['items'])

		if total_items == 0: print("Note: No items returned.")
		else:
			# export each provider and download the json file to the directory

			providers_exported=0

			for i in range(0,returned_items):

				providerID=resultdata['items'][i]["name"]
				
				print("The map provder: '"+providerID+"' will be exported to: "+basedir+providerID+".json")

				command=clicommand+' reports map-providers export --map-provider-name '+providerID+' --output-location '+basedir+''
				print(command)

				subprocess.call(command, shell=True)

				providers_exported=providers_exported+1
				print( )
				print( )
				
			print("NOTE: "+str(total_items)+" total geographic data providers found, "+str(providers_exported)+" geographic data providers exported to json files in "+path)

else:
	 print("NOTE: Operation cancelled")