#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# createreportimage.py
# Jan 2025
# Developed on SAS Viya Version: 2024.12
#
# this tool will generate a svg of a visual analytics report (or report object) and save it to 
# the local filesystem
#
# The purpose of the tool is to be able programatically archive a report  (or report object) in svg format
#
# example
#
# export the visual analytcs report 12345678-1234-1234-1234-123456789abc to the local directory "/tmp" as
# image.svg
#
# createreportimage.py -d /tmp -f image.svg -r 12345678-1234-1234-1234-123456789abc 
#
# 
# Change History
#
# 21jan2025 initial coding
#
# Copyright Ã‚Â© 2025, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse, sys, subprocess, os, glob, ast
from sharedfunctions import callrestapi, getapplicationproperties,getclicommand,getbaseurl


# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="Generate a Visual Analytics Report Image")
parser.add_argument("-d","--directory", help="Directory to store output file",required='True')
parser.add_argument("-f","--file", help="Name of the output file",required='True')
parser.add_argument("-r","--reportId", help="ID of the report to export",required='True')
parser.add_argument("-s","--size", help="Size of the output image as a string (ex: '1024px,768px')",default='1024px,768px')
parser.add_argument("-o","--reportObjectId", help="ID of the report object to export (ex: ve123)")
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')

args= parser.parse_args()
basedir=args.directory
outfile=args.file
imagesize=args.size
reporturi=args.reportId
reportobjectid=args.reportObjectId
quietmode=args.quiet

# create objectRequest var
if reportobjectid!=None: objectRequest="&reportObject="+reportobjectid
else: objectRequest=""

# ensure output filename has proper extension
if not outfile.endswith('.svg'):
	outfile += '.svg'

# build output file full path
archivefile=basedir+'/'+outfile

# prompt if directory exists because existing file will be deleted
if os.path.exists(basedir):

	# if the quiet mode flag is not passed then prompt to continue
	if not quietmode:

		if version  > 2:
			areyousure=input("The folder exists, the following file: "+outfile+" will be deleted. Continue? (Y)")
		else:
			areyousure=raw_input("The folder exists, the following file: "+outfile+" will be deleted. Continue? (Y)")
	else:
		areyousure="Y"

else: areyousure="Y"

# prompt is Y if user selected Y, its a new directory, or user selected quiet mode
if areyousure.upper() =='Y':
	path=basedir

	# create directory if it doesn't exist
	if not os.path.exists(path): os.makedirs(path)
	else:
		if os.path.exists(archivefile):
			os.remove(archivefile)

	# generate the image
	reqtype='get'
	reqvalImg='/visualAnalytics/reports/'+reporturi+'/svg?size='+imagesize+objectRequest
	
	# save the output file
	resultdata=callrestapi(reqvalImg,reqtype,acceptType='image/svg+xml')
	with open(archivefile, 'w') as fp:
		fp.write(resultdata)

		fp.close()
else:
	 print("NOTE: Operation cancelled")