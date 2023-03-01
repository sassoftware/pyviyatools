#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# submit_jobreq.py
# August 2021
# March 2023 - Issue #137
#
# This function takes in the job id and verbose variables. id is the only required argument.
# based on the id, it will check to see, it will start the process of submitting the job
# in the jobmodule submit_job_request function.
#
# As the jobmodule waits for the job to finish, this script allows users to Ctrl + C out of the program by giving them
# a choice to either cancel the job or keep it running in the background.
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

import argparse
import logging
import os
import sys
import time
from datetime import datetime

from jobmodule import jobmodule


arguments = None
start_time = time.time()
parser = argparse.ArgumentParser(description="Submit Job using job definition")
parser.add_argument("-id",help="Provide Job Definition ID", action='store',required=True)
parser.add_argument("-v", "--verbose", help="Print Verbosity", action='store_true', default=False)
args = parser.parse_args()
try:

    profile = os.environ.get("SAS_CLI_PROFILE", "Default")
    x = jobmodule()

    # March 2023 - Issue #137 - It was incorrectly checking for a context which was not needed. 
    x.submit_job_request(id=args.id, verbose=args.verbose)


    print("=================================")
    print("Job Definition ID: {}".format(x.job_definition_id))
    print("Job Request ID: {}".format(x.job_requests_id))
    print("Job ID: {}".format(x.job_execution_id))
    print("Job Status: {}".format(x.sasjob_status))
    print("Job Status Details: {}".format(x.sasjob_status_details))
    print("Job Error Code: {}".format(x.sasjob_error_details))
    print("Job Log: {}".format(x.saslog_location))
    print("Job List: {}".format(x.sasout_location))
    print("Job Res: {}".format(x.sasres_location))
    print("=================================")

except KeyboardInterrupt as ke:
    job_continue = None
    if x.sasjob_status == "running":
        job_continue = input("Do you want to cancel job? [y/N]: ")
        while job_continue not in ['Y','y','N','n','']:
            job_continue = input("Do you want to cancel job? [y/N]: ")

        if job_continue in ['Y','y']:
            if x.cancel_job_uri is not None and x.cancel_job_method is not None:
                cancel_job_result = x.cancel_job()
                print("Result of Cancellation: {}".format(cancel_job_result))
                print("Job with id: {} has been cancelled!".format(x.job_execution_id))
                x.sasjob_status = "canceled"
        else:
            print ("Job is still running in the background with ID: {}".format(x.job_execution_id))

except Exception as e:
    print ("There was an unexpected error.")
    if x.sasjob_status == "running":
        print ("The job was still running when the error occured, please check REST API log and/or check the job.")
        x.sasjob_status = "failed"

    logging.error("Exception: ")
    logging.error(e)

finally:
    if x.sasjob_status_details is not None:
        print("Job {} with {}".format(x.sasjob_status,x.sasjob_status_details))
        if x.sasjob_error_details is not None:
            print("More details {}".format(x.sasjob_error_details))
    else:
        print("Job {}".format(x.sasjob_status))

    if x.sasjob_status == "failed" or x.sasjob_status == "canceled":
        sys.exit(1)
    if x.sasjob_status == "completed":
        if x.sasjob_status_details is None:
            if x.sasjob_status_details == "info":
                print ("Job has some information.")
                sys.exit(0)
        elif x.sasjob_status_details is not None:
            sys.exit(2)
