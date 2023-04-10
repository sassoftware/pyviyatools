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

echo "Show current tool setup"
${pyversion} showsetup.py
echo

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


echo "Show current tool setup"
${pyversion} showsetup.py
echo

echo "Test creategroups.py"

tee /tmp/migration_package_pvc.yaml > /dev/null <<EOF
"Custom Group ID","Custom Group Name / Persona","Notes/Comments","Azure AD Group (Members)"
"persona_platformadm_prd","Persona: PROD Platform Admin","","sas-viya-prod-platformadm"
"persona_datamgr_fraud_prd","Persona: PROD Data Manager – Fraud","","sas-viya-prod-datamgr-fraud"
EOF


echo "Test createfolders.py"

tee /tmp/createfolders.csv > /dev/null <<EOF
"/temporary","Temporary Folder for testing"
"/temporary/folder1",Folder1"
"/temporary/folder2","Folder2"
"/temporary/Création","French"
"/temporary/ÆØandÅ","Danish"
EOF


${pyversion} createfolders.py -f /tmp/createfolders.csv
echo

# remove folders that testing createdcall
${pyversion} deletefolder.py -f /temporary -q


echo "Test creategroups.py"

tee /tmp/creategroups.csv > /dev/null <<EOF
"Custom Group ID","Custom Group Name / Persona","Notes/Comments","Members"
"sas-viya-prod-test1","Test New group sas-viya-prod-test1","Add sasadm","sasadm"
"sas_viya_group1","Test nerw group sas_viya_group1","Add another group as member","sas-viya-prod-test1"
"Création","Création Group"
EOF

${pyversion} creategroups.py -f /tmp/creategroups.csv --skipfirstrow
echo

# delete the groups from the previous test
${pyversion} callrestapi.py -m delete -e /identities/groups/sas_viya_group1
${pyversion} callrestapi.py -m delete -e /identities/groups/sas-viya-prod-test1
${pyversion} callrestapi.py -m delete -e /identities/groups/Création
