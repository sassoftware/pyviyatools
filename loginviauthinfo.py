#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# IMPORTANT: calls the sas-admin cli change the variable below if your CLI is not
# installed in the default location 
#
# usage python loginviauthinfo.py
#              loginviauthinfo.py -f /tmp/myfile
#
#
# Authinfo file users .netrc format https://www.ibm.com/support/knowledgecenter/en/ssw_aix_71/filesreference/netrc.html
#
# Example
#
# default user sasadm1 password mypass
# machine sasviya01.race.sas.com user sasadm2 password mpass2
#
# Change History
#
# 25AUG2019 modified to logon to the host in the profile and support multiple lines iin authinfo
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
import json
from sharedfunctions import file_accessible
from urlparse import urlparse

# CHANGE THIS VARIABLE IF YOUR CLI IS IN A DIFFERENT LOCATION
clidir='/opt/sas/viya/home/bin/'
#clidir='c:\\admincli\\'

debug=0
profileexists=0

# get input parameters	
parser = argparse.ArgumentParser(description="Authinfo File")
parser.add_argument("-f","--file", help="Enter the path to the authinfo file.",default='.authinfo')
args = parser.parse_args()
authfile=args.file

# Read from the authinfo file in your home directory
fname=os.path.join(os.path.expanduser('~'),authfile)

# get current profile from ENV variable or if not set use default
myprofile=os.environ.get("SAS_CLI_PROFILE","Default")
print("Logging in with profile: ",myprofile )

# get hostname from profile
endpointfile=os.path.join(os.path.expanduser('~'),'.sas','config.json')
access_file=file_accessible(endpointfile,'r')
badprofile=0

#profile does not exist
if access_file==False:
    badprofile=1 
    host='default'


#profile is empty file
if os.stat(endpointfile).st_size==0: 
    badprofile=1
    host='default'

# get json from profile

if not badprofile:

    with open(endpointfile) as json_file:
        data = json.load(json_file)

    # get the hostname from the current profile
    if myprofile in data:
        urlparts=urlparse(data[myprofile]['sas-endpoint'])
        host=urlparts.netloc
        print("Getting Credentials for: "+host)
        profileexists=1

    else: #without a profile don't know the hostname
        profileexists=0
        print("ERROR: profile "+myprofile+" does not exist. Recreate profile with sas-admin profile init.")


if profileexists:

    # based on the hostname get the credentials and login
    if os.path.isfile(fname):

       secrets = netrc.netrc(fname)
       username, account, password = secrets.authenticators( host )

       if debug:
          print('user: '+username)
          print('profile: '+myprofile)
          print('host: '+host)

       command=clidir+'sas-admin --profile '+myprofile+ ' auth login -u '+username+ ' -p '+password
       subprocess.call(command, shell=True)
    
    else:
       print('ERROR: '+fname+' does not exist') 
