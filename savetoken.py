#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Saves the access token from the CLI credentials file to a file in the format expected by the SAS Vscode extension
# The token is saved to a file ~/.sas/<profile>_token.txt 
#

import sys
import json
import os

from sharedfunctions import file_accessible, getprofileinfo 

 #get authentication information for the header
credential_file=os.path.join(os.path.expanduser('~'),'.sas','credentials.json')

# check that credential file is available and can be read
access_file=file_accessible(credential_file,'r')

if access_file==False:
    oaval=None
    print("ERROR: Cannot read authentication credentials at: ", credential_file)
    print("ERROR: Try refreshing your token with sas-admin auth login")
    sys.exit()

with open(credential_file) as json_file:
    data = json.load(json_file)
    
# profile

cur_profile=os.environ.get("SAS_CLI_PROFILE","NOTSET")

if cur_profile=="NOTSET":
    print("SAS_CLI_PROFILE environment variable not set, using Default profile")
    cur_profile='Default'
else:
    print("SAS_CLI_PROFILE environment variable set to profile "+ cur_profile)


ssl_file=os.environ.get("SSL_CERT_FILE","NOTSET")

if ssl_file=="NOTSET":
    print("SSL_CERT_FILE environment variable not set.")
else:
    print("SSL_CERT_FILE environment variable set to profile "+ ssl_file)


r_ssl_file=os.environ.get("REQUESTS_CA_BUNDLE","NOTSET")

if r_ssl_file=="NOTSET":
    print("REQUESTS_CA_BUNDLE environment variable not set.")
else:
    print("REQUESTS_CA_BUNDLE environment variable set to profile "+ r_ssl_file)

if cur_profile in data:

    oauthToken=data[cur_profile]['access-token']
    token_file=os.path.join(os.path.expanduser('~'),'.sas',cur_profile+"_token.txt")

    with open(token_file, "w") as tokenfile:
            tokenfile.write(oauthToken)
    
    print("NOTE: token saved to "+token_file)


