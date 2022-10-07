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
def specializedPrint(jsonData, outputStyle, cols):
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

#Allows command-line arguments
parser = argparse.ArgumentParser()
#Controls output type for data output
parser.add_argument("-o","--output", help="Output Style", choices=['csv','json','simple','simplejson', 'passfail'],default='csv')
#By including the flag -g, the test file will be created in the current directory, but if -g is not used, the test will not be generated at all
#It is also possible to use -g filename.json to give your test a custom name
parser.add_argument("-g","--generate-tests", dest="generateTestJson", help="Generate JSON Test Preferences File", nargs="?", type=argparse.FileType('w'), const=(os.getcwd() + "/testPreferences.json"), metavar="filename")
#There is no default file name to be read for -c, it must be entered manually
parser.add_argument("-c","--custom-tests", dest="customTests", help="Use a Custom Test Preferences File", nargs="?", type=argparse.FileType('r'), metavar="filename")
#Verbose parameter determines whether or not validateviya talks while running
parser.add_argument("-v", "--verbose", help="Add Output Verbosity", action="store_true")

args = parser.parse_args()
output_style=args.output
verbose = args.verbose

testPreferences = None
defaultNumTests = 8

# Create testPreferences json object from either custom or default tests
if(args.customTests is not None):
    try:
        #Read JSON file as a JSON object
        customPreferences = json.load(args.customTests)
    except:
        print("Custom Test Preferences File could not be read")
        quit()

    #Convert count to int
    numTests = int(customPreferences['count'])
    #Assure that the number of tests is equal to the actual number of tests
    assert(numTests == len(list(customPreferences['tests'])))

    #Assure the number of tests is default amount
    for i in range(0, numTests):
        #Assure each test has an id, counting up from 0 to numTests-1
        assert(int(customPreferences['tests'][i]['id']) == i)
        #Convert ids to int
        customPreferences['tests'][i]['id'] = int(customPreferences['tests'][i]['id'])
        #Assure each test contains the active parameter, either True or False
        assert(customPreferences['tests'][i].get('active') is not None)

    #Set the test preferences to those specificied in the file
    testPreferences = customPreferences
else:
    numTests = defaultNumTests
    #Create JSON object with default preferences
    defaultPreferences = {
        "tests":[
            {"id":"0", "name":"Logged in User", "req":['/identities/users/@currentUser'], "active":"True", "cols":['name', 'id'], 'type':'Data Collection'},
            {"id":"1", "name":"List Users", "req":["/identities/users?limit=10000"], "active":"True", "cols":['name', 'id'], 'type':'Data Collection'},
            {"id":"2", "name":"List Base Folders", "req":['/folders/rootFolders?limit=10000'], "active":"True", "cols":['name','description'],'type':'Data Collection'},
            {"id":"3", "name":"List CAS Servers", "req":['/casManagement/servers?limit=10000'], "active":"True", "cols":['name','host','port','description'], 'type':'Data Collection'},
            {"id":"4", "name":"List CAS Server Metrics", "req":['/casManagement/servers/', '/metrics'], "reqVariable":"servers", "servers":[["cas-shared-default"]], "active":"True", "cols":['serverName','systemNodes','systemCores','cpuSystemTime','memory'], 'type':'Data Collection'},
            {"id":"5", "name":"List CAS Server Caslibs", "req":['/casManagement/servers/', '/caslibs?limit=10000'], "reqVariable":"servers", "servers":[["cas-shared-default"]], "active":"True", "cols":['name','scope','description'], 'type':'Data Collection'},
            {"id":"6", "name":"List CASLib Tables", "req":['/casManagement/servers/', '/caslibs/', '/tables?limit=10000'], "reqVariable":"caslibs", "caslibs":[["cas-shared-default", "systemData"]], "active":"True", "cols":['name','rowCount'], 'type':'Data Collection'},
            {"id":"7", "name":"Run Test SAS Code", "active":"True", "cols":['runSuccessful',"jobState"], "type":"Computation"}
        ],
        "count":numTests
    }
    #Set the test preferences to the default values
    testPreferences = defaultPreferences

# If -g flag is on, generate the test json and write to file
# If -g and -c are used, the generated test json will be a copy of the one loaded in
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

#Get active tests from library and split into data collection and computation tests
activeTests = [test for test in testPreferences['tests'] if test['active'] == "True"]
dataCollectionTests = [test for test in activeTests if test['type'] == "Data Collection"]
computationTests = [test for test in activeTests if test['type'] == "Computation"]

#Special case: by setting the output type to "passfail", the tests are limited to just
#computation tests, as these will be a simple way to validate viya.
if(output_style == "passfail"):
    activeTests = computationTests
    dataCollectionTests = []

#Run Data Collection Tests
for test in dataCollectionTests:
    verbosePrint("Data Collection Test Started: " + test['name'], verbose)
    test['results'] = []
    #If there is a request variable, that means there could be more than one request for
    #the given test, resulting in the need for a for loop
    if(test.get('reqVariable') is not None):
        #the key "reqVariable" points to the key inside test that contains the variable used
        #in the api request
        reqVariables = test[test['reqVariable']]
        for variables in reqVariables:
            request = ""
            for i in range(len(test['req'])):
                request += test['req'][i]
                #Being that the varaibles list should have len = len(test['req']) - 1,
                #this ensures that there is no attempt to access an out-of-bounds index
                if(i < len(variables)):
                    request += variables[i]

            #Error checking: if our request fails, we remove the test from activeTests (so it
            #is not printed with sucessful results) and move onto the next test
            result = callrestapi(request, "get", stoponerror=False)
            if(result is None):
                verbosePrint("An error occurred running test " + str(test['id']), verbose)
                activeTests.remove(test)
                #break out of the for loop, pushing us to the next test
                break
            else:
                #If things went well:
                test['results'].append(result)
    #In this case, there is only one request and, therefore, only one result
    else:
        request = test['req'][0]
        result = callrestapi(request, "get", stoponerror=False)
        if(result is None):
            verbosePrint("An error occurred running test " + str(test['id']) + ": " + test['name'], verbose)
            activeTests.remove(test)
        else:
            #If things went well:
            test['results'].append(result)

#Run computation tests:
#Currently designed only for "Run Test SAS Code"
if(len(computationTests) == 1):
    #In the event of transformation into for loop, replace code below with for test in ...
    test = computationTests[0]
    test['results'] = []

    verbosePrint("Computation Test Started: " + test['name'], verbose)
    #Get the job execution compute context:
    getComputeContextReq="/compute/contexts?filter=contains(name, 'Job Execution')"
    computeContext_result_json = callrestapi(getComputeContextReq, "get")
    contextId = computeContext_result_json['items'][0]['id']

    verbosePrint("Compute Context Found with id: " + contextId, verbose)
    #Create a compute session for the test code:
    createSessionReq="/compute/contexts/" + contextId + "/sessions"
    newSession = callrestapi(createSessionReq, "post")
    sessionId = newSession['id']

    verbosePrint("Compute Session Created with id: " + sessionId, verbose)

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

        verbosePrint("Code Executed", verbose)
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
        verbosePrint("Code Has Completed Execution with State: " + jobState, verbose)
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
            verbosePrint("Compute session with session id " + sessionId + " closed successfully", verbose)

        test['results'].append(executeData_result_json)

#Print Results:

#In the case of passfail output, we simply check to see if all of our tests
#ran successfully, if so, we return PASS, else FAIL
if(output_style == "passfail"):
    runSuccessful = True
    for test in activeTests:
        for result in test['results']:
            if(result['runSuccessful'] == False):
                runSuccessful = False
                break
        #If we break in the inner for loop, we want to break the outer, as well
        else:
            continue
        break

    if(runSuccessful):
        print("PASS")
    else:
        print("FAIL")

    #To avoid unneeded indendation on the main print block, we just quit here
    quit()

#For standard output types:
for test in activeTests:
    #Verbose print the name, id of our test:
    testName = test['name']
    verbosePrint("\nTest " + str(test['id']) + ": " + testName, verbose)
    #For each test that we ran, go through the results
    for i in range(len(test['results'])):
        #If there is a request variable, verbose print it
        if('reqVariable' in test):
            reqVar = test['reqVariable']
            verbosePrint((reqVar + ":" + str(test[reqVar][i])), verbose)
        #If there is not an items key inside the results, we have to use specializedPrint
        #if there is we can just use printresult
        if not "items" in test['results'][0]:
            specializedPrint(test['results'][i], output_style, test['cols'])
        else:
            printresult(test["results"][i], output_style, test['cols'])
