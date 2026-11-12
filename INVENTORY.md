# Inventory of pyviyatools

| Group | Tool | Description | Note |
| --- | --- | --- | --- |
| General | callrestapi.py | Call a Viya REST endpoint | |
| General | call_rest_api.py | Legacy Python 2 wrapper for `callrestapi.py`; use `callrestapi.py` with Python 3 | |
| General | getfolderid.py | return ID or URI from folder path | |
| General | getpath.py | Return a folder or content path from its ID or URI | |
| General | getpathsplus.py | Return a folder path and additional details from an ID or URI | |
| General | checkssl.py | Check SSL certificate configuration | |
| General | validateviya.py | Check that a Viya environment is working | |
| Authorization | applyviyarules.py | Reads Viya Rules from a CSV and creates in Viya | |
| Authorization | applyauthmodel.py | used in conjunction with the ViyaAuthModel project to apply authorization| |
| Authorization | applyfolderauthorization.py | Apply bulk authorization from a CSV file to folders and contents | |
| Authorization | explainaccess.py |  explain direct and indirect permissions on an object | |
| Authorization | toggleviyarules.py | Reads in a CSV file, looks up the rule IDs and either disables or enables the rule | |
| Authorization | testfolderaccess.py | Test a user's or group's permission on a folder | |
| Inventory | listcaslibs.py | List CAS libraries | |
| Inventory | listcaslibsandeffectiveaccess.py | List CAS libraries and effective access | |
| Inventory | listcastables.py | List CAS tables | |
| Inventory | listcastablesandeffectiveaccess.py | List CAS tables and effective access | |
| Inventory | listcontent.py | Query and list Viya content | |
| Inventory | listfiles.py | Query and list files stored in the Viya Infrastructure Data Server | |
| Inventory | listgroupsandmembers.py | List Viya groups and group membership | |
| Inventory | listmemberswithpath.py | List folder members with their paths | |
| Inventory | listmodelobjects.py | Query and list analytic model objects | |
| Inventory | listreports.py | Query and list Visual Analytics reports | |
| Inventory | listrules.py | Query and list authorization rules | |
| Inventory | listtransferpackages.py | Query and list transfer packages in the Infrastructure Data Server | |
| Inventory | listallcasservercachestatus.py | List cache status for CAS servers | |
| Inventory | comparecontent.py | Compare two content inventory files | Added 09/05/2024 |
| Inventory | compareviyarules.py | Compare Viya authorization rules | |
| Inventory | getauditrecords.py | Retrieve audit records | |
| Inventory | getactivityrecords.py | Retrieve activity records | |
| Inventory | getreportdatasources.py | List report data sources | |
| Inventory | getdefaultqkb.py | Get the default QKB configuration | |
| Inventory | getloglevels.py | Retrieve service log levels | |
| Inventory | getruleid.py | Look up an authorization rule ID | |
| Migration | importcaslibs.py | Import JSON files with CASLIB definitions from a directory | |
| Migration | importconfiguration.py | Import Viya configuration definitions from JSON files | |
| Migration | importtemplates.py | Import Viya templates from a directory | |
| Migration | importpackages.py | Import Viya packages from a directory | |
| Migration | changeimportloc.py | Prepare exported JSON content for import to a target folder | |
| Migration | gettransfermapping.py | Download a JSON mapping file from a mapping set | |
| Migration | exportcaslibs.py | Export CAS libraries and authorization to a directory | |
| Migration | exportcustomgroups.py | Export custom groups to a package | |
| Migration | exportfolder.py | Export a folder and its content to a package | |
| Migration | exportfoldertree.py | Export the Viya folder tree to a set of packages | |
| Migration | exportstudioflowcode.py | Create SAS code from SAS Studio flows | |
| Migration | exportgeoproviders.py | Export geographic data providers to JSON files | |
| Migration | exportjobflow.py | Export job flows and their dependent objects | |
| Migration | deletetransferpackages.py | Delete transfer packages | |
| Migration | uploadfiles.py | Upload files to Viya | |
| Migration | createcaslibjson.py | Generate CASLIB definition JSON files from a CSV file | |
| Migration | createcaslibjsonauth.py | Generate CASLIB definition JSON with authorization data | |
| Migration | createreportimage.py | Export a Visual Analytics report or object as an image | |
| Migration | createreportpdf.py | Export a Visual Analytics report as a PDF | |
| Migration | snapshotreports.py | Export individual reports to a Viya package | |
| Migration | snapshotcontent.py | Export individual content items to a Viya package | |
| Management | archivefiles.py | Archive and optionally delete files stored in the Viya Infrastructure Data Server | |
| Management | createbinarybackup.py | Create a binary backup job | |
| Management | movecontent.py |Move content from a source to a target folder | |
| Management | createfolders.py | Create folders that are read from a csv file | |
| Management | creategroups.py | Create custom groups that are read from a csv file | |
| Management | createpublishdest.py | Create publishing destinations | |
| Management | deletecontent.py | Deletes content from a folder | |
| Management | deletefolder.py | Deletes a folder | |
| Management | deletefolderandcontent.py | Deletes a folder, any sub-folders and content | |
| Management | deletepublishdest.py | Deletes a publishing destination | |
| Management | deletejobhistory.py | Removes historical job execution data and logs | |
| Management | deleteorphanedfiles.py | Removes files with a parentUri that does not exist | |
| Management | mergeuserfolders.py | Merge user folders | |
| Management | removecaslibs.py | Remove CAS libraries | |
| Management | loadcasdata.py | Load data into CAS | |
| Management | loadcasformats.py | Load formats into CAS | |
| Management | setjobrequestexpire.py | Defines the expiresAfter parameter for existing job requests | |
| Management | setjobrequestfolder.py | Stores job requests in a folder | |
| Management | getimportresults.py | Retrieves results of each import task from an import job | |
| Management | getschedulehistory.py | Retrieves the most recent execution result from scheduled jobs | |
| Management | deleteorphanedfoldermembers.py | Identifies and optionally deletes broken folder members | |
| Management | deleteorphanedschedulerjobs.py | Identifies and optionally removes scheduled jobs without a valid target | |
| Management | setobjectattribute.py | Set an object attribute using a PUT update | |
| Configuration | createdomain.py | Create Viya domain | |
| Configuration | createcryptdomain.py | Create an encryption domain | |
| Configuration | modifydomain.py | Modify an existing  Viya domain | |
| Configuration | deletedomain.py | delete a Viya domain | |
| Configuration | updatedomain.py |update a Viya domain | |
| Configuration | updatepreferences.py |update user preferences | |
| Configuration | getconfigurationproperties.py | Return a set of configuration properties | |
| Configuration | setconfigurationproperties.py | Set configuration properties | |
| Configuration | getposixgroups.py | Returns the posix attributes of a group or all groups | |
| Configuration | getposixidentity.py | Returns the posix attributes of a user similar to the Linux "id" command | |
| Configuration | setposixattributes.py | Set POSIX attributes for User and Group (uid and gid) from a csv file | |
| Configuration | getcomputecontextattributes.py |get attributes of a  compute context. | |
| Configuration | setcomputecontextattributes.py |Add attributes to an existing compute context. | |
| Configuration | updatecomputecontext.py | Update an existing compute context from a JSON file. | |
| Configuration | modifyglobalcaslib.py | Modify global CASLIB settings | |
| Configuration | setdefaultqkb.py | Set the default QKB configuration | |
| Configuration | setfiletypedefname.py | Set a file type definition name | |
| Utility |loginviauthinfo.py | Authenticate to Viya using an .authinfo file | |
| Utility |showsetup.py | Display system settings to help with troubleshooting | |
| Utility |setup.py | Configure the location and executable name of the Viya CLI | |
| Utility |savetoken.py | Save the current authentication token | |
| Other | submit_jobdef.py | Submit Job using job definition | |
| Other | submit_jobreq.py | Submit Job using job request | |
| Other | setupcopilotcredentials.py | Create or update credentials for SAS Viya Copilot setup | |

The repository also contains shared support modules (`sharedfunctions.py` and `jobmodule.py`) and an example script (`listcaslibs_example.py`); these are not standalone administration tools.