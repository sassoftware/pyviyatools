#!/usr/bin/sh
#
# unittestsadm33.sh
# December 2018
#
# Calls each of the pyviyatools at least once, as a simple unit/integration test
#
# Some tests are provided with example folder paths which are not likely to
# exist in your deployment. However, most tests are not dependent on any
# custom content in the deployment, and will run well on any deployment.
#
# Some tests intentionally do things which do not work, e.g. delete a folder
# which does not exist. The error message returned by the tool called is
# considered sufficient to demonstrate that it has in fact been called, and is
# working as intended. If you like, you could create content for these tests
# to act on, e.g. create a folder called "/this_folder_does_not_exist", and
# allow one of the tests below delete it.
#
# The following tests create new content, and do not clean up after themselves:
# 1. "Create a domain using createdomain"
#    - creates or replaces domain named 'test', does not create multiple
#      copies
# 2. "Create a binary backup job"
#    - creates a new scheduled job named 'BINARY_BACKUP_JOB' each time it
#      runs, will create multiple copies
# You may wish to clean up after them manually, especially in a
# real customer environment. Study the tests and/or run them individually
# to learn more about what they create, so that you can find and delete it
# yourself. In a dev, PoC, playpen or classroom environment, the cleanup
# might be optional, as the created objects will not interfere with other
# content or work.
# 
# Change History
#
# 01Jun2018 Initial version after refactoring tools
# 18Oct2018 updated gerrulid test because -o changed to -u 
# 03Dec2018 Added tests for explainaccess.py
#
#
# Copyright 2018, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
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


echo "Return all the rest calls that can be made to the folders endpoint"
./callrestapi.py -e /folders -m get
echo

echo "Return the json for all the folders/folders"  
./callrestapi.py -e /folders/folders -m get
echo

echo "Return simple text for all the folders/folders"
./callrestapi.py -e /folders/folders -m get -o simple
echo

echo "Rest calls often limit the results returned the text output will tell you returned and total available items" 
echo "in this call set a limit above the total items to see everything"
./callrestapi.py -e /folders/folders?limit=500 -m get -o simple
echo

echo "Return the json for all the identities"
./callrestapi.py -e /identities/identities -m get
echo

echo "Return the json for all the identities output to a file"
./callrestapi.py -e /identities/identities -m get > /tmp/identities.json
echo
echo "Contents of /tmp/identities.json:"
cat /tmp/identities.json
echo "End of contents of /tmp/identities.json"
echo
echo "Deleting /tmp/identities.json"
rm /tmp/identities.json
echo "Demonstrating that /tmp/identities.json has been deleted - list it, ls should say no such file or directory:"
ls -al /tmp/identities.json
echo

echo "Refresh the identities cache"
./callrestapi.py -e /identities/userCount -m get
./callrestapi.py -e /identities/cache/refreshes -m post
echo

echo "Pass the folder path and return the folder id and uri"
./getfolderid.py -f /gelcontent
echo

echo "Delete a folder based on its path - we don't want to delete a real folder, so try (and fail) to delete one which does not exist" 
./deletefolder.py -f /this_folder_does_not_exist
echo

echo "Delete a folder and its content - we don't want to delete a real folder, so try (and fail) to delete one which does not exist" 
./deletefolderandcontent.py -f /this_folder_does_not_exist
echo

echo "Return a set of configuration properties"
./getconfigurationproperties.py -c sas.identities.providers.ldap.user
echo

echo "Create a domain using createdomain"
./createdomain.py -t password -d test -u sasadm -p lnxsas -g "SASAdministrators,HR,Sales"
echo

# Commented out for Viya 3.4 version: this tool is only intended for use with Viya 3.3
#echo "Create a binary backup job"
#./createbinarybackup.py
#echo

echo "Get a rule ID"
#Get /Public folder ID
./getfolderid.py --folderpath /Public > /tmp/folderid.txt
id=$(grep "Id  " /tmp/folderid.txt | tr -s ' ' | cut -f3 -d " ")
echo "The Public folder ID is" $id
./getruleid.py -u /folders/folders/$id/** -p authenticatedUsers
echo

echo "Move all content from one folder to another folder (or in this case, the same folder)"
./movecontent.py -s /gelcontent/GELCorp/Shared/Reports -t /gelcontent/GELCorp/Shared/Reports -q
echo

echo "Test folder access"
./testfolderaccess.py -f '/gelcontent/GELCorp' -n gelcorp -t group -m read -s grant
echo

echo "Display all sasadministrator rules"
./listrules.py --p SASadministrators -o simple
echo

echo "Display all rules that contain SASVisual in the URI"
./listrules.py -u SASVisual -o simple
echo

echo "Create folders from a CSV file"
./createfolders.py -h
echo

echo Update the theme for the user sasadm
./updatepreferences.py -t user -tn sasadm -pi OpenUI.Theme.Default -pv sas_hcb
echo

echo "Explain permissions for the folder /gelcontent/GELCorp, with no header row."
./explainaccess.py -f /gelcontent/GELCorp
echo

echo "Explain permissions for the folder /gelcontent/GELCorp, with no header row, for Heather."
./explainaccess.py -f /gelcontent/GELCorp -n Heather -t user
echo

echo "Explain permissions for the folder /gelcontent/GELCorp, with a header row, and include the folder path."
./explainaccess.py -f /gelcontent/GELCorp --header -p
echo

echo "Explain permissions for the folder /gelcontent/GELCorp, showing only rows with at least one direct permission."
./explainaccess.py -f /gelcontent/GELCorp --direct_only
echo

echo "Explain permissions for several application capabilities. Notice that there are no conveyed permissions in the results"
./explainaccess.py -u /SASEnvironmentManager/dashboard --header -p -l read update delete secure add remove create
./explainaccess.py -u /SASDataStudio/** -p -l read update delete secure add remove create
./explainaccess.py -u /SASDataExplorer/** -p -l read update delete secure add remove create
./explainaccess.py -u /SASVisualAnalytics_capabilities/buildAnalyticalModel -p -l read update delete secure add remove create
echo

echo "Explain the permissions for a folder expressed as a URI. This works with any kind of object, not just folders"
echo "Uses the default permissions list. Specify -c true to include conveyed permissions, as they are not included by default when you use the -u URI parameter."
#Get /gelcontent/GELCorp folder ID
./getfolderid.py --folderpath /gelcontent/GELCorp > /tmp/folderid.txt
id=$(grep "Id  " /tmp/folderid.txt | tr -s ' ' | cut -f3 -d " ")
./explainaccess.py -u /folders/folders/$id --header -p -c true
echo

echo "Get the path of a folder"
./getpath.py -u /folders/folders/$id
echo

echo "List members of a folder, with paths for each member"
./listmemberswithpath.py -u /folders/folders/$id -r
echo
