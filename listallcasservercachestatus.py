#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listallcasservercachestatus.py
# February 2020
#
# Usage:
# listallcasservercachestatus.py [--noheader] [-d]
#
# Examples:
#
# 1. Return list of CAS_DISK_CACHE usage on all CAS servers
#        ./listallcasservercachestatus.py
#
# Copyright © 2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

debug=False

# Import Python modules
from tabulate import tabulate       # pip install tabulate
import argparse
import swat                         # pip install swat
import sys
from sharedfunctions import callrestapi

parser = argparse.ArgumentParser()
parser.add_argument("--noheader", action='store_true', help="Do not print the header row")
parser.add_argument("-d","--debug", action='store_true', help="Debug")
args = parser.parse_args()
noheader=args.noheader
debug=args.debug

# Print header row unless noheader argument was specified
if not noheader:
    print('server,host-or-ip,port,restPort, [table]')

endpoint='/casManagement/servers'
method='get'

#make the rest call
serverlist_result_json=callrestapi(endpoint,method)

if debug:
    print(serverlist_result_json)
    print('serverlist_result_json is a '+type(serverlist_result_json).__name__+' object') #serverlist_result_json is a dictionary

servers = serverlist_result_json['items']

for server in servers:
    servername=server['name']
    serverhost=server['host']
    serverport=server['port']
    serverrest=server['restPort']

    print(servername+','+serverhost+','+str(serverport)+','+str(serverrest))

    # connect to each CAS server
    s = swat.CAS(serverhost, serverport)
    # TLS relies on env var $CAS_CLIENT_SSL_CA_LIST=/opt/sas/viya/config/etc/SASSecurityCertificateFramework/cacerts/vault-ca.crt (or local location)
    # else "ERROR: SSL Error: Missing CA trust list"

    # get CAS_DISK_CACHE usage
    s.accessControl.assumeRole(adminRole="superuser")   # superuser role reqd
    results = s.builtins.getCacheInfo                   # returns dictionary and table

    # display table with CAS_DISK_CACHE usage stats
    print(tabulate(results,headers='firstrow'))
