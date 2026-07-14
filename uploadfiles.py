#!/usr/bin/env python3
# Script to add one or more files to the files service in the Viya environment.
# This uses the files service rest API to upload files, so is bound by the configured size limit for the files service.
# Script will accept as arguments a destination path in SAS Content and either one or more files to upload, or a folder containing files to upload.
# The script is provided either multiple --file arguments or a single --folder argument, or both. It is also passed a --content-path argument which is the destination path in SAS Content where the files will be uploaded to.
# Change History
# 27MAY2026 Initial commit
#
import argparse
import os
from sharedfunctions import callrestapi,getfolderid,getpath
import logging

parser = argparse.ArgumentParser()
parser.add_argument("-f","--file", help="Specify one or more files to upload.",action="append")
parser.add_argument("--folder", help="Specify a folder containing files to upload.")
parser.add_argument("-c","--content-path", help="Specify the destination path in SAS Content where the files will be uploaded to.",required=True)
args = parser.parse_args()
files=args.file
folder=args.folder
content_path=args.content_path

# set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Validate that at least one of --file or --folder is provided
if not files and not folder:
    logging.error("You must specify at least one file to upload or a folder containing files to upload.")
    exit(1)

# Get the folder ID for the destination content path
folder_details = getfolderid(content_path)
folder_id = folder_details[0]
if not folder_id:
    logging.error(f"Could not find folder ID for content path: {content_path}")
    exit(1)

# Collect the list of files to upload
files_to_upload = []
if files:
    for file in files:
        if os.path.isfile(file):
            files_to_upload.append(file)
        else:
            logging.warning(f"Specified file does not exist: {file}")
if folder:
    if os.path.isdir(folder):
        for entry in os.listdir(folder):
            file_path = os.path.join(folder, entry)
            if os.path.isfile(file_path):
                files_to_upload.append(file_path)
    else:
        logging.warning(f"Specified folder does not exist: {folder}")

if not files_to_upload:
    logging.error("No valid files to upload.")
    exit(1)


# For each file, call the files service endpoint (POST to /files/files) using multipart or the body to upload the file content. Use the content-disposition header to specify the file name. 
# The query parameter parentFolderUri should be set to /folders/folders/{folder_id} where folder_id is the ID of the destination folder in SAS Content we want to upload the file to.
# The query parameter typeDefName is used to specify the type of the file being uploaded. We can check if /types/types/file_{extension} exists to determine if there is a specific type for the file extension, and if not we can not define the typeDefName parameter and the files service will default to treating it as a generic file.

# Maintain a list of extensions we have checked for a specific type definition to avoid making unnecessary REST API calls.
checked_extensions = {}

for file in files_to_upload:
    file_name = os.path.basename(file)
    file_extension = os.path.splitext(file_name)[1].lower().lstrip('.')
    type_def_name = None

    if file_extension in checked_extensions:
        type_def_name = checked_extensions[file_extension]
    else:
        # Check if a specific type definition exists for this file extension using HEAD method on /types/types/file_{extension}
        type_check_response,type_check_response_code = callrestapi(f"/types/types/file_{file_extension}", "head")
        if type_check_response_code == 200:
            type_def_name = f"file_{file_extension}"
            logging.info(f"Found specific type definition for extension '{file_extension}': {type_def_name}")
        else:
            logging.info(f"No specific type definition found for extension '{file_extension}'. Using generic file type.")
        checked_extensions[file_extension] = type_def_name

    with open(file, 'rb') as f:
        files_payload = {
            'file': (file_name, f)
        }
        query_params = {
            'parentFolderUri': f"/folders/folders/{folder_id}"
        }
        if type_def_name:
            query_params['typeDefName'] = type_def_name

        response = callrestapi("/files/files", "postmultipart", data=files_payload, params=query_params)
        if response and response.get("id"):
            logging.info(f"Successfully uploaded file: {file_name}")
        else:
            logging.error(f"Failed to upload file: {file_name}")