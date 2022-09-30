#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# validateviya.py September 2022
#
# Validateviya an example of how easy it is to build a new tool. This tool is not really needed as you can do this easily with the CLI
# it is here for demo purposes. It lists the caslibs and their details accepting the cas server as a parameter
#
#
# Change History
#
#
# Copyright © 2022, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#  express or implied. See the License for the specific language governing permissions and limitations under the License.
#

import argparse
from sharedfunctions import callrestapi,printresult
import json
import os

from jobmodule import jobmodule

#Used in place of printresults in scenarios where results are not itemized, making printresults unusuable
def specializedPrint(jsonData, cols, outputStyle):
    if(outputStyle == "json"):
        print(json.dumps(jsonData,indent=2))
    else:
        for key in list(jsonData):
            if key not in cols: del jsonData[key]
        if(outputStyle=='simple'):
            for key in list(jsonData):
                print ("====="+key+"=======")
                print (jsonData[key])
        elif(outputStyle=='simplejson'):
            print(json.dumps(jsonData,indent=2))
        else:
            for i in range(len(list(jsonData))):
                if(i != len(list(jsonData))-1):
                    print(list(jsonData)[i],",",end="")
                else:
                    print(list(jsonData)[i])

            for i in range(len(list(jsonData.keys()))):
                if(i != len(list(jsonData))-1):
                    print('"'+str(list(jsonData.items())[i][1])+'",',end="")
                else:
                    print('"'+str(list(jsonData.items())[i][1])+'"')

#Simple helper method to print only if our user wants verbose printing
def verbosePrint(text, verbose):
    if(verbose):
        print(text)

# setup command-line arguements. In this block which is common to all the tools you setup what parameters
# are passed to the tool
# the --output parameter is a common one which supports the three styles of output json, simple or csv

parser = argparse.ArgumentParser()
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson', 'passfail'],default='csv')
#By including the flag -g, the test file will be created in the current directory, but if -g is not used, the test will not be generated at all
#It is also possible to use -g filename.json to give your test a custom name
parser.add_argument("-g","--generate-tests", dest="generateTestJson", help="Generate JSON Test Preferences File", nargs="?", type=argparse.FileType('w'), const=(os.getcwd() + "/testPreferences.json"), metavar="filename")
#There is no default file name to be read for -c, it must be entered manually
parser.add_argument("-c","--custom-tests", dest="customTests", help="Use a Custom Test Preferences File", nargs="?", type=argparse.FileType('r'), metavar="filename")

args = parser.parse_args()
output_style=args.output

testPreferences = None
numTests = 8

if(args.customTests is not None):
    try:
        #Read JSON file as a JSON object
        customPreferences = json.load(args.customTests)
    except:
        print("Custom Test Preferences File could not be read")
        quit()

    #Verify preferences to be of correct form
    assert(int(customPreferences['count']) == numTests)
    #Convert count to int
    customPreferences['count'] = int(customPreferences['count'])

    for i in range(0, numTests):
        #Assure each test has an id, counting up from 1 to numTests
        assert(int(customPreferences['tests'][i]['id']) == i)
        #Convert ids to int
        customPreferences['tests'][i]['id'] = int(customPreferences['tests'][i]['id'])
        #Assure each test contains the key
        assert(customPreferences['tests'][i]['active'] is not None)

    #Set the test preferences to those specificied in the file
    testPreferences = customPreferences
else:
    #Create JSON object with default preferences
    defaultPreferences = {
        "tests":[
            {"id":"0", "name":"Logged in User", "active":"True"},
            {"id":"1", "name":"List Users", "active":"True"},
            {"id":"2", "name":"List Base Folders", "active":"True"},
            {"id":"3", "name":"List CAS Servers", "active":"True"},
            {"id":"4", "name":"List CAS Server Metrics", "servers":["cas-shared-default"], "active":"True"},
            {"id":"5", "name":"List CAS Server Caslibs", "servers":["cas-shared-default"], "active":"True"},
            {"id":"6", "name":"List CASLib Tables", "caslibs":[("cas-shared-default", "systemData")], "active":"True"},
            {"id":"7", "name":"Run Test SAS Code", "active":"True"}
        ],
        "count":numTests
    }
    #Set the test preferences to the default values
    testPreferences = defaultPreferences

if(args.generateTestJson is not None):
    #Write tests preferences JSON to file (default OR those specified via -c)
    try:
        args.generateTestJson.write(json.dumps(testPreferences, indent=2))
    except:
        print("JSON Test Preferences File cannot be written")
    finally:
        args.generateTestJson.close()

    #We only want to generate the test file, not run tests
    quit()

#Run tests:
#Important values:
defaultCAS = "cas-shared-default"
caslibs = ["systemData"]

#Requests used:
loggedInUserReq = '/identities/users/@currentUser'
listUsersReq = '/identities/users?limit=10000'
baseFoldersReq = '/folders/rootFolders?limit=10000'
listServersReq = '/casManagement/servers?limit=10000'
serverMetricsReq = '/casManagement/servers/' + defaultCAS + '/metrics'
serverCaslibsReq = '/casManagement/servers/' + defaultCAS + '/caslibs?limit=10000'
caslibTableReq = '/casManagement/servers/' + defaultCAS + '/caslibs/' + "systemData" + '/tables?limit=10000'

loggedInUser_result_json = callrestapi(loggedInUserReq, "get")
listUsers_result_json = callrestapi(listUsersReq, "get")
baseFolders_result_json = callrestapi(baseFoldersReq, "get")
listServers_result_json = callrestapi(listServersReq, "get")
serverMetrics_result_json = callrestapi(serverMetricsReq, "get")
serverCaslibs_result_json = callrestapi(serverCaslibsReq, "get")
caslibTable_result_json = callrestapi(caslibTableReq, "get")

#Columns printed for simple, simplejson, and csv output_style
loggedInUser_cols=['name', 'id']
listUsers_cols=['name', 'id']
baseFolders_cols=['name','description']
listServers_cols=['name','host','port','description']
serverMetrics_cols = ['serverName','systemNodes','systemCores','cpuSystemTime','memory']
serverCaslibs_cols = ['name','scope','description']
systemData_cols = ['name','rowCount']
executeData_cols=['runSuccessful',"jobState"]

#Run test code:
#Get the job execution compute context:
getComputeContextReq="/compute/contexts?filter=contains(name, 'Job Execution')"
computeContext_result_json = callrestapi(getComputeContextReq, "get")
contextId = computeContext_result_json['items'][0]['id']
#Create a compute session for the test code:
createSessionReq="/compute/contexts/" + contextId + "/sessions"
newSession = callrestapi(createSessionReq, "post")
sessionId = newSession['id']

#Keep it in a try loop to ensure we will always end our compute session
try:
    #Homemade json object for storing test code data:
    executeData_result_json = {"runSuccessful": False, "log": []}

    #Execute SAS code using our compute session:
    executeCodeReq="/compute/sessions/" + sessionId + "/jobs"
    #Our code uses proc print and proc cas:
    run_code_json = {
        "name":"Test SAS Code Request",
        "code":'proc print data=sashelp.class; run; cas casauto; proc cas; table.fetch table={name="zipcode.sashdat", caslib="AppData"}; run; quit; cas casauto terminate;',
    }
    executeCode = callrestapi(executeCodeReq, "post", data=run_code_json)
    #Get our job id from our job request:
    jobId = executeCode['id']

    #Get job state - we want to see if it ran successfully
    getJobStateReq="/compute/sessions/" + sessionId + "/jobs/" + jobId + "/state?wait=10"
    jobState = callrestapi(getJobStateReq, "get")
    #Continually check the job state until it is no longer running:
    while(jobState == "running"):
        jobState = callrestapi(getJobStateReq, "get")

    #Record our final job state:
    executeData_result_json['jobState'] = jobState

    #Get job log - can be used for debugging
    getJobLogReq="/compute/sessions/" + sessionId + '/jobs/' + jobId + "/log"
    getJobLog = callrestapi(getJobLogReq, "get")
    executeData_result_json['log'] = getJobLog['items']

    #If our code ran succesfully, we want to take note of that
    if(jobState == "completed"):
        executeData_result_json['runSuccessful'] = True
finally:
    #We include this in a finally block just in case our session exists and
    #the test code fails - we want to close the session no matter what
    if(sessionId):
        #Close session: delete /sessions/SESSIONID
        closeSessionReq = "/compute/sessions/" + sessionId
        closeSession = callrestapi(closeSessionReq, "delete")
        print("Compute session with session id " + sessionId + " closed successfully")

#Print our results:
print("Current user:")
specializedPrint(loggedInUser_result_json, loggedInUser_cols, output_style)
print("\nUsers:")
printresult(listUsers_result_json,output_style,listUsers_cols)
print("\nBase Folders:")
printresult(baseFolders_result_json,output_style,baseFolders_cols)
print("\nCAS Servers:")
printresult(listServers_result_json,output_style,listServers_cols)
print("\nDefault Server Metrics:")
specializedPrint(serverMetrics_result_json, serverMetrics_cols, output_style)
print("\nDefault Server Caslibs:")
printresult(serverCaslibs_result_json,output_style,serverCaslibs_cols)
print("\Caslib Tables:")
printresult(caslibTable_result_json,output_style,systemData_cols)
print("\nRun a Test Program:")
specializedPrint(executeData_result_json, executeData_cols, output_style)