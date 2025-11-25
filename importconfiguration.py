#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# importconfiguration.py
# April 2021
#
# Pass in a directory and this tool will import all the json files in the directory. It depends on the admin CLI
# The json files should be standard viya configuration definitions
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
import argparse, sys, os, json
from sharedfunctions import callrestapi, getapplicationproperties,getclicommand,updateconfigurationproperty

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

# get input parameters
parser = argparse.ArgumentParser(description="Import JSON files that update Viya configuration. All json files in directory will be imported.")
parser.add_argument("-d","--directory", help="Directory that contains JSON configuration definition files to import",required='True')
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
        areyousure=raw_input("WARNING: Are you sure? (Y)")
else:
    areyousure="Y"

if areyousure.upper() =='Y':

    # check that directory exists
    if os.path.isdir(basedir):

        # loop files in the directory
        for filename in os.listdir( basedir ):

            # only process json files
            if filename.lower().endswith('.json'):
                command=clicommand+'  configuration configurations update --file '+os.path.join(basedir,filename)

                updateconfigurationproperty(command)
                print("NOTE: Configuration import attempted from json file "+filename+" in  directory "+basedir  )

    else: print("ERROR: Directory does not exist")
else:
     print("NOTE: Operation cancelled")







