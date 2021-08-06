#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# listcaslibs.py
# January 2019
#
# Usage:
# listcaslibs.py [--noheader] [-d]
#
# Examples:
#
# 1. Return list of all CAS libraries on all servers
#        ./listcaslibs.py
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse, json, sys, os, glob
from sharedfunctions import callrestapi

# get python version
version=int(str(sys.version_info[0]))

parser = argparse.ArgumentParser()
parser.add_argument("-s","--server", help="CAS Server (default is cas-shared-default)",default="cas-shared-default")
parser.add_argument("-i","--includeauthorization", help="Also export caslib authorization",action='store_true')
parser.add_argument("-d","--directory", help="Directory where packages are written.",required='True')
parser.add_argument("-nc","--namecontains", help="Name contains",default=None)
parser.add_argument("-dc","--descriptioncontains", help="Name contains",default=None)
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
parser.add_argument("--debug", action='store_true', help="Debug")

args = parser.parse_args()
debug=args.debug
server=args.server
basedir=args.directory
quietmode=args.quiet
includeauthorization=args.includeauthorization
nameval=args.namecontains
descval=args.descriptioncontains

delimiter=','
# create a list for filter conditions
filtercond=[]

if nameval!=None: filtercond.append('contains(name,"'+nameval+'")')
if descval!=None: filtercond.append('contains(description,"'+descval+'")')


if len(filtercond)>1:
    completefilter = 'and('+delimiter.join(filtercond)+')'
elif len(filtercond)==1:
    if nameval!=None: completefilter='contains(name,"'+nameval+'")'
    if descval!=None: completefilter='contains(description,"'+descval+'")'

if len(filtercond)==0: completefilter=str()
else: completefilter='&filter='+completefilter

# prompt if directory exists because existing json files are deleted
if os.path.exists(basedir):

    # if the quiet mode flag is not passed then prompt to continue
    if not quietmode:

        if version  > 2:
            areyousure=input("The folder exists any existing json files in it will be deleted. Continue? (Y)")
        else:
            areyousure=raw_input("he folder exists any existing json files in it will be deleted. Continue? (Y)")
    else:
        areyousure="Y"
else: areyousure="Y"

# prompt is Y if user selected Y, its a new directory, or user selected quiet mode
if areyousure.upper() =='Y':

    path=basedir

    # List the caslibs in this server
    endpoint='/casManagement/servers/'+server+'/caslibs?excludeItemLinks=true&limit=10000'+completefilter
    if debug: print(endpoint)
    method='get'
    caslibs_result_json=callrestapi(endpoint,method)
    caslibs=caslibs_result_json['items']

    if len(caslibs):

        if not os.path.exists(path): os.makedirs(path)
        else:
            filelist=glob.glob(path+"/*.json")

            for file in filelist:
                os.remove(file)

    # loop the caslibs and output a json file
    for caslib in caslibs:

        caslib['server']=server
        caslibname=caslib['name']
        #print(json.dumps( caslib,indent=2))
        fullfile=os.path.join(basedir,caslibname+'.json')
        outfile=open(fullfile, "w")
        json.dump(caslib, outfile)

        # optionally export caslib authorization
        if includeauthorization:
            method='get'
            endpoint='/casAccessManagement/servers/'+server+'/caslibControls/'+caslibname+'?excludeItemLinks=true&limit=10000'
            casauth_result=callrestapi(endpoint,method)

            authfile=os.path.join(basedir,caslibname+'_authorization_.json')
            outauth=open(authfile, "w")

            # delete metadata items before writing file
            if 'name' in casauth_result: casauth_result.pop('name')
            if 'count' in casauth_result: casauth_result.pop('count')
            if 'start' in casauth_result: casauth_result.pop('start')
            if 'limit' in casauth_result: casauth_result.pop('limit')
            if 'links' in casauth_result: casauth_result.pop('links')
            if 'version' in casauth_result: casauth_result.pop('version')
                

            json.dump(casauth_result, outauth)

if len(caslibs):
    print("NOTE: caslib definitions written to "+basedir)
    if includeauthorization: print("NOTE: Authorization files included.")
else: print("NOTE: no caslibs found.")
