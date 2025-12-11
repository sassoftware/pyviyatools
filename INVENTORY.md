# Inventory of pyviyatools

| Group| Tool | Description | Note
|  ---  |  ---  |  --- | --- |
| General | callrestapi.py |calls a Viya REST endpoint | |
| General | getfolderid.py | return ID or URI from folder path | |
| General | getpath.py | return folder path from ID ir URI | |
| General | getpathsplus.py | return folder path and additional details from ID ir URI | |
| Authorization | applyviyarules.py | Reads Viya Rules from a CSV and creates in Viya | |
| Authorization | applyauthmodel.py | used in conjunction with the ViyaAuthModel project to apply authorization| |
| Authorization | applyfolderauthorization.py | Apply bulk authorization from a CSV file to folders and contents | |
| Authorization | explainaccess.py |  explain direct and indirect permissions on an object | |
| Authorization | toggleviyarules.py | Reads in a CSV file, looks up the rule IDs and either disables or enables the rule | |
| Inventory | listcaslibs.py | list CAS libraries | |
| Inventory | listcaslibsandeffectiveaccess.py | list CAS libraries and effective access | |
| Inventory | listcastables.py |list CAS tables | |
| Inventory | listcastablesandeffectiveaccess.py | list CAS tables and effective access | |
| Inventory | listcontent.py | query and list viya content | |
| Inventory | listfiles.py | query and list files stored in Viya infastructure data server | |
| Inventory | listgroupsandmembers.py | list Viya groups and group membership | |
| Inventory | listmodelobjects.py | query and list analytic model objects | |
| Inventory | listreports.py | query and list Visual Analytics Reports | |
| Inventory | listrules.py | query and list authorization rules | |
| Inventory | listtransferpackages.py | query and list transfer packages stored in infastructure data server | |
| Inventory | comparecontent.py | Can be used to compare two inventory files|Added 09/05/2024 |
| Migration | importcaslibs.py | import JSON files with CASLIB definitions from a directory | |
| Migration | importconfiguration.py | import JSON files with viya configuration definitions from a directory | |
| Migration | importtemplates.py | import Viya templates from a directory | |
| Migration | importpackages.py | import Viya packages from a directory | |
| Migration | gettransfermapping.py | download a JSON mapping file from a mapping set | |
| Migration | exportcaslibs.py | export caslibs and authorization to a directory | |
| Migration | exportcustomgroups.py | export custom groups to a package | |
| Migration | exportfolder.py | export an individual folder and its content to a package | |
| Migration | exportfoldertree.py | export the complete viya folder tree to a set of packages | |
| Migration | exportstudioflowcode.py | create SAS code from SAS Studio flows | |
| Migration | exportgeoproviders.py |  export geographic data providers to json files in a directory | |
| Migration | exportjobflow.py |  export one or many job flows and all dependent objects | |
| Migration | snapshotreports.py | export individual reports to a viya package per report | |
| Migration | snapshotcontent.py | export individual content to a viya package per content item | |
| Management | archivefiles.py |Archive and optionally delete files stored in the Viya infrastructure data server. | |
| Management | validateviya.py |Validate that a Viya environment is working. | |
| Management | validateviya.py |Validate that a Viya environment is working. | |
| Management | movecontent.py |Move content from a source to a target folder | |
| Management | createfolders.py | Create folders that are read from a csv file | |
| Management | creategroups.py | Create custom groups that are read from a csv file | |
| Management | createpublishdest.py | Create publising destinations| |
| Management | deletecontent.py | Deletes content from a folder | |
| Management | deletefolder.py | Deletes a folder | |
| Management | deletefolderandcontent.py | Deletes a folder, any sub-folders and content | |
| Management | deletepublishdest.py |  Deletes a publishing destination| |
| Management | deletejobhistory.py | Removes historical job execution data and logs | |
| Management | deleterophanedfiles.py | Removes files with a parentUri that does not exist | |
| Management | setjobrequestexpire.py | Defines the expiresAfter parameter for existing job requests | |
| Management | setjobrequetsfolder.py | Stores job requests in a folder | |
| Management | getimportresults.py | Retrieves results of each import task from an import job | |
| Management | getschedulehistory.py | Retrieves the most recent execution result from scheduled jobs | |
| Management | deleteorphanedfoldermembers.py | Identifies and optionally deletes broken folder members | |
| Configuration | createdomain.py | Create Viya domain | |
| Configuration | createcryptdomain.py | Create an encryption domain | |
| Configuration | modifydomain.py | Modify an existing  Viya domain | |
| Configuration | deletedomain.py | delete a Viya domain | |
| Configuration | updatedomain.py |update a Viya domain | |
| Configuration | updatepreferences.py |update user preferences | |
| Configuration | getconfigurationproperties.py | Return a set of configuration properties | |
| Configuration | getposixgroups.py | Returns the posix attributes of a group or all groups | |
| Configuration | getposixidentity.py | Returns the posix attributes of a user similar to the Linux "id" command | |
| Configuration | setposixattributes.py | Set POSIX attributes for User and Group (uid and gid) from a csv file | |
| Configuration | getcomputecontextattributes.py |get attributes of a  compute context. | |
| Configuration | setcomputecontextattributes.py |Add attributes to an existing compute context. | |
| Configuration | updatecomputecontext.py | Update an existing compute context from a JSON file. | |
| Utility |loginvauthinfo.py | Authenticate to Viya using an .authinfo file | |
| Utility |showsetup.py | output some system settings to help with debugging issues | |
| Utility |setup.py | provide location of Viya CLI | |
| Other | submit_jobdef.py | Submit Job using job definition | |
| Other | submit_jobreq.py | Submit Job using job request | |