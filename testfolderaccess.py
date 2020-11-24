#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# testfolderaccess.py
# January 2018
#
# Usage:
# python testfolderaccess.py -f folderpath -n name_of_user_or_group -t user|group -s grant|prohibit -m permission [-q] [-d]
#
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


# Import Python modules

import argparse
import subprocess
import json
import sys

from sharedfunctions import getfolderid,callrestapi,getapplicationproperties


# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)

debug=False

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print "%s: %s" % (exception_type.__name__, exception)

sys.excepthook = exception_handler

parser = argparse.ArgumentParser()
parser.add_argument("-f","--folderpath", help="Enter the path to the viya folder.",required='True')
parser.add_argument("-n","--name", help="Enter the name of the user or group to test.",required='True')
parser.add_argument("-t","--principaltype", help="Enter the type of principal to test: user or group.",required='True',choices=['user','group'])
parser.add_argument("-s","--setting", help="Enter grant or prohibit as the expected setting for the permission being tested.",required='True', choices=['grant','prohibit'])
parser.add_argument("-m","--permission", help="Enter the permission to test.",required='True', choices=["read","update","delete","add","secure","remove"])
parser.add_argument("-q","--quiet", action='store_true')
parser.add_argument("-d","--debug", action='store_true')
args = parser.parse_args()
path_to_folder=args.folderpath
name=args.name
principaltype=args.principaltype
setting=args.setting
permission=args.permission
quiet=args.quiet
debug=args.debug


getfolderid_result_json=getfolderid(path_to_folder)

if (debug):
    print(getfolderid_result_json)


if getfolderid_result_json[0] is not None:
    folder_uri=getfolderid_result_json[1]
    if (debug):
        print("Id  = "+getfolderid_result_json[0])
        print("URI = "+folder_uri)
        print("Path = "+getfolderid_result_json[2])

endpoint='/authorization/decision'
if(principaltype.lower()=='user'):
    endpoint=endpoint+'?additionalUser='+name
else:
    endpoint=endpoint+'?additionalGroup='+name
method='post'
accept='application/vnd.sas.authorization.explanations+json'
content='application/vnd.sas.selection+json'
inputdata={"resources":[folder_uri]}

decisions_result_json=callrestapi(endpoint,method,accept,content,inputdata)

#print(decisions_result_json)
#print('decisions_result_json is a '+type(decisions_result_json).__name__+' object') #decisions_result_json is a dict object
e = decisions_result_json['explanations'][folder_uri]

#print('e is a '+type(e).__name__+' object') #e is a list object

principal_found=False

for pi in e:
    #print pi['principal']
    # Test whether principal has a name: authenticatedusers and guest do not have a name key
    if 'name' in pi['principal']:
        if (pi['principal']['name'].lower() == name.lower()):
            #print(pi['principal']['name']+':'+pi[permission.lower()]['result'])
            principal_found=True
            if (pi[permission.lower()]['result'] == setting.lower()):
                if not quiet:
                    print('TEST PASSED: the effective '+permission.lower()+' permission for '+pi['principal']['name']+' on folder '+path_to_folder+' is '+pi[permission.lower()]['result'])
            else:
                raise Exception('TEST FAILED: the effective '+permission.lower()+' permission for '+pi['principal']['name']+' on folder '+path_to_folder+' is '+pi[permission.lower()]['result']+', not '+setting.lower())

if not principal_found:
    raise Exception('No direct or inherited authorization rules found for \''+name+'\' on folder '+path_to_folder+'. Please check that you spelled the principal name correctly, and specified the correct principal type - user or group.')
