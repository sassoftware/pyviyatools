#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# createbinarybackup.py
# February 2018
#
# Usage:
# python createbinarybackup.py [-q] [-d]
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

from sharedfunctions import callrestapi, getapplicationproperties
import argparse
import json
import sys
import os

# get python version
version=int(str(sys.version_info[0]))

# get cli location from properties
propertylist=getapplicationproperties()

clidir=propertylist["sascli.location"]
cliexe=propertylist["sascli.executable"]

clicommand=os.path.join(clidir,cliexe)


debug=False
defaultBackupScheduleName="DEFAULT_BACKUP_SCHEDULE"
newScheduleName="BINARY_BACKUP_SCHEDULE"
newScheduleDesc="JobRequest to execute a binary backup"
jobDefinitionURIStem="/jobDefinitions/definitions/"
newScheduleContentType="application/vnd.sas.backup.request+json" # For a single-tenant deployment
#newScheduleContentType="application/vnd.sas.backup.deployment.request+json" # For a multi-tenant deployment

# Define exception handler so that we only output trace info from errors when in debug mode
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print (exception_type.__name__, exception)

sys.excepthook = exception_handler

parser = argparse.ArgumentParser()
#parser.add_argument("-t","--principaltype", help="Enter the type of principal to test: user or group.",required='True',choices=['user','group'])
parser.add_argument("-q","--quiet", action='store_true')
parser.add_argument("-d","--debug", action='store_true')
args = parser.parse_args()
#principaltype=args.principaltype
quiet=args.quiet
debug=args.debug

# STEP 1 of 4: Get the jobDefinition of the existing DEFAULT_BACKUP_SCHEDULE

endpoint='/jobDefinitions/definitions?limit=20&filter=in(name,"'+defaultBackupScheduleName+'")'
method='get'
accept='application/json'

jobDefinition_json=callrestapi(endpoint,method,accept)
if debug:
    print('jobDefinition_json:')
    print(jobDefinition_json)

jobDefinitions=jobDefinition_json['items']
id_found=False
jobDefinitionId=''
for jobDefinition in jobDefinitions:
    if jobDefinition['name']:
        if(jobDefinition['name']==defaultBackupScheduleName):
            jobDefinitionId=jobDefinition['id']
            print('Id: '+jobDefinitionId)
            id_found=True

if not id_found:
    raise Exception('Unable to determine Id for '+defaultBackupScheduleName+'.')

# STEP 2 of 4: Create a jobExecution request

endpoint='/jobExecution/jobRequests'
method='post'
accept='application/vnd.sas.job.execution.job.request+json'
content='application/vnd.sas.job.execution.job.request+json'
inputdata={
  "name": newScheduleName,
  "description": newScheduleDesc,
  "jobDefinitionUri": jobDefinitionURIStem+jobDefinitionId,
  "arguments": {
                    "contentType": newScheduleContentType,
                    "backupType": "binary"
  }
}

jobExecutionRequest_json=callrestapi(endpoint,method,accept,content,inputdata)
if debug:
    print('jobExecutionRequest_json:')
    print(jobExecutionRequest_json)

# STEP 3 of 4: Get the href to submit the job from the create jobExecution response

links=jobExecutionRequest_json['links']
href_found=False
submitJobHref=''
for link in links:
    if link['rel']:
        if(link['rel']=="submitJob"):
            submitJobHref=link['href']
            print('Href: '+submitJobHref)
            href_found=True

if not href_found:
    raise Exception('Unable to find the href for the submitJob link.')

# STEP 4 of 4: Submit the jobExecution request

endpoint=submitJobHref
method='post'
accept='application/vnd.sas.job.execution.job+json'

submitJob_json=callrestapi(endpoint,method,accept)
#if debug:
print('submitJob_json:')
print(submitJob_json)
