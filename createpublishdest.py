#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# createpublishdest.py
# feb 2019
#
# create a viya domain
#
# Change History
#
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

# Create a publishing destination

import argparse

from sharedfunctions import callrestapi


parent_parser = argparse.ArgumentParser(add_help=False)

parent_parser.add_argument("-d","--desc", help="Description",default="Created by pyviya")
parent_parser.add_argument("-n","--name", help="Enter the destination name.",required=True)
parent_parser.add_argument("-s","--server", help="CAS Server.",default="cas-shared-default",required=True)
parent_parser.add_argument("-c","--caslib", help="CASLIB.",required=True)

parser = argparse.ArgumentParser(description="Create a Publishing Destinations")

subparsers = parser.add_subparsers(help='Type of Destination',dest="type")

cas_parser=subparsers.add_parser("cas",help="CAS destination",parents=[parent_parser])

cas_parser.add_argument("-t","--table", help="Table",required=True)

hadoop_parser=subparsers.add_parser("hadoop",help="Hadoop destination",parents=[parent_parser])

hadoop_parser.add_argument("-hd","--hdfsdir", help="HDFS Directory",required=True)


teradata_parser=subparsers.add_parser("teradata",help="Teradata Destination",parents=[parent_parser])

teradata_parser.add_argument("-db","--dbcaslib", help="Database Caslib",required=True)
teradata_parser.add_argument("-dt","--table", help="Destination Table",required=True)


args = parser.parse_args()

publish_name=args.name
publish_type=args.type
desc=args.desc
server=args.server
caslib=args.caslib

# build the json parameters
data = {}

data['name'] = publish_name
data['description'] = desc
data['destinationType'] = publish_type
data['casServerName'] = server
data['casLibrary'] = caslib


if args.type=="cas":

   table=args.table
   data['destinationTable'] = table


elif args.type=="hadoop":
   hdfsdir=args.hdfsdir
   data['hdfsDirectory'] = hdfsdir

elif args.type=='teradata':
   dbcaslib=args.dbcaslib
   table=args.table
   data['databaseCasLibrary'] = dbcaslib
   data['destinationTable'] = table

# build the rest call
reqval="/modelPublish/destinations/"
reqtype="post"


# create the domain
callrestapi(reqval,reqtype,acceptType='application/vnd.sas.models.publishing.destination+json',contentType='application/vnd.sas.models.publishing.destination+json',data=data)

print("NOTE: destination created with the following parameters")
print(data)

