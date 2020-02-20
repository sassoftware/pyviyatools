#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# creategroups.py
# Februar 2020
#
# create custom groups and add members using a csv file as input
# you can also add members to existing groups
#
# if the group already exists it will not be added and the http response is printed
# if the user does not exist it will not be added to the group and the http response is printed
# if the user is already a member of the group it will not be added to the group and the http response is printed
#
# none of the above conditions will prevent the processing of additional items in the csv
#
#
# Change History
#
# 03feb2020 Initial development
#
# Format of csv file is two columns
#  Column 1 group id 
#  Column 2 group name 
#  Column 3 is a description
#  Column 4 member id
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
parser = argparse.ArgumentParser(description="Create custom groups and establish membership")
parser.add_argument("-f","--file", help="Full path to csv file containing groups ",required='True')
args = parser.parse_args()
file=args.file

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

        for row in filecontents:
            
            #print(row)

            cols=len(row)

            id=row[0]
            newgroup=row[1]
            description=row[2]

            data = {}
            data["id"]=id
            data['name'] = newgroup
            data['description'] = description
            data["state"]="active"

            if id in groupslist:
                 print("Note: group with name "+newgroup+"  and id "+id+" already exists." )

            else:
               
                print ("Note: Trying to creating Group: "+newgroup )

                reqtype='post'
                reqval="/identities/groups/"

                myresult=callrestapi(reqval,reqtype,data=data,stoponerror=0)

                if myresult != None: print("Note: Group: "+newgroup+" created" )
                      
            # 4th column is group membership
            if cols>=4:
          
                member=row[3]
                print("Note: Trying to add user "+ member+ " to group "+newgroup )

                reqval="/identities/groups/"+id+"/userMembers/"+member
                reqtype='put'
                myresult=callrestapi(reqval,reqtype,data=data,stoponerror=0)
                if myresult != None: print("Note: user: "+member+" added to group "+newgroup )


else:
    print("ERROR: cannot read "+file)
        
