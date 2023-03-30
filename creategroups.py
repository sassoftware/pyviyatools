#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# creategroups.py
# Februar 2020
#
# create custom groups and add members using a csv file as input
# you can also add members to existing groups
#
# if the group already exists it will not be added
# if the user does not exist it will not be added to the group
# if the user is already a member of the group it will not be added to the group
#
# none of the above conditions will prevent the processing of additional items in the csv
#
#
# Change History
#
# 03feb2020 Initial development
# 30mar2023 Added some more error checking
# 30mar2023 Added -skipfirstrow for situations where first row is a header
#
# Format of csv file is two columns
#  Column 1 group id
#  Column 2 group name
#  Column 3 a description
#  Column 4 member id (groupid or userid)
#
# For example:
#group2,"Group 2","My Group 2"
#group3,"Group 3","My Group3",geladm
#group1,"Group 1","group 1"
#
# Copyright 2020, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
import argparse
import csv
import os
from sharedfunctions import callrestapi, getfolderid, file_accessible, getidsanduris

# setup command-line arguements
parser = argparse.ArgumentParser(description="Create custom groups and establish membership from csv: File Format: column1=groupid,column2=group name,column3=description,optional column4=memberid")
parser.add_argument("-f","--file", help="Full path to csv file containing groups ",required='True')
parser.add_argument("--debug", action='store_true', help="Debug")
parser.add_argument("--skipfirstrow", action='store_true', help="Skip the first row if it is a header")
args = parser.parse_args()
file=args.file
skipfirstrow=args.skipfirstrow
debug=args.debug

reqtype="post"

check=file_accessible(file,'r')

allgroups=callrestapi("/identities/groups","get")

# create a list of all groups

groupslist=[]

if 'items' in allgroups:

        total_items=allgroups['count']
        returned_items=len(allgroups['items'])

        for i in range(0,returned_items):

           groupslist.append(allgroups['items'][i]['id'])

# file can be read
if check:

    with open(file, 'rt') as f:

        filecontents = csv.reader(f)

        if skipfirstrow: next(filecontents,None)

        for row in filecontents:

            cols=len(row)

            # skip row and output a message if only 1 column
            if cols>1:

                # add a default description if only two columns
                if cols==2: row.append("Add by pyviyatools creategroups.py")

                id=row[0]
                newgroup=row[1]
                description=row[2]

                data = {}
                data["id"]=id
                data['name'] = newgroup
                data['description'] = description
                data["state"]="active"

                # if group does not exist add it
                if id in groupslist:
                    print("Note: group with name "+newgroup+"  and id "+id+" already exists." )
                else:
                    print ("Note: Trying to creating Group: "+newgroup )

                    reqtype='post'
                    reqval="/identities/groups/"

                    myresult=callrestapi(reqval,reqtype,data=data,stoponerror=0)

                    if myresult != None: print("Note: Group: "+newgroup+" created" )

                # 4th column is group membership either a userid or groupid, its optional.
                if cols>=4 and row[3] !="":

                    member=row[3]
                    print("Note: Trying to add user "+ member+ " to group "+newgroup )

                    #test that user exists
                    reqval="/identities/users/"+member
                    usertest=callrestapi(reqval,'get',noprint=1,stoponerror=0)

                    # user exists try to add to group, if user does not exist print a message
                    if usertest!=None:

                        reqval="/identities/groups/"+id+"/userMembers/"+member
                        reqtype='put'
                        myresult=callrestapi(reqval,reqtype,data=data,noprint=1,stoponerror=0)

                        if myresult != None: print("Note: user: "+member+" added to group "+newgroup )
                        else: print("Note: user: "+member+" is already a member of group "+newgroup )

                    else: print("WARNING: user: "+member+" does not exist and therefor cannot be added to group.")

            else: print("WARNING: too few columns in row, row must have at least two columns for group id and group.")

else:
    print("ERROR: cannot read csv file: "+file)

