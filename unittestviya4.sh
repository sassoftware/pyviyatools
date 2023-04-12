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


tooldir=/opt/pyviyatools

while getopts :p:d:h: option
do
case "${option}"
in
p) pyversion=${OPTARG};;
d) tooldir=${OPTARG};;
h) usage=${OPTARG};;
   
esac
done

if [ ! "${pyversion}" ] || [ ! "${tooldir}" ]; then
  echo "arguments -p {python version} and -d {tool directory}"
  echo "$usage" >&2; exit 1
fi


echo NOTE: pyviyatools test tools in ${tooldir} using $pyversion

testdir=/tmp/pyviyatest
mkdir -p ${testdir}

cd ${tooldir}

echo "NOTE: Show current tool setup: ${pyversion} showsetup.py "
${pyversion} showsetup.py
echo


echo "NOTE: create a folder and sun-folders: ${pyversion} createfolders.py -f ${testdir}/createfolders.csv"

tee ${testdir}/createfolders.csv > /dev/null <<EOF
"/temporary","Temporary Folder for testing"
"/temporary/folder1",Folder1"
"/temporary/folder2","Folder2"
"/temporary/Création","French"
"/temporary/ÆØandÅ","Danish"
EOF


${pyversion} createfolders.py -f ${testdir}/createfolders.csv
echo

echo "NOTE: Pass the folder path and return the folder id and uri: ${pyversion} getfolderid.py -f /temporary"
${pyversion} getfolderid.py -f /temporary -o simplejson
echo

# create a report
parentfolder=/folders/folders/$(python3 getfolderid.py -f /temporary -o simplejson | jq -r .id)

tee ${testdir}/newreport1.json > /dev/null <<EOF
{
  "name": "pyviyatest Report 1",
  "description": "TEST New Description"
}
EOF

${pyversion} callrestapi.py -m post -e /reports/reports?parentFolderUri=${parentfolder}  -i ${testdir}/newreport1.json


# Create another report with French characters
parentfolder=/folders/folders/$(python3 getfolderid.py -f /temporary/folder1 -o simplejson | jq -r .id)

tee ${testdir}/newreport2.json > /dev/null <<EOF
{
  "name": "pyviyatest Création ",
  "description": "TEST New Description Création"
}
EOF

${pyversion} callrestapi.py -m post -e /reports/reports?parentFolderUri=${parentfolder}  -i ${testdir}/newreport2.json

# list the folders

echo "NOTE: Pass the folder path and return the folder id and uri: ${pyversion} getfolderid.py -f /temporary"
${pyversion} listcontent.py -f /temporary -o csv
echo

# remove folders that testing create


echo "NOTE: Create custom groups: ${pyversion} creategroups.py -f ${testdir}/creategroups.csv --skipfirstrow"

tee ${testdir}/creategroups.csv > /dev/null <<EOF
"Custom Group ID","Custom Group Name / Persona","Notes/Comments","Members"
"pyviyatest-group1","Group pyviyatest_group1 for pyviyatest","Add sasadm","sasadm"
"pyviyatest_group2","Group pyviyatest_group2 for pyviyatest","Add another group as member","pyviyatest-group1"
"pyviyatest_Création_group3","Group pyviyatest_Création_group3 for pyviyatest"
EOF

${pyversion} creategroups.py -f ${testdir}/creategroups.csv --skipfirstrow
echo

echo "NOTE: listgroups and members: ${pyversion} listgroupsandmembers.py"
${pyversion} listgroupsandmembers.py | grep pyviyatest
echo

echo "Return a set of configuration properties"
#${pyversion} getconfigurationproperties.py -c sas.identities.providers.ldap.user -o simple
echo


# Clean up temporary files and content

# echo "NOTE: delete temporary folder: {pyversion} deletefolder.py -f /temporary -q"
# ${pyversion} deletefolderandcontent.py -f /temporary -q


# # delete the groups from the previous test
# echo "NOTE: delete custom groups: ${pyversion} callrestapi.py -m delete -e /endpoint"
# ${pyversion} callrestapi.py -m delete -e /identities/groups/pyviyatest-group1
# ${pyversion} callrestapi.py -m delete -e /identities/groups/pyviyatest_group2
# ${pyversion} callrestapi.py -m delete -e /identities/groups/pyviyatest_Création_group3


rm -f ${testdir}