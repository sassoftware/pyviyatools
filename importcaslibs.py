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
# 14APR2023 - Added 'superuser' argument
# 01JUN2034 - Include 'superuser' with authorization apply
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
import argparse, sys, subprocess, os, json, shlex
from sharedfunctions import callrestapi, getapplicationproperties, file_accessible, getclicommand


# get input parameters
parser = argparse.ArgumentParser(description="Import JSON files that define path-based CASLIBS from directory. All json files in directory will be imported.")
parser.add_argument("-d","--directory", help="Directory that contains JSON caslib definition files to import",required=True)
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
parser.add_argument("-su","--superuser", help="Runs the CASLIB create process with superuser permissions.", action='store_true')
parser.add_argument("-v","--verbose", help="Show merged stdout/stderr for successful commands and pass --verbose to CLI.", action='store_true')
args= parser.parse_args()
basedir=args.directory
quietmode=args.quiet
su=args.superuser
verbose=args.verbose


# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

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

tryimport=0

if areyousure.upper() =='Y':

      # check that directory exists
      if os.path.isdir(basedir):

            # loop files in the directory
            for filename in os.listdir( basedir ):

                  fullfile=os.path.join(basedir,filename)
                  
                  # only process json files
                  if filename.lower().endswith('.json'):

                        #create the caslib
                        if '_authorization_' not in filename:

                              # get some caslib attributes for the authorization import
                              with open(fullfile) as json_file:
                                    data = json.load(json_file)

                              # check if key 'name' and 'server' exist in the json data
                              if 'name' not in data or 'server' not in data:
                                    print("ERROR: Missing required keys in file "+filename)
                                    continue
                              
                              caslibname=data['name']
                              casserver=data['server']
                              # creates then runs the caslib creation command, with superuser perms where selected
                              # build safe argument list for subprocess (avoid shell=True)
                              cmd_args = [clicommand, 'cas', 'caslibs', 'create', 'path', '--source-file', fullfile]

                              # if verbose flag passed to this script, also pass it to the CLI (e.g. sas-viya --verbose ...)
                              if verbose:
                                    cmd_args.insert(1, '--verbose')

                              if su:
                                    cmd_args.append('--su')
                              print("NOTE: Viya Caslib import attempted from json file "+filename+" in  directory "+basedir  )
                              print("RUN: "+' '.join(shlex.quote(str(a)) for a in cmd_args))

                              try:
                                    result = subprocess.run(
                                          cmd_args,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          text=True
                                    )

                                    print("RETURN CODE: "+str(result.returncode))

                                    # On failure print merged output (stdout+stderr)
                                    if result.returncode != 0:
                                          if result.stdout:
                                                print("OUTPUT:")
                                                print(result.stdout)
                                          print("ERROR: Command failed for file "+filename)
                                          continue
                                    else:
                                          if result.stdout:
                                                if verbose:
                                                      print("OUTPUT:")
                                                else:
                                                      print("STDOUT:")
                                                print(result.stdout)

                              except Exception as e:
                                    print("ERROR executing command for file "+filename)
                                    print(str(e))
                                    continue

                              tryimport=tryimport+1

                              # apply the authorization if authorization file exists
                              authfile=os.path.join(basedir,caslibname+'_authorization_.json')
                              access_file=file_accessible(authfile,'r')

                              if access_file==True:
                                    
                                    # build safe argument list for authorization replace (avoid shell=True)
                                    auth_args = [clicommand, 'cas', 'caslibs', 'replace-controls', '--server', casserver, '--name', caslibname, '--force', '--source-file', authfile]

                                    # if verbose flag passed to this script, also pass it to the CLI
                                    if verbose:
                                          auth_args.insert(1, '--verbose')

                                    if su:
                                          auth_args.insert( auth_args.index('--source-file'), '--su')

                                    print("NOTE: Viya Caslib authorization import attempted from json file "+filename+" in  directory "+basedir  )
                                    print("RUN: "+' '.join(shlex.quote(str(a)) for a in auth_args))
                                    try:
                                          auth_result = subprocess.run(auth_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                                          if auth_result.returncode != 0:
                                                if auth_result.stdout:
                                                      print("OUTPUT:")
                                                      print(auth_result.stdout)
                                                print("ERROR: Authorization command failed for caslib "+caslibname)
                                          else:
                                                if auth_result.stdout:
                                                      if verbose:
                                                            print("OUTPUT:")
                                                      else:
                                                            print("STDOUT:")
                                                      print(auth_result.stdout)
                                    except Exception as e:
                                          print("ERROR executing auth command for file "+filename)
                                          print(str(e))

            if not tryimport: print("NOTE: No caslib files available for import.")

      else: print("ERROR: Directory does not exist.")
else:
       print("NOTE: Operation cancelled.")







