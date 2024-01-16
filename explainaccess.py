#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# explainaccess.py
# November 2018
#
# Usage:
# explainaccess.py [-f folderpath | -u objectURI] [-n name_of_user_or_group -t user|group] [-p] [--header] [--direct_only] [-l permissions_list] [-c true|false] [-d]
#
# Examples:
#
# 1. Explain direct and indirect permissions on the folder /folderA/folderB, no header row. For folders, conveyed permissions are shown by default.
#        ./explainaccess.py -f /folderA/folderB
#
# 2. As 1. but for a specific user named Heather
#        ./explainaccess.py -f /folderA/folderB -n Heather -t user
#
# 3. As 1. with a header row
#        ./explainaccess.py -f /folderA/folderB --header
#
# 4. As 1. with a header row and the folder path, which is useful if you concatenate sets of results in one file
#        ./explainaccess.py -f /folderA/folderB -p --header
#
# 5. As 1. showing only rows which include a direct grant or prohibit
#        ./explainaccess.py -f /folderA/folderB --direct_only
#
# 6. Explain direct and indirect permissions on a service endpoint. Note in the results that there are no conveyed permissions.
#    By default they are not shown for URIs.
#        ./explainaccess.py -u /SASEnvironmentManager/dashboard
#
# 7. As 6. but including a header row and the create permission, which is relevant for services but not for folders and other objects
#        ./explainaccess.py -u /SASEnvironmentManager/dashboard --header -l read update delete secure add remove create
#
# 8. Explain direct and indirect permissions on a report, reducing the permissions reported to just read, update, delete and secure,
#    since none of add, remove or create are applicable to a report.
#        ./explainaccess.py -u /reports/reports/e2e0e601-b5a9-4601-829a-c5137f7441c6 --header -l read update delete secure
#
# 9. Explain direct and indirect permissions on a folder expressed as a URI. Keep the default permissions list, but for completeness
#    we must also specify -c true to request conveyed permissions be displayed, as they are not displayed by default for URIs.
#        ./explainaccess.py -u /folders/folders/9145d26a-2c0d-4523-8835-ad186bb57fa6 --header -p -c true
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
import os
from sharedfunctions import getfolderid,callrestapi,getapplicationproperties, getclicommand

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

debug=False
direct_only=False
valid_permissions=['read','update','delete','secure','add','remove','create']
default_permissions=['read','update','delete','secure','add','remove']
#direct_permission_suffix=u"\u2666" #Black diamond suit symbol - ok in stdout, seems to cause problems with other tools
direct_permission_suffix='*'


# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print (exception_type.__name__, exception)

sys.excepthook = exception_handler

parser = argparse.ArgumentParser()
parser.add_argument("-f","--folderpath", help="Path to a Viya folder. You must specify either -f folderpath or -u objectURI.")
parser.add_argument("-u","--objecturi", help="Object URI. You must specify either -f folderpath or -u objectURI.")
parser.add_argument("-n","--name", help="Enter the name of the user or group to test.")
parser.add_argument("-t","--principaltype", help="Enter the type of principal to test: user or group.",choices=['user','group'])
parser.add_argument("-p","--printpath", action='store_true', help="Print the folder path in each row")
parser.add_argument("--header", action='store_true', help="Print a header row")
parser.add_argument("--direct_only", action='store_true', help="Show only explanations which include a direct grant or prohibit")
parser.add_argument("-l","--permissions_list", nargs="+", help="List of permissions, to include instead of all seven by default", default=default_permissions)
parser.add_argument("-c","--convey", help="Show conveyed permissions in results. True by default when folder path is specified. False by dfefault if Object URI is specified.",choices=['true','false'])
parser.add_argument("-d","--debug", action='store_true', help="Debug")
args = parser.parse_args()
path_to_folder=args.folderpath
objecturi=args.objecturi
name=args.name
principaltype=args.principaltype
printpath=args.printpath
header=args.header
direct_only=args.direct_only
permissions=args.permissions_list
conveyparam=args.convey
debug=args.debug

if path_to_folder and objecturi:
  raise Exception('You must specify either -f and a Viya folder path, or -u and an object URI, but not both.')
if path_to_folder is None and objecturi is None:
  raise Exception('You must specify either -f and a Viya folder path, or -u and an object URI. You may not specify both.')

if name and principaltype is None:
  raise Exception('If you specify a principal name, you must also specify a principal type which can be user or group.')
if principaltype and name is None:
  raise Exception('If you specify a principal type, you must also specify a principal name.')

for permission in permissions:
  if permission not in valid_permissions:
    raise Exception(permission+' is not the name of a permission. Valid permissions are: '+' '.join(map(str, valid_permissions)))

# Two ways this program can be used: for a folder, or for a URI.
if path_to_folder:
    getfolderid_result_json=getfolderid(path_to_folder)

    if (debug):
        print(getfolderid_result_json)


    if getfolderid_result_json[0] is not None:
        folder_uri=getfolderid_result_json[1]
        if (debug):
            print("Id  = "+getfolderid_result_json[0])
            print("URI = "+folder_uri)
            print("Path = "+getfolderid_result_json[2])

    explainuri=folder_uri
    resultpath=path_to_folder
    #Set convey to true, unless user overrode that setting and asked for false
    if(conveyparam is not None and conveyparam.lower()=='false'):
        convey=False
    else:
        convey=True

else:
    explainuri=objecturi
    # This tool explains the permissions of any object.
    # If the object is a folder, we expect the user to supply path_to_folder, and we find its ID
    # If the object is something else, we don't have the path to the object.
    # It might be possible to get the path to the object from it's ID, but I'm not sure if there is a universal way to do that.
    # If the object is a report, you can call e.g.
    #    /opt/sas/viya/home/bin/sas-admin --output text reports show-info -id 43de1f98-d7ef-4490-bb46-cc177f995052
    # And the folder is one of the results passed back. But that call uses the reports plug-in to sas-admin and
    # should not be expected to return the path to other objects.
    # Plus, some objects do not have a path: service endpoints, for example.
    # This is a possible area for future improvement.
    resultpath=objecturi
    #Set convey to false, unless user overrode that setting and asked for true
    if(conveyparam is not None and conveyparam.lower()=='true'):
        convey=True
    else:
        convey=False


#Use the /authorization/decision endpoint to ask for an explanation of the rules that are relevant to principals on this URI
#See Authorization API documentation in swagger at http://swagger.na.sas.com/apis/authorization/v4/apidoc.html#op:createExplanation
endpoint='/authorization/decision'
if name and principaltype:
    if(principaltype.lower()=='user'):
        endpoint=endpoint+'?additionalUser='+name
    else:
        endpoint=endpoint+'?additionalGroup='+name
method='post'
accept='application/vnd.sas.authorization.explanations+json'
content='application/vnd.sas.selection+json'
inputdata={"resources":[explainuri]}

decisions_result_json=callrestapi(endpoint,method,accept,content,inputdata)

#print(decisions_result_json)
#print('decisions_result_json is a '+type(decisions_result_json).__name__+' object') #decisions_result_json is a dict object
e = decisions_result_json['explanations'][explainuri]

#print('e is a '+type(e).__name__+' object') #e is a list object

# Print header row if header argument was specified
if header:
    if printpath:
        if convey:
            print('path,principal,'+','.join(map(str, permissions))+','+','.join(map('{0}(convey)'.format, permissions)))
        else:
            print('path,principal,'+','.join(map(str, permissions)))
    else:
        if convey:
            print('principal,'+','.join(map(str, permissions))+','+','.join(map('{0}(convey)'.format, permissions)))
        else:
            print('principal,'+','.join(map(str, permissions)))

principal_found=False

#For each principle's section in the explanations section of the data returned from the REST API call...
for pi in e:
    #print pi['principal']
    #We are starting a new principal, so initialise some variables for this principal
    outstr=''
    has_a_direct_grant_or_deny=False
    if printpath:
        outstr=outstr+resultpath+','
    # If a name and principaltype are provided as arguments, we will only output a row for that principal
    if name and principaltype:
        if 'name' in pi['principal']:
            if (pi['principal']['name'].lower() == name.lower()):
                principal_found=True
                outstr=outstr+pi['principal']['name']
                # Permissions on object
                for permission in permissions:
                    # Not all objects have all the permissions
                    # Note that some objects do have permissions which are not meaningful for that object.
                    # E.g. SASAdministrators are granted Add and Remove on reports, by an OOTB rule which grants SASAdministrators all permissions (including Add and Remove) on /**.
                    # Meanwhile, Add and Remove are not shown in the View or Edit Authotizations dialogs for reports in EV etc.
                    # So, while it may be correct for the /authorization/decisions endpoint to explain that SASAdministrators are granted Add and Remove on a report,
                    # that does not alter the fact that in the context of a report, Add and Remove permissions are not meaningful.
                    if pi[permission.lower()]:
                        # This permission was in the expanation for this principal
                        outstr=outstr+','+pi[permission.lower()]['result']
                        if 'grantFactor' in pi[permission.lower()]:
                            if 'direct' in pi[permission.lower()]['grantFactor']:
                                if pi[permission.lower()]['grantFactor']['direct']:
                                    has_a_direct_grant_or_deny=True
                                    outstr=outstr+direct_permission_suffix
                    else:
                        # This permission was absent from the expanation for this principal
                        outstr=outstr+','
                # Conveyed permissions
                if convey:
                    for permission in permissions:
                        # Only a few objects have conveyed permissions at all
                        if 'conveyedExplanation' in pi[permission.lower()]:
                            # This permission was in the expanation for this principal
                            outstr=outstr+','+pi[permission.lower()]['conveyedExplanation']['result']
                            if 'grantFactor' in pi[permission.lower()]['conveyedExplanation']:
                                if 'direct' in pi[permission.lower()]['conveyedExplanation']['grantFactor']:
                                    if pi[permission.lower()]['conveyedExplanation']['grantFactor']['direct']:
                                        has_a_direct_grant_or_deny=True
                                        outstr=outstr+direct_permission_suffix
                        else:
                            # This permission was absent from the expanation for this principal
                            outstr=outstr+','
                if direct_only:
                    if has_a_direct_grant_or_deny:
                        print(outstr)
                else:
                    print(outstr)
    # But if no name or principaltype are provided, we output all rows
    else:
        if 'name' in pi['principal']:
            outstr=outstr+pi['principal']['name']
        else:
            outstr=outstr+pi['principal']['type']
        # Permissions on object
        for permission in permissions:
            # Not all objects have all the permissions
            if pi[permission.lower()]:
                # This permission was in the expanation for this principal
                outstr=outstr+','+pi[permission.lower()]['result']
                if 'grantFactor' in pi[permission.lower()]:
                    if 'direct' in pi[permission.lower()]['grantFactor']:
                        if pi[permission.lower()]['grantFactor']['direct']:
                            has_a_direct_grant_or_deny=True
                            outstr=outstr+direct_permission_suffix
            else:
                # This permission was absent from the expanation for this principal
                outstr=outstr+','
        # Conveyed permissions
        if convey:
            for permission in permissions:
                # Not all objects have all the permissions
                if 'conveyedExplanation' in pi[permission.lower()]:
                    # This permission was in the expanation for this principal
                    outstr=outstr+','+pi[permission.lower()]['conveyedExplanation']['result']
                    if 'grantFactor' in pi[permission.lower()]['conveyedExplanation']:
                        if 'direct' in pi[permission.lower()]['conveyedExplanation']['grantFactor']:
                            if pi[permission.lower()]['conveyedExplanation']['grantFactor']['direct']:
                                has_a_direct_grant_or_deny=True
                                outstr=outstr+direct_permission_suffix
                else:
                    # This permission was absent from the expanation for this principal
                    outstr=outstr+','
        if direct_only:
            if has_a_direct_grant_or_deny:
                print(outstr)
        else:
            print(outstr)
