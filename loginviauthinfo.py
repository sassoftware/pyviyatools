#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# IMPORTANT: calls the sas-admin cli change the variable below if your CLI is not
# installed in the default location 
#
# usage python loginviauthinfo.py
#
# Change History
#
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
from __future__ import print_function
import netrc
import subprocess
import platform
import os
import argparse

# CHANGE THIS VARIABLE IF YOUR CLI IS IN A DIFFERENT LOCATION
clidir='/opt/sas/viya/home/bin/'
#clidir='c:\\admincli\\'

# get input parameters	
parser = argparse.ArgumentParser(description="Authinfo File")
parser.add_argument("-f","--file", help="Enter the path to the authinfo file.",default='.authinfo')
args = parser.parse_args()
authfile=args.file

host=platform.node()

# Read from the authinfo file in your home directory
fname=os.path.join(os.path.expanduser('~'),authfile)

cur_profile=os.environ.get("SAS_CLI_PROFILE","Default")
print("Logging in with profile: ",cur_profile )

if os.path.isfile(fname):

    secrets = netrc.netrc(fname)
    username, account, password = secrets.authenticators( host )
    command=clidir+'sas-admin --profile '+cur_profile+ ' auth login -u '+username+ ' -p '+password
    subprocess.call(command, shell=True)
    
else:
	print('ERROR: '+fname+' does not exist') 