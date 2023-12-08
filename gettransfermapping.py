#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# November 2022
#
# pass in a mapping set name and download to a mapping file for use with the Viya CLI
#
# Change History
#
# 06NOV2022 Initial Development
#
#
# Copyright © 2022, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
from __future__ import print_function
import argparse, json, os, sys

from sharedfunctions import callrestapi, printresult, getidsanduris

parser = argparse.ArgumentParser(description="Create a JSON Mapping File from a Viya Mapping Set.")
parser.add_argument("-n","--name", help="Name of the Mapping Set (also the name of the output file).",required='True',default='system')
parser.add_argument("-d","--directory", help="Directory where mapping files are written.",required='True')
parser.add_argument("--debug", action='store_true', help="Debug")
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')

# get python version
version=int(str(sys.version_info[0]))

args = parser.parse_args()
mapname=args.name
debug=args.debug
basedir=args.directory
quietmode=args.quiet

# prompt if directory exists because existing json files are deleted
if os.path.exists(basedir):

    # if the quiet mode flag is not passed then prompt to continue
    if not quietmode:

        if version  > 2:
            areyousure=input("The folder exists any existing json files in it will be deleted. Continue? (Y)")
        else:
            areyousure=raw_input("he folder exists any existing json files in it will be deleted. Continue? (Y)")
    else:
        areyousure="Y"
else: areyousure="Y"

# prompt is Y if user selected Y, its a new directory, or user selected quiet mode
if areyousure.upper() =='Y':

    # get all transfer mapping sets
    reqval="/transfer/mappings"
    if debug : print(reqval)

    originaljson=callrestapi(reqval,'get')
    #if debug: printresult(originaljson,output_style)

    allmaps={}

    #get id of selected mapping set
    #because filter by name does not work on previous REST call

    if 'items' in originaljson:

        maps=originaljson["items"]

        found=0
        for map in maps:

            if map["name"]==mapname:

                idformap=map["id"]
                found=1
                break

    if found: print("NOTE: Mapping set "+mapname+" with id "+idformap+" selected." )
    else:
        print("ERROR: Mapping set with name "+mapname+" not found.")
        print("NOTE: list mapping sets with './callrestapi.py -m get -e /transfer/mappings -o csv' ")
        sys.exit()

    reqvalbase="/transfer/mappings/"+idformap

    # get options
    # currently mapping sets do not contain options :(
    reqval=reqvalbase+"/options"
    options=callrestapi(reqval,'get')

    # get substitutions
    reqval=reqvalbase+"/substitutions"
    substitutions=callrestapi(reqval,'get')

    # reformat substitutions into list of dictionaries for mapping file
    new_substitutions=[]

    if 'items' in substitutions:

        allitems=substitutions["items"]

        for asub in allitems:

            thisdict={}

            thisdict["resourceId"]=asub["contentSourceLocation"]
            thisdict["resourceName"]=asub["name"]

            props=asub["mapSubstitutionProperties"]

            #remove id from properties list
            for aproperty in props:

                discard=aproperty.pop("id","notfound")

            thisdict["properties"]=props

            new_substitutions.append(thisdict)


    # get mappings or connectors
    reqval=reqvalbase+"/items"
    connectors=callrestapi(reqval,'get')
    #if debug: print(json.dumps(connectors,3))

    # reformat connector (Data Resources in the UI) into a list of connectors for each TYPE
    new_connectors={}

    tables=[]
    users=[]
    usergroups=[]

    if 'items' in connectors:

            allconnectors=connectors["items"]
            for connection in allconnectors:

                newconnection={}
                newconnection["resourceName"]=connection["name"]
                newconnection["target"]=connection["mapTargetProperties"][0]["value"]
                newconnection["source"]=connection["mapSourceProperties"][0]["value"]

                # upcase comparison as it seems to be inconsistent
                type=connection["type"].upper()
               
                if type.upper()=="TABLE":
                    tables.append(newconnection)
                    
                elif type=="UserGroup":
                    usergroups.append(newconnection)
                elif type=="User":
                    users.append(newconnection)

            new_connectors["Table"]=tables
            new_connectors["User"]=users
            new_connectors["UserGroup"]=usergroups

    # Create mapping file and write to the file-system

    m_json={'version':1}

    m_json["connectors"]=new_connectors
    m_json["substitutions"]=new_substitutions

    if not os.path.exists(basedir): os.makedirs(basedir)

    filecontent=json.dumps(m_json,indent=2)
    file=mapname+'.json'
    filename=os.path.join(basedir,file)

    with open(filename, "w") as outfile:
        outfile.write(filecontent)

    print("NOTE: Mapping set "+mapname+" output to file "+filename )
