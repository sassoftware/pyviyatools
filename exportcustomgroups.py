#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# exportcustomgroups.py
# Feb 2021
#
# Pass in a customgroups and this tool will  export the customgroups to a apcakge
#
#
# Change History
#
#
# Copyright Â© 2019, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse, sys, subprocess, uuid, time, os, glob, json, tempfile

from sharedfunctions import getfolderid, callrestapi, getapplicationproperties, printresult

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)

tempdir=tempfile.gettempdir()

# get input parameters
parser = argparse.ArgumentParser(description="Export Custom Groups to a Package")

parser.add_argument("-f","--filename", help="Full path to file. (No extension)",default="/tmp/customgroups")
parser.add_argument("--id", help="Subset based on group id containing a string",default=None )
parser.add_argument("--desc", help="Subset based on description containing a string",default=None )

parser.add_argument("-d","--debug", action='store_true', help="Debug")


args= parser.parse_args()

filename=args.filename
debug=args.debug

idval=args.id
descval=args.desc

# create filter
filtercond=[]
delimiter = ','
filtercond.append('eq(providerId,"local")')

if idval!=None: filtercond.append('contains(id,"'+idval+'")')
if descval!=None: filtercond.append('contains(id,"'+descval+'")')

completefilter = 'and('+delimiter.join(filtercond)+')'

# create the requests file of the custom groups

# get all groups that are custom
reqtype='get'
reqval='/identities/groups/?limit=10000&filter='+completefilter
groupslist_result_json=callrestapi(reqval,reqtype)

groups = groupslist_result_json['items']

#if debug: print(json.dumps(groups,indent=2))

""" This is the json format {
"version": 1,
"name": "Modelers",
"description": "Modelers",
"items": [  "/identities/groups/SalesModelers",
            "/identities/groups/HRModelers"
     ]
} """

basename = os.path.basename(filename)

requests_dict={"version":1}
requests_dict["name"]=basename
requests_dict["description"]="Custom Groups from pyviyatools "+basename

grouplist=[]

# create a dictionary that will generate the requests file
for group in groups:

    group_uri="/identities/groups/"+group['id']
    grouplist.append(group_uri)

requests_dict["items"]=grouplist

if debug: print(json.dumps(requests_dict,indent=2))

# build the requests file from the list

request_file=os.path.join(tempdir,filename+"_requests.json")

with open(request_file, "w") as outfile:
	json.dump(requests_dict, outfile)

# export the groups to a package file

command=clicommand+' transfer export -r @'+request_file+' --name "'+basename+'"'

print(command)
subprocess.call(command, shell=True)

reqtype='get'
reqval='/transfer/packages?filter=eq(name,"'+basename+'")'
package_info=callrestapi(reqval,reqtype)
package_id=package_info['items'][0]['id']

completefile=os.path.join(filename+'.json')
command=clicommand+' transfer download --file '+completefile+' --id '+package_id

print(command)
subprocess.call(command, shell=True)
