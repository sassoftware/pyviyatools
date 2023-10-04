#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# modifyglobalcaslib.py
# October 2023
#
# Serves as a wrapper for listing granting access to users/groups for Global
# and Session CASLIBs.
#
#
# Change History
# 04OCT2023 Initial development
#
#
# USAGE EXAMPLES
#
# 1. Listing special CASLIB permissions
# ./modifyglobalcaslib.py -o list
#
# 2. Granting a group rights to create Global CASLIBs
# ./modifyglobalcaslib.py -o grant -t group -i <groupname>
#
# 3. Granting a user rights to create Session CASLIBs
# ./modifyglobalcaslib.py -o grant -t user -i <username> --scope session
#
# 4. Revoking a group rights to create Global CASLIBs
# ./modifyglobalcaslib.py -o revoke -t group -i <groupname>
#
#
# OPTIONAL PARAMETERS
# --cas may be used to override its default value of 'cas-shared-default' with an alternative CAS server name.
# --scope may be used to override its default value of 'global' with 'session'.
#
#
# NOTE
# There is not validation of user or group names performed by the CLI prior to performing a 'grant' or 'revoke' operation.
# Do use caution with the spelling of user/group names when using this utility.
# (PMCPFR-1420)
#
#
# Copyright © 2023, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
#  OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
#
# Import Python modules
import argparse, sys, subprocess, os
from sharedfunctions import callrestapi, getapplicationproperties

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)

# get input parameters
parser = argparse.ArgumentParser(description="Import JSON files that update Viya configuration. All json files in directory will be imported.")
parser.add_argument("-o","--operator", help="Option to list, grant or revoke access to special CASLIBs", choices=['list','grant','revoke'], required='True')
parser.add_argument("-i","--id", help="A user or group ID")
parser.add_argument("-t","--idtype", help="'user' or 'group'", choices=['user', 'group'])
parser.add_argument("--cas", help="Sets a non-default CAS Server.", default='cas-shared-default')
parser.add_argument("--scope", help="'global' (default) or 'session'", choices=['global', 'session'], default='global')
args= parser.parse_args()
operator=args.operator.lower()
id=args.id
idtype=args.idtype
casserver=args.cas
scope=args.scope

# sets CAS server as env var
os.environ['SAS_CLI_DEFAULT_CAS_SERVER']=casserver

# reads operator argument and compiles a Viya CLI command
if operator == "list":
    command=clicommand+' cas servers privileges list'
elif operator != "list":
    # verifies required arguments are present and exits if any are missing
    if id is None or idtype is None:
      print("\033[1;31mERROR: A value for both '-i' and '-t' must be set in order to use "+operator+" operator.\033[0m")
      sys.exit()
    else:
      command=clicommand+' cas servers privileges modify --'+operator+' --'+scope+' --'+idtype+" '"+id+"'"

# prints notifications and runs Viya CLI command
print('\033[1;32mSetting CAS server: '+casserver+'\033[0m')
print('\033[1;32mRunning command: '+command+'\033[0m')
subprocess.call(command, shell=True)