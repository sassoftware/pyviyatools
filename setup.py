#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setup.py
# December 2020
#
# Updates the application.properties file with the location and name of the administration cli
# The default application properties stores the values for Viya 3.x
# This ensures bacward compatibility for Viya 3 users.
#
# sascli.location=/opt/sas/viya/home/bin/
# sascli.executable=sas-admin
#
# The defaults for the function are the Viya 4 values
#
# sascli.location=/opt/sas/viya/home/bin/
# sascli.executable=sas-viya
#
# As a result you only need to run setup.sh if you clone master and are using viya4
#
# .setup.py will set the default values for Viya 4
# OR
# ./setup.py --clilocation /opt/bin --cliexecutable sas-viya
#
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
# Import Python modules

import argparse, sys, os, inspect

from sharedfunctions import getapplicationproperties
from configobj import ConfigObj

# get python version
version=int(str(sys.version_info[0]))

# get input parameters
parser = argparse.ArgumentParser(description="Setup pyviyatools")
parser.add_argument("--clilocation", help="Enter the full path to the viya cli.",default="/opt/sas/viya/home/bin/")
parser.add_argument("--cliexecutable", help="Enter the name of the viya cli executable.", default="sas-viya")
args = parser.parse_args()

clilocation=args.clilocation
cliexecutable=args.cliexecutable

thepath=os.path.split(inspect.getsourcefile(lambda:0))
install_dir=thepath[0]
prop_file=os.path.join(install_dir, "application.properties")

print ("Note: updating "+prop_file)

dict={"sascli.location":clilocation,"sascli.executable":cliexecutable}

print("NOTE: configuration values set to ", dict )

config = ConfigObj(dict)
config.filename = prop_file

config.write()

