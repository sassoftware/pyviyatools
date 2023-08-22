#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# validateviya.py
# September 2022
#
# ValidateViya runs a swath of tests on a Viya environment, validating that it is running as expected.
# ValidateViya is designed to be heavily modular, allowing for the creation of custom tests, the alteration
# of existing tests, and the removal of unneeded tests.
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
# Change History
#
# AUG2023 Fixed bug in order of columns for HTML output
#

from __future__ import print_function

import argparse
from sharedfunctions import callrestapi,printresult
import json
import os
import sys
import datetime

from jobmodule import jobmodule

#Used in place of printresults in scenarios where results are not itemized, making printresults unusuable
def specializedPrint(jsonData, outputStyle, cols):
    if(outputStyle == "json"):
        print(json.dumps(jsonData,indent=2))
    else:
        #Simple and simplejson -> remove "links" key from json
        if(jsonData.get("links") != None):
            jsonData.pop("links")
        #Simple output
        if(outputStyle=='simple'):
            #To mimic the existing structure:
            print("===== Item 0 =======")
            for key in list(jsonData):
                print(str(key) + " = " + str(jsonData[key]))
            #Again, mimicing existing structure
            print("Result Summary: Total items available: 1 Total items returned: 1")
        #Simplejson output
        elif(outputStyle=='simplejson'):
            print(json.dumps(jsonData,indent=2))
        else:
            #CSV -> remove all keys not found in cols param
            for key in list(jsonData):
                if key not in cols: del jsonData[key]
            #CSV output
            #Create our column row using cols list, to ensure ordering
            for index in range(len(cols)):
                if(index != len(cols) - 1):
                    print(cols[index],",",end="")
                else:
                    print(cols[index])

            #Create a row containing the corresponding result for each column
            for index in range(len(cols)):
                if(index != len(cols) - 1):
                    #Using .get(cols[index]) to ensure order matches the column row above
                    print('"'+str(jsonData.get(cols[index]))+'",',end="")
                else:
                    print('"'+str(jsonData.get(cols[index]))+'"')

#Simple helper method to print only if our user wants verbose printing
def verbosePrint(text, verbose):
    if(verbose):
        print(text)

#Allows command-line arguments
parser = argparse.ArgumentParser()
#Controls output type for data output
parser.add_argument("-o","--output", help="Output Style", choices=['csv', 'json', 'simple', 'simplejson', 'passfail', 'passfail-full', 'report', 'report-full'],default='csv')
#By including the flag -g, the test file will be created in the current directory, but if -g is not used, the test will not be generated at all
#It is also possible to use -g filename.json to give your test a custom name
parser.add_argument("-g","--generate-tests", dest="generateTestJson", help="Generate JSON Test Preferences File", nargs="?", const="/testPreferences.json", metavar="filename")
#There is no default file name to be read for -c, it must be entered manually
parser.add_argument("-c","--custom-tests", dest="customTests", help="Use a Custom Test Preferences File", nargs=1, type=argparse.FileType('r'), metavar="filename")
#Verbose parameter determines whether or not validateviya talks while running
parser.add_argument("-v", "--verbose", help="Add Output Verbosity", action="store_true")
#Silent parameter ensures that no text is printed besides results
parser.add_argument("-s", "--silent", help="Limit Output to Results Only", action="store_true")
#Output directory for instances where a file is outputted
parser.add_argument('-d',"--output-directory", dest="directory", help="Output Directory for Generated Files", metavar="directory")

args = parser.parse_args()
output_style=args.output
generateFile=args.generateTestJson
verbose = args.verbose
outputDirectory = args.directory

testPreferences = None
defaultNumTests = 8

# Create testPreferences json object from either custom or default tests
if(args.customTests is not None):
    if(args.generateTestJson is not None):
        print("You cannot generate and load custom tests at the same time")
        quit()
    try:
        #Read JSON file as a JSON object
        customPreferences = json.load(args.customTests[0])
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
            {"id":"0", "name":"Logged in User", "active":"True", "req":['/identities/users/@currentUser'], "cols":['name', 'id'], 'type':'Data Collection'},
            {"id":"1", "name":"List Users", "active":"True", "req":["/identities/users?limit=10000"], "cols":['name', 'id'], 'type':'Data Collection'},
            {"id":"2", "name":"List Base Folders", "active":"True", "req":['/folders/rootFolders?limit=10000'], "cols":['name','description'],'type':'Data Collection'},
            {"id":"3", "name":"List CAS Servers", "active":"True", "req":['/casManagement/servers?limit=10000'], "cols":['name','host','port','description'], 'type':'Data Collection'},
            {"id":"4", "name":"List CAS Server Metrics", "active":"True", "req":['/casManagement/servers/', '/metrics'], "reqVariable":"servers", "servers":[["cas-shared-default"]], "cols":['serverName','systemNodes','systemCores','cpuSystemTime','memory'], 'type':'Data Collection'},
            {"id":"5", "name":"List CAS Server Caslibs", "active":"True", "req":['/casManagement/servers/', '/caslibs?limit=10000'], "reqVariable":"servers", "servers":[["cas-shared-default"]], "cols":['name','scope','description'], 'type':'Data Collection'},
            {"id":"6", "name":"List CASLib Tables", "active":"True", "req":['/casManagement/servers/', '/caslibs/', '/tables?limit=10000'], "reqVariable":"caslibs", "caslibs":[["cas-shared-default", "systemData"]], "cols":['serverName','caslibName','name'], 'type':'Data Collection'},
            {"id":"7", "name":"Run Test SAS Code", "active":"True", "active":"True", "cols":['runSuccessful',"jobState"], "type":"Computation"}
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

            
        if(outputDirectory is not None):
            #create directory if it doesn't exist
            if not os.path.exists(outputDirectory):
                os.makedirs(outputDirectory)
        else: outputDirectory = os.getcwd()
        
       
        outputFile = outputDirectory
        outputFile = os.path.join(outputFile,generateFile)
        print(outputFile)
        f = open(outputFile, 'w')
        
        f.write(json.dumps(testPreferences, indent=2))

    except:
        print("JSON Test Preferences File cannot be written")
    finally:
        if f is not None:
            f.close()
    #We only want to generate the test file, not run tests
    quit()

if(args.silent):
    if(verbose):
        #Python doesn't know sign language yet
        print("You cannot be silent and verbose at the same time.")
        quit()

    #Sets standard output to a null file -> no output, effectively
    sys.stdout = open(os.devnull, 'w')

#Get active tests from library and split into data collection and computation tests
activeTests = [test for test in testPreferences['tests'] if test['active'] == "True"]
dataCollectionTests = [test for test in activeTests if test['type'] == "Data Collection"]
computationTests = [test for test in activeTests if test['type'] == "Computation"]
passingTests = []
failingTests = []

testStartTime = datetime.datetime.now()

#Run Data Collection Tests
for test in dataCollectionTests:
    print("Data Collection Test Started: " + test['name'])
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
                print("An error occurred running test " + str(test['id']))
                failingTests.append(test)
                #break out of the for loop, pushing us to the next test
                break
            else:
                #If things went well:
                test['results'].append(result)
                if(test not in passingTests):
                    passingTests.append(test)
    #In this case, there is only one request and, therefore, only one result
    else:
        request = test['req'][0]
        result = callrestapi(request, "get", stoponerror=False)
        if(result is None):
            print("An error occurred running test " + str(test['id']) + ": " + test['name'])
            failingTests.append(test)
        else:
            #If things went well:
            test['results'].append(result)
            passingTests.append(test)

#Run computation tests:
#Currently designed only for "Run Test SAS Code"
if(len(computationTests) == 1):
    #In the event of transformation into for loop, replace code below with for test in ...
    test = computationTests[0]
    test['results'] = []

    print("Computation Test Started: " + test['name'])
    #Get the job execution compute context:
    getComputeContextReq="/compute/contexts?filter=contains(name, 'Job Execution')"
    computeContext_result_json = callrestapi(getComputeContextReq, "get", stoponerror=False)
    if(computeContext_result_json is None):
        print("An error occurred running test " + str(test['id']))
        failingTests.append(test)
    else:
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
                passingTests.append(test)
            else:
                print("An error occurred running test " + str(test['id']) + ": " + test['name'])
                failingTests.append(test)
        finally:
            #We include this in a finally block just in case our session exists and
            #the test code fails - we want to close the session no matter what
            if(sessionId):
                #Close session: delete /sessions/SESSIONID
                closeSessionReq = "/compute/sessions/" + sessionId
                closeSession = callrestapi(closeSessionReq, "delete")
                verbosePrint("Compute session with session id " + sessionId + " closed successfully", verbose)

            test['results'].append(executeData_result_json)

testEndTime = datetime.datetime.now()
timeElapsed = testEndTime - testStartTime
verbosePrint('Tests Completed at ' + testEndTime.strftime("%H:%M:%S on %m/%d/%Y"), verbose)
verbosePrint("Time Elapsed: " + str(timeElapsed.seconds) + " seconds", verbose)

#Print Results:
#Turn back out stdout if silent
if(args.silent):
    sys.stdout = sys.__stdout__

#In the case of passfail output, we simply check to see if all of our tests
#ran successfully, if so, we return PASS, else FAIL
if(output_style == "passfail"):
    if(len(failingTests) != 0):
        print("FAIL")
    else:
        print("PASS")

    #To avoid unneeded indendation on the main print block, we just quit here
    quit()

if(output_style == "passfail-full"):
    passfail = {
        "count":len(activeTests),
        "tests":[]
    }
    for test in failingTests:
        passfail["tests"].append({"id":test.get("id"), "name":test.get("name"), "result":"FAIL"})
    for test in passingTests:
        passfail["tests"].append({"id":test.get("id"), "name":test.get("name"), "result":"PASS"})

    print(json.dumps(passfail,indent=2))

    #To avoid unneeded indendation on the main print block, we just quit here
    quit()

if(output_style == "report" or output_style == "report-full"):
    #Create the string containing our html code - start with head
    htmlStr = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>ValidateViya Test Report</title>\n</head>\n'
    #Style
    htmlStr += '<style>\nbody {font-family:"Open Sans", "Helvetica Neue", sans-serif;}\ntable {border-collapse: collapse;width: 70%;}\ntd, th {border: 1px solid #dddddd;text-align: left;padding: 8px;}</style>\n'
    #Title, summary start
    htmlStr += '<body>\n<main>\n<h1>ValidateViya Test Report</h1>\n<h2>Summary:</h2>\n'
    #All tests passing/some tests failing
    htmlStr += '<div style="font-size: large;">\n'
    if(len(failingTests) == 0):
        htmlStr += '<div style="color: green; font-weight: bold;">ALL TESTS PASSING</div>\n'
    else:
        htmlStr += '<div style="color: red; font-weight: bold;">SOME TESTS FAILING</div>\n'
    htmlStr += 'Tests Completed at ' + testEndTime.strftime("%H:%M:%S on %m/%d/%Y") + '<br>\n'
    htmlStr += str(len(passingTests)) + '/' + str(len(activeTests)) + ' Tests Ran Successfully<br>\n'
    htmlStr += "Testing Took " + str(timeElapsed.seconds) + " Seconds To Complete\n</div>"

    for test in dataCollectionTests:
        #Label our test, state whether it has passed or not
        htmlStr += "<hr>\n<h3>Test " + str(test['id']) + ": " + test['name'] + "</h3>\n"
        if(test in passingTests):
            htmlStr += '<div style="color: green; font-weight: bold;">Test Ran Successfully</div>\n'
        else:
            htmlStr += '<div style="color: red; font-weight: bold;">Test Failed</div>\n'

        #List items returned
        itemsReturned = 0
        for result in test['results']:
            #If there's an "items" parameter, we add the number of items to itemsReturned
            if('items' in result):
                itemsReturned += len(result['items'])
            else:
                #If not, we just increment by 1
                itemsReturned += 1

        htmlStr += str(itemsReturned) + ' item(s) returned</div>\n'

        #Create the table with the results only if the output style is report-full
        if(output_style == "report-full"):
            htmlStr += "<table>\n<thead>\n<tr>"
            
            columns=test['cols']

            for col in columns:
                htmlStr += "<th>" + col + "</th>"
            htmlStr += "</tr>\n</thead>\n"
            #print(htmlStr)

            for result in test['results']:
                #Create tbody
                htmlStr += '<tbody>\n<tr>\n'
                #Logic is similar to that of printresult/specialized print
                #If the 'items' key exists, we collect 1 or more rows of data from there
                #if it does not, we collect 1 row from result
                if('items' in result):
                    
                    #Remove all columns except those specified
                    for item in result['items']:
                        for key in list(item):
                            if key not in test['cols']: del item[key]
                    # #Create column row with labels
                    # for col in test['cols']:
                    #     htmlStr += "<th>" + col + "</th>\n"
                    # htmlStr += '</tr>\n'
                    # #Create a row for each result
                    for item in result['items']:
                        htmlStr += "<tr>\n"
                        for col in test['cols']:
                            htmlStr += "<td>" + str(item.get(col)) + "</td>\n"
                        htmlStr += "</tr>\n"
                else:

                    print(json.dumps(result,indent=2))
                    #Remove all columns except those specified
                    for key in list(result):
                        if key not in test['cols']: del result[key]
                    # #Create column row with labels
                    # for key in list(result.keys()):
                    #     htmlStr += '<th>' + key + '</th>\n'
                    # htmlStr += '</tr>\n'
                    #Create a row for each result
                    htmlStr += "<tr>\n"

                    print(json.dumps(result,indent=2))
                    
                    #sasgnn use the column name to get the value do not rely on the order
                    for resultvalue in columns: 
                        htmlStr += '<td>' + str(result[resultvalue]) + '</td>\n'                        

                    # for value in list(result.values()):
                    #     htmlStr += '<td>' + str(value) + '</td>\n'
                    htmlStr += '</tr>\n'
                    print(htmlStr)

                htmlStr += '</tbody>\n'
            htmlStr += "</table>"

    #Create table for computation tests:
    for test in computationTests:
        htmlStr += "<hr>\n<h3>Test " + str(test['id']) + ": " + test['name'] + "</h3>\n"
        if(test in passingTests):
            htmlStr += '<div style="color: green; font-weight: bold;">Test Ran Successfully</div>\n'
        else:
            htmlStr += '<div style="color: red; font-weight: bold;">Test Failed</div>\n'

        if(output_style == "report-full"):
            htmlStr += "<div style='margin: 0 auto;'><h4>Log:</h4>\n<div style='margin-left: 50px'>"
            for line in test['results'][0]['log']:
                htmlStr += line['line'] + '<br>\n'
            htmlStr += "</div></div>"


    #Create the html file to write
    try:
                    
        if(outputDirectory is not None):
            #create directory if it doesn't exist
            if not os.path.exists(outputDirectory):
                os.makedirs(outputDirectory)
        else: outputDirectory=os.getcwd()
               
        htmlFileName=os.path.join(outputDirectory,"report-" + testEndTime.strftime("%m.%d.%y-%H.%M.%S") + ".html")
        
        htmlFile = open(htmlFileName, "w")
        #Write to html file
        htmlFile.write(htmlStr)
        verbosePrint("NOTE: Report created at " + htmlFileName, verbose)

    except:
        print("ERROR: Problem creating report")
    finally:
        #Save html file
        if htmlFile is not None:
            htmlFile.close()
        quit()

#For standard output types:
for test in passingTests:
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