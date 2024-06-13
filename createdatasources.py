#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# createdatasource.py
# Copyright © 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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
# Format of CSV
#name,libref,path,description
#"test 2",test2,"/tmp","my second test"
#"test 3",test3,"/tmp","my 3 test"
#"test 4",test4,"/tmp","my 4 test"

import base64, argparse, sys, csv, json

from sharedfunctions import callrestapi, file_accessible

version=int(str(sys.version_info[0]))

if version==2:
    from io import open

parser = argparse.ArgumentParser(description="Create Compute Libraries (Data Sources1).")
parser.add_argument("-f","--file", help="CSV File containing Data Source Definitions",default="test.csv")
parser.add_argument("--skipfirstrow", action='store_false', help="Skip the first row if it is a header")
if version==2: parser.add_argument("--encoding",default="ascii",help="default is ascii for python2")
else: parser.add_argument("--encoding",default="utf-8",help="default is utf-8 for python3")

args = parser.parse_args()
file=args.file
encoding=args.encoding
skipfirstrow=args.skipfirstrow


#file=args.csvfile
file="/tmp/defs.csv"

check=file_accessible(file,'r')

# adds the data source definition to compute
# available as disconnected on all compute contexts

#dataSourceId="SAS Studio compute context"
providerId="Compute"

# file exists
if check:

   # open and read csv file 
   with open(file, 'rt',encoding=encoding,) as f:

        filecontents = csv.reader(f)
        print(filecontents)

        if skipfirstrow: next(filecontents,None)
        
        rownum=0
        # loop through the csv and add library definitions
        for row in filecontents:

            cols=len(row)
            name=row[0]

            if cols:
                data={}
                attrs={}
                options={}
                data['name'] = name
                data['providerId'] = providerId
                data['description'] = name + " created by pyviyatools"
                data['attributes'] = attrs
                data ["defaultLibref"]=row[1]
                #data ["dataSourceId"]=dataSourceId
                attrs['engineName'] = 'sase7'
                attrs['physicalName'] =  row[2]
                data['attributes'] = attrs
                
                # check if it exist for the provider and context before adding
                existresult=callrestapi("/dataSources/providers/Compute/sourceDefinitions/?filter=eq(name,'"+name+"')","get")

                if existresult["count"]:
                    print("WARNING: Library with name '"+name+"' already exists for compute server and will not be added.")   
                else:                    
                    print(json.dumps(existresult,indent=2))
                    rc=callrestapi("/dataSources/providers/Compute/sourceDefinitions",'post',data=data)

                    print("NOTE: Adding library: ", data)
                    #print(json.dumps(rc,indent=2))
            


