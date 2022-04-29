#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# jobmodule.py
# August 2021
#
# This module has the following functions in the folder.
# submit_job_definition is used by submit_jobdef.py to submit a job based on the job definition id. Depending if a
# corresponding job request was found for the job definition it would either call execute_job or would go to
# submit_job_request to create a new job request based on a default template in variable jobReq
#
# submit_job_request is used by submit_jobreq.py to submit a job based on job request id. If the call is coming from
# submit_job_definition then it will create a job request after which it will call execute_job.
#
# execute_job is called by both submit_job_definition and submit_job_request and is responsible for submitting the job.
#
# check_context verifies if the context provided by the user is the correct context, if it's not the program will error out
#
#
#
# NOTE: Above functions don't use callrestapi from the shared module, instead it makes requests calls.
# getauthtoken
# getbaseurl
# file_accessible
#
# There is another method called cancel_job, which allows users to manually cancel the job by pressing Ctrl + C on the
# keyboard.
#
#
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#  express or implied. See the License for the specific language governing permissions and limitations under the License.
#

import requests, sys, os, time, json
from sharedfunctions import callrestapi

class jobmodule:
    def __init__(self):
        self.head = {"Content-type": "application/json", "Accept": "application/json", "Authorization": jobmodule.getauthtoken(jobmodule.getbaseurl())}
        self.verbose = None
        self.sasjob_status = None
        self.sasjob_status_details = None
        self.saslog_location = None
        self.sasout_location = None
        self.sasres_location = None
        self.job_definition_id = None
        self.job_requests_id = None
        self.job_execution_id = None
        self.sasjob_error_details = None
        self.cancel_job_uri = None
        self.cancel_job_method = None



    def submit_job_definition(self, contextName="SAS Job Execution compute context", id=None, verbose=False):
        if verbose:
            self.verbose = True
        # jobID = "dbbc02b9-e191-4a0b-b549-388df207c933"
        # contextName = "SAS Job Execution compute context"
        self.job_definition_id = id
        jobID = id
        contextName = contextName
        jobDefinitionUri = "/jobDefinitions/definitions/" + jobID
        url = self.getbaseurl() + jobDefinitionUri
        result = requests.get(url=url, headers=self.head)
        if result.status_code == 404:
            print("ERROR! Job Definition ID is invalid. No Job Definition was found with id: {}".format(id))
            return
        print ("Job Definition id: {}".format(id))
        if self.verbose:
            print ("Checking Response IDs associated with the job definition id.")
        name = result.json()['name']
        desc = result.json()['name'].strip() + " created by: " + os.getlogin() + " using pyviyatools"
        url = self.getbaseurl() + "/jobExecution/jobRequests?filter=in('jobDefinitionUri','{}')&sortBy=modifiedTimeStamp:descending".format(jobDefinitionUri)
        result = requests.get(url=url,headers=self.head)
        count = result.json()['count']
        if count == 0:
            if self.verbose:
                print ("No Job Responses were found associated to the job request. Creating new job request")
            jobReq = {
                "name": name,
                "description": desc,
                "jobDefinitionUri": jobDefinitionUri,
                "arguments": {
                    "_contextName": contextName,
                    "_omitJsonLog": "true"
                }
            }

            url = self.getbaseurl() + "jobExecution/jobRequests"
            self.submit_job_request(url=url, data=jobReq)
        elif count >= 1:
            if self.verbose:
                print ("Job Request Found using job request id {}".format(result.json()['items'][0]['id']))
            self.job_requests_id = result.json()['items'][0]['id']
            for links in result.json()['items'][0]['links']:
                if links['rel'] == 'submitJob':
                    jobSubmitURI = links['uri']
                    url = self.getbaseurl() + jobSubmitURI
                    self.execute_job(url=url)

    def submit_job_request(self, id=None, job_req_json=None, verbose=False):
        if verbose:
            self.verbose = verbose
        if id is not None:
            self.job_requests_id = id
            if self.verbose:
                print ("Checking if the job request id {} is valid".format(id))
            url = self.getbaseurl() + "/jobExecution/jobRequests/{}".format(id)
            result = requests.get(url=url,headers=self.head)
            if result.status_code == 404:
                print("ERROR! Job Request ID is invalid. No Job Request was found with id: {}".format(kwargs['jobID']))
                sys.exit(1)
            print ("Job Request id {} is found.")
            for result in result.json()['links']:
                if result['rel'] == 'submitJob':
                    submit_job_uri = self.getbaseurl() + result['uri']
                    self.execute_job(url=submit_job_uri)
        elif job_req_json is not None:
            if self.verbose:
                print ("Submitting a new job request.")
            url = self.getbaseurl() + "/jobExecution/jobRequests"
            result = requests.post(url=url,data=job_req_json,headers=self.head)
            print ("New Job Request has been created. {}".format(result.json()['id']))
            self.job_requests_id = result.json()['id']
            for links in result.json()['links']:
                submit_job_url = self.getbaseurl() + links['uri'].strip()
                self.execute_job(url=submit_job_url)

    def execute_job(self, url):
        sasout_loc = None
        saslog_loc = None
        sasresinfo = None
        job_error_details = None
        job_status_details = None
        jobStatusURI = None
        result = requests.post(url=url, headers=self.head)
        print ("Job Submitted.")
        print ("Job id: {} \nState: {}".format(result.json()['id'],result.json()['state']))
        for links in result.json()['links']:
            if links['rel'] == 'self':
                jobStatusURI = links['uri']
                url = self.getbaseurl() + jobStatusURI
            if links['rel'] == 'updateState':
                self.cancel_job_uri = links['uri'] + "?value=canceled"
                self.cancel_job_method = links['method']

                print ("Get Job Results > {}".format(url))
                result = requests.get(url=url, headers=self.head)
        while result.json()['state'] == 'running':
            time.sleep(0.01)
            url = self.getbaseurl() + jobStatusURI
            result = requests.get(url=url,headers=self.head)

        url = self.getbaseurl() + jobStatusURI
        result = requests.get(url=url,headers=self.head)
        job_status = result.json()['state']
        if 'stateDetails' in result.json():
            print ("Job {} with {}".format(job_status,job_status_details))
            job_status_details = result.json()['stateDetails']
        else:
            print ("Job {}".format(job_status))

        if 'error' in result.json():
            job_error_details = json.dumps(result.json()['error'])
        if 'results' in result.json():
            computeJob = result.json()['results']['COMPUTE_JOB']
            if computeJob + ".list" in result.json()['results']:
                sasout_loc = result.json()['results'][computeJob + ".list.txt"]
            saslog_loc = result.json()['logLocation']
            sasresinfo = json.dumps(result.json()['results'])

        self.sasjob_status = job_status
        self.sasjob_status_details = job_status_details
        self.saslog_location = saslog_loc
        self.sasout_location = sasout_loc
        self.sasres_location = sasresinfo
        self.sasjob_error_details = job_error_details

    def cancel_job(self):
        if self.sasjob_status == "running":
            result = callrestapi(self.cancel_job_uri, self.cancel_job_method, acceptType="text/plain", contentType="text/plain")
            return result.text


    def check_context(self,contextName):
        context = ["SAS Job Execution compute context", "SAS Studio compute context"]
        if contextName not in context:
            print("Context provided, {} ,is not the default context".format(contextName))
            check_context_uri = self.getbaseurl() + "/compute/contexts?filter=eq('name','{}')".format(contextName)
            check_context_resp = requests.get(check_context_uri,headers=self.head)
            count = check_context_resp.json()['count']
            if count == 0:
                session_context_nf_uri = self.getbaseurl() + "/compute/contexts"
                session_context_nf_result = requests.get(session_context_nf_uri,headers=self.head)
                listOfNames = []
                for names in session_context_nf_result.json()['items']:
                    listOfNames.append(names['name'])
                print(
                        "Invalid Context Name. {} is not available in SAS Viya. Here is the list of valid context names {}".format(
                            contextName, listOfNames))
                sys.exit(1)

        return True


    @staticmethod
    def getauthtoken(baseurl):

        #get authentication information for the header
        credential_file=os.path.join(os.path.expanduser('~'),'.sas','credentials.json')

        # check that credential file is available and can be read
        access_file=jobmodule.file_accessible(credential_file, 'r')

        if access_file==False:
            oaval=None
            print("ERROR: Cannot read authentication credentials at: ", credential_file)
            print("ERROR: Try refreshing your token with sas-admin auth login")
            sys.exit()

        with open(credential_file) as json_file:
            data = json.load(json_file)
        type(data)

        # the sas-admin profile init creates an empty credential file
        # check that credential is in file, if it is add it to the header, if not exit

         # get the profile environment variable to use it
        # if it is not set default to the default profile

        cur_profile=os.environ.get("SAS_CLI_PROFILE","Default")

        #print("LOGON: ", cur_profile )

        if cur_profile in data:
            oauthToken=data[cur_profile]['access-token']
            oauthTokenType="bearer"
            oaval=oauthTokenType + ' ' + oauthToken

            if oauthToken == "":
                oaval = None
                print("ERROR: access token not in file: ", credential_file)
                print("ERROR: Try refreshing your token with sas-admin auth login")
                sys.exit()

        else:

            oaval=None
            print("ERROR: access token not in file: ", credential_file)
            print("ERROR: Try refreshing your token with sas-admin auth login")
            sys.exit()

        return oaval


    @staticmethod
    def getbaseurl():
        # check that profile file is available and can be read

        # note the path to the profile is hard-coded right now
        endpointfile=os.path.join(os.path.expanduser('~'),'.sas','config.json')
        access_file= jobmodule.file_accessible(endpointfile, 'r')

        #profile does not exist
        if access_file==False:
            print("ERROR: Cannot read CLI profile at:",endpointfile,". Recreate profile with sas-admin profile init.")
            sys.exit()

        #profile is empty file
        if os.stat(endpointfile).st_size==0:
             print("ERROR: Cannot read CLI profile empty file at:",endpointfile,". Recreate profile with sas-admin profile init.")
             sys.exit()

        # get json from profile
        with open(endpointfile) as json_file:
            data = json.load(json_file)

        # get the profile environment variable to use it
        # if it is not set default to the default profile

        cur_profile=os.environ.get("SAS_CLI_PROFILE","Default")
        #print("URL: ",cur_profile )

        # check that information is in profile
        if cur_profile in data:
            baseurl=data[cur_profile]['sas-endpoint']
        else:

            baseurl=None
            print("ERROR: profile "+cur_profile+" does not exist. Recreate profile with sas-admin profile init.")
            sys.exit()


        return baseurl

    @staticmethod
    def file_accessible(filepath, mode):

        try:
            f = open(filepath, mode)
            f.close()
        except IOError as e:
            return False

        return True
