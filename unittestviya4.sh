#!/usr/bin/sh
#
# unittestviya4.sh
# April 2023
#
# Calls some of the pyviyatools at least once, as a simple unit/integration test
#
#
#
# Copyright 2023, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

pyversion=python3
tooldir=/opt/pyviyatools

echo pyviyatools test using $pyversion

cd ${tooldir}

# echo "Return the json for all the identities"
# ${pyversion} callrestapi.py -e /identities/identities -m get
# echo

echo "Pass the folder path and return the folder id and uri"
${pyversion} getfolderid.py -f /Public
echo

# echo "Delete a folder based on its path - we don't want to delete a real folder, so try (and fail) to delete one which does not exist" 
# ${pyversion} deletefolder.py -f /this_folder_does_not_exist
# echo

# echo "Delete a folder and its content - we don't want to delete a real folder, so try (and fail) to delete one which does not exist" 
# ${pyversion} deletefolderandcontent.py -f /this_folder_does_not_exist
# echo

echo "Return a set of configuration properties"
${pyversion} getconfigurationproperties.py -c sas.identities.providers.ldap.user
echo


