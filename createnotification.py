#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# create a viya notification
# notification is displayed in the UI in the notifications pane
#
# Change History
#

#
# Copyright © 2021, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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

# Create a notification

import argparse

# message is commented out at the moment because the EV ui does not display it
# level does not seem to make a difference to the UI either


from sharedfunctions import callrestapi

parser = argparse.ArgumentParser(description="Create a Viya Notification")
parser.add_argument("-s","--subject", help="Enter the subject.",required=True)
#parser.add_argument("-m","--message", help="Enter the message.",required=True)
parser.add_argument("-l","--level", help="Enter the level.",default='warn')

args = parser.parse_args()

n_subject=args.subject
#n_message=args.message
n_level=args.level

# build the rest call
reqval="/notifications/notifications"
reqtype="post"

# build the json parameters
data = {}
data['Subject'] = n_subject
data['Message'] = "Admin generated notification"
data['Level'] = n_level

# create the domain
callrestapi(reqval,reqtype,data=data)



