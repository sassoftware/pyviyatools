#!/usr/bin/env python3
# Script to add one or more files to the files service in the Viya environment.
# This uses the files service rest API to upload files, so is bound by the configured size limit for the files service.
# Script will accept as arguments a destination path in SAS Content and either one or more files to upload, or a folder containing files to upload.
# The script is provided either multiple --file arguments or a single --folder argument, or both. It is also passed a --content-path argument which is the destination path in SAS Content where the files will be uploaded to.
# Change History
# 27MAY2026 Initial commit
#
# Copyright © 2026, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
from sharedfunctions import callrestapi,getfolderid
import logging

parser = argparse.ArgumentParser()
parser.add_argument("-f","--file", help="Specify one or more files to upload.",action="append")
parser.add_argument("--folder", help="Specify a folder containing files to upload.")
parser.add_argument("-w","--overwrite", help="Overwrite existing files with the same name in the destination folder.",action="store_true")
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


# For each file, call the files service endpoint (POST to /files/files) using multipart or the body to upload the file content.
# The query parameter parentFolderUri should be set to /folders/folders/{folder_id} where folder_id is the ID of the destination folder in SAS Content.
# The query parameter typeDefName is used to specify the type of the file being uploaded from the types service.

# Maintain a list of extensions we have checked for a specific type definition to avoid making unnecessary REST API calls.
checked_extensions = {}
 
for file in files_to_upload:
    file_name = os.path.basename(file)
    file_extension = os.path.splitext(file_name)[1].lower().lstrip('.')
    type_def_name = None

    # Check if a file with this name already exists in the destination folder
    response = callrestapi(f"/folders/folders/{folder_id}/members", "get", params={"filter": f"and(eq(name,'{file_name}'),eq(type,'child'))"})
    if response and response.get("items"): # We have at least one file with this name in the destination folder
        if args.overwrite:
            # Check if it's only one file with this name in the destination folder. If there are multiple, we will not overwrite and will log a warning.
            if len(response["items"]) > 1:
                logging.warning(f"Multiple files with the name '{file_name}' already exist in the destination folder. Skipping upload.")
                continue
            logging.info(f"A file with the name '{file_name}' already exists in the destination folder. Overwriting.")
            # We can overwrite using a PUT request to /files/files/{file_id}/content.
            file_uri = response["items"][0]["uri"]
            # Get the etag of the existing file to include in the If-Match header for the PUT request.
            response,etag,rc = callrestapi(file_uri, "head", returnEtag=True)
            if not etag:
                logging.error(f"Could not retrieve etag for existing file: {file_name}. Skipping upload.")
                continue
            headers = {
                "If-Match": etag
            }
            with open(file, 'rb') as f:
                files_payload = {
                    'file': (file_name, f)
                }
                query_params = {
                    'parentFolderUri': f"/folders/folders/{folder_id}"
                }
                if type_def_name:
                    query_params['typeDefName'] = type_def_name

                response = callrestapi(f"{file_uri}/content", "putmultipart", data=files_payload, params=query_params, header=headers)
                if response and response.get("id"):
                    logging.info(f"Successfully overwritten file: {file_name}")
                else:
                    logging.error(f"Failed to overwrite file: {file_name}")
            continue
        else:
            logging.warning(f"A file with the name '{file_name}' already exists in the destination folder. Skipping upload.")
            continue

    if file_extension in checked_extensions:
        type_def_name = checked_extensions[file_extension]
    else:
        # Check if a specific type definition exists for this file extension using /types/types?filter=contains(extensions,'{file_extension}')
        response = callrestapi("/types/types", "get", params={"filter": f"contains(extensions,'{file_extension}')"})
        if response and response.get("items"):
            type_def_name = response["items"][0]["name"]
        else:
            logging.info(f"No specific type definition found for file extension: {file_extension}")
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