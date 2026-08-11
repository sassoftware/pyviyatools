#!/usr/bin/env python3
# In the SAS Viya Platform, user folders are named after the user's account ID. In some cases that account ID may change after the user's
# folder has been created and content added. From the perspective of SAS Viya, the new account ID is a new user, so has no access to their
# old content.

# This script addresses this issue by either granting the new user access to the old user's folder, or by moving the old user ID folder content
# into the new user folder.

# Folders that have the "allowMove" property set to "false" cannot be moved or renamed. The folders service will prevent userFolders and delegate
# folders from having this attribute changed, so can never be moved.

# This script handles the following scenarios:
# 1. The user never logged in with the old ID (no action required)
# 2. The user has not logged in with the new ID (grant access to the old folder -- can rerun this script after the user logs in with the new ID to move content)
# 3. The user has logged in with the new ID (move content from old folder to new folder)

# Import required modules
import argparse
import logging
import sys
import csv
from sharedfunctions import callrestapi, callpagedrestapi

# Configure a basic logger to output timestamp/level/message.
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Merge user folders in SAS Viya Platform based on account ID changes."
)
parser.add_argument(
    "--csv",
    required=False,
    help="Path to the CSV file containing old and new user IDs.",
)
parser.add_argument(
    "--commit", action="store_true", help="Commit changes (default is dry run)."
)
parser.add_argument("--old-id", required=False, help="Old user account ID.")
parser.add_argument("--new-id", required=False, help="New user account ID.")
parser.add_argument(
    "--merge",
    action="store_true",
    help="Merge content from old user folder to new user folder.",
)
parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
parser.add_argument(
    "--skip-identity-validation",
    action="store_true",
    help="Skip validation of user IDs in the Viya identities service.",
)
parser.add_argument(
    "--original-root-folder-id",
    required=False,
    help="Folder ID for the /Users folder to move content from.",
)
parser.add_argument(
    "--new-root-folder-id",
    required=False,
    help="Folder ID for the /Users folder to move content to.",
)
args = parser.parse_args()

if args.debug:
    logger.setLevel(logging.DEBUG)
    logger.debug("Debug logging enabled.")

# Validate supplied options:
if not args.csv and (not args.old_id or not args.new_id):
    logger.error("Either --csv or both --old-id and --new-id must be provided.")
    sys.exit(1)

# Define helper functions


# Function: Validate User
def validate_user(user_id):
    """
    Check that a user exists in the Viya identities service.

    Args:
        user_id (str): The user account ID to validate.

    Returns:
        user_id (str): The validated user account ID.
    """
    logger.debug(
        f"validate_user: Validating user ID '{user_id}' against identities service."
    )
    if args.skip_identity_validation:
        logger.debug(
            "validate_user: Skipping validation of user ID '%s' in the Viya identities service.",
            user_id,
        )
        return user_id

    # Perform a case-insensitive search ($primary) for the user ID in the Viya identities service
    reqtype = "get"
    params = {"filter": f"eq($primary,id,'{user_id}')"}
    reqval = f"/identities/users"
    response = callrestapi(reqval, reqtype, params=params)

    # This response should contain a single item with "id" equal to the passed in user ID.
    if (
        not response
        or "items" not in response
        or len(response["items"]) == 0
        or len(response["items"]) > 1
    ):
        logger.error("User ID '%s' not found in the Viya identities service.", user_id)
        sys.exit(1)
    validated_user_id = response["items"][0]["id"]
    if validated_user_id != user_id:
        logger.warning(
            "User ID '%s' found in the Viya identities service as '%s'. Returning the validated ID.",
            user_id,
            validated_user_id,
        )
    return validated_user_id


# Function: Get Users root folder ID
def get_users_root_folder_id():
    """
    Get the folder ID for the /Users root folder.

    Returns:
        str: The folder ID for the /Users root folder.
    """
    logger.debug(
        "get_users_root_folder_id: Retrieving the folder ID for the /Users root folder."
    )
    reqtype = "get"
    reqval = "/folders/folders"
    params = {"filter": "eq(type,'userRoot')"}
    response = callrestapi(reqval, reqtype, params=params)

    # This should return a single item with "id" equal to the /Users root folder ID.

    if not response or "items" not in response or len(response["items"]) == 0:
        logger.error("Could not find the /Users root folder.")
        sys.exit(1)
    if len(response["items"]) > 1:
        logger.error(
            "Multiple /Users root folders found. Use --original-root-folder-id and --new-root-folder-id to specify the desired source and destination."
        )
        sys.exit(1)
    logger.debug("Found /Users root folder with ID: %s", response["items"][0]["id"])
    return response["items"][0]["id"]


# Function Get User Folder ID
def get_user_folder_id(user_id, root_folder_id):
    """
    Get the folder ID for a user's folder under the /Users root folder.

    Args:
        user_id (str): The user account ID.
        root_folder_id (str): The folder ID for the /Users root folder.

    Returns:
        str: The folder ID for the user's folder.
    """
    logger.debug(
        "get_user_folder_id: Retrieving the folder ID for user '%s' under userRoot folder ID '%s'.",
        user_id,
        root_folder_id,
    )
    reqtype = "get"
    reqval = f"/folders/folders/{root_folder_id}/members"
    params = {"filter": f"and(eq($tertiary,name,'{user_id}'),eq(contentType,'userFolder'))"}
    response = callrestapi(reqval, reqtype, params=params)

    # This should return a single item; extract folder ID from the member uri, not id (membership ID).
    if not response or "items" not in response or len(response["items"]) == 0:
        logger.debug("User folder for '%s' not found under /Users.", user_id)
        return None
    if len(response["items"]) > 1:
        logger.error("Multiple user folders found for '%s' under /Users.", user_id)
        return None
    folder_id = response["items"][0]["uri"].split("/")[-1]
    logger.debug(
        "get_user_folder_id: Found user folder for '%s' with ID: %s",
        user_id,
        folder_id,
    )
    return folder_id


# Function Create Rule
def create_rule(folder_id, user_id):
    """
    Create a rule to grant access to a user's folder.

    Args:
        folder_id (str): The folder ID for the user's folder.
        user_id (str): The user account ID.

    Returns:
        None
    """
    logger.debug(
        "create_rule: Granting user '%s' access on folder '%s'.", user_id, folder_id
    )

    # Validate the user ID before creating the rule
    validated_user_id = validate_user(user_id)

    logger.debug(
        "create_rule: Checking if a rule already exists for user '%s' on folder '%s'.",
        validated_user_id,
        folder_id,
    )
    reqtype = "get"
    reqval = "/authorization/rules"
    params = {
        "filter": f"and(or(eq(containerUri,'/folders/folders/{folder_id}'),eq(objectUri,'/folders/folders/{folder_id}/**')),eq(principal,'{validated_user_id}'))"
    }
    response = callrestapi(reqval, reqtype, params=params)
    if response and "items" in response and len(response["items"]) > 0:
        logger.info(
            "Rule already exists for user '%s' on folder '%s'.",
            validated_user_id,
            folder_id,
        )
        return

    logger.debug(
        "create_rule: No existing rule found for user '%s' on folder '%s'. Creating new rule.",
        validated_user_id,
        folder_id,
    )
    reqtype = "post"
    reqval = "/authorization/rules"
    data = {
        "containerUri": f"/folders/folders/{folder_id}",
        "objectUri": f"/folders/folders/{folder_id}/**",
        "type": "grant",
        "principal": validated_user_id,
        "principalType": "user",
        "permissions": ["delete", "read", "secure", "remove", "update", "add"],
        "description": f"Created by mergeuserfolders pyviyatools to grant {validated_user_id} permission on the folder.",
        "reason": f"Granting {validated_user_id} permission on the folder.",
    }
    if args.commit:
        response = callrestapi(reqval, reqtype, data=data)
        logger.info(
            "Created rule for user '%s' on folder '%s'.", validated_user_id, folder_id
        )
    else:
        logger.info(
            "DRY-RUN: Would create rule for user '%s' on folder '%s'.",
            validated_user_id,
            folder_id,
        )


# Function Validate Member Name
def validate_member_name(parent_id, content_type, object_name, type_def_name=None):
    """
    Validate that the new name for a folder is unique among its siblings.

    Args:
        parent_id (str): The parent folder ID.
        content_type (str): The content type of the member (e.g., 'folder').
        object_name (str): The name of the object to validate.
        type_def_name (str, optional): The type definition name.
     Returns:
        bool: True if the new name is unique among its siblings, False otherwise.
    """
    logger.debug(
        "validate_member_name: Validating that the new name '%s' for member type '%s' is unique under parent folder ID '%s'.",
        object_name,
        content_type,
        parent_id,
    )
    reqtype = "put"
    reqval = f"/folders/commons/validations/folders/{parent_id}/members/@new/name"
    if type_def_name is None:
        params = {"value": object_name, "type": content_type}
    else:
        params = {
            "value": object_name,
            "type": content_type,
            "typeDefName": type_def_name,
        }
    response = callrestapi(reqval, reqtype, acceptType="application/vnd.sas.validation+json", params=params)
    logger.debug(
        "validate_member_name: Validation response for new name '%s': %s",
        object_name,
        response.get("valid") if response else "No response",
    )
    return response.get("valid") if response else False


# Function Get Folder Members
def get_folder_members(folder_id):
    """
    Get the members of a folder.

    Args:
        folder_id (str): The folder ID.

    Returns:
        list: A list of members in the folder.
    """
    logger.debug(
        "get_folder_members: Retrieving members for folder ID '%s'.", folder_id
    )
    reqtype = "get"
    reqval = f"/folders/folders/{folder_id}/members"
    response = callpagedrestapi(reqval, reqtype)
    logger.debug(
        "get_folder_members: Retrieved %d members for folder ID '%s'.",
        len(response) if response else 0,
        folder_id,
    )
    return response if response else []


# Function move member
def move_member(old_folder_id, new_folder_id, member_id):
    """
    Move a member from the old folder to the new folder.

    Args:
        old_folder_id (str): The folder ID of the old user folder.
        new_folder_id (str): The folder ID of the new user folder.
        member_id (str): The member ID to move.
    """
    logger.debug(
        "move_member: Moving member ID '%s' from old folder ID '%s' to new folder ID '%s'.",
        member_id,
        old_folder_id,
        new_folder_id,
    )
    reqtype = "get"
    reqval = f"/folders/folders/{old_folder_id}/members/{member_id}"
    response = callrestapi(reqval, reqtype)
    if not response:
        logger.error(
            "Member ID '%s' not found in old folder ID '%s'.", member_id, old_folder_id
        )
        return
    member_copy = response.copy()
    member_copy["parentFolderUri"] = f"/folders/folders/{new_folder_id}"

    reqtype = "put"
    reqval = f"/folders/folders/{old_folder_id}/members/{member_id}"
    data = member_copy
    if args.commit:
        response = callrestapi(reqval, reqtype, data=data)
        logger.info(
            "Moved member ID '%s' to new folder ID '%s'.", member_id, new_folder_id
        )
    else:
        logger.info(
            "DRY-RUN: Would move member ID '%s' to new folder ID '%s'.",
            member_id,
            new_folder_id,
        )


# Function Merge Folders
def merge_folders(old_folder_id, new_folder_id):
    """
    Merge the contents of the old folder into the new folder.

    Args:
        old_folder_id (str): The folder ID of the old user folder.
        new_folder_id (str): The folder ID of the new user folder.

    Returns:
        None
    """
    logger.debug(
        "merge_folders: Merging contents from old folder ID '%s' into new folder ID '%s'.",
        old_folder_id,
        new_folder_id,
    )

    # Stop if the IDs are the same
    if old_folder_id == new_folder_id:
        logger.warning("Old folder ID and new folder ID are the same. Skipping.")
        return

    # Get the members of the old folder
    old_members = get_folder_members(old_folder_id)
    new_members = get_folder_members(new_folder_id)

    # For each member, we need to pull some attributes
    for member in old_members:
        member_id = member.get("id")
        member_name = member.get("name")
        member_uri = member.get("uri")
        member_type = member.get("type")
        member_content_type = member.get("contentType")
        # There may be a typeDefName attribute for some members, so we need to check for that
        member_type_def_name = member.get("typeDefName", None)

        # If the member is a reference, we can perform a name validation check and then move it to the new folder.
        if member_type == "reference":
            logger.debug(
                "Validating member name '%s' for uniqueness in new folder ID '%s'.",
                member_name,
                new_folder_id,
            )
            is_valid_name = validate_member_name(
                new_folder_id, member_content_type, member_name, member_type_def_name
            )
            if not is_valid_name:
                logger.error(
                    "Member name '%s' already exists in new folder ID '%s'. Skipping this member.",
                    member_name,
                    new_folder_id,
                )
                continue

            # Move the reference to the new folder
            logger.debug(
                "Moving reference '%s' (ID: %s) from old folder ID '%s' to new folder ID '%s'.",
                member_name,
                member_id,
                old_folder_id,
                new_folder_id,
            )
            move_member(old_folder_id, new_folder_id, member_id)

        elif member_type == "child":
            # Child members could be special "delegate" folders, normal folders, or normal content (reports, files, etc.). If we are working with a folder
            # we need to check if we can move it. Delegate folders can't be moved, so we'd need to identify the delegate folder in the destination and then
            # recursively run this function on the delegate folders.
            # Delegate folders have special content types: "trashFolder","favoritesFolder", "applicationDataFolder", "myFolder", "historyFolder"
            if member_content_type in [
                "trashFolder",
                "favoritesFolder",
                "applicationDataFolder",
                "myFolder",
                "historyFolder",
            ]:
                logger.debug(
                    "Member '%s' (ID: %s) is a delegate folder of type '%s'. Recursively merging its contents.",
                    member_name,
                    member_id,
                    member_content_type,
                )
                old_delegate_folder_id = member_uri.split("/")[-1]
                # Find the corresponding delegate folder in the new folder
                corresponding_new_member = next(
                    (
                        m
                        for m in new_members
                        if m.get("contentType") == member_content_type
                    ),
                    None,
                )
                if corresponding_new_member:
                    new_delegate_folder_id = corresponding_new_member.get("uri").split(
                        "/"
                    )[-1]
                    logger.debug(
                        "Found corresponding delegate folder in new folder ID '%s' with ID '%s'. Merging contents.",
                        new_folder_id,
                        new_delegate_folder_id,
                    )
                    merge_folders(old_delegate_folder_id, new_delegate_folder_id)
                else:
                    logger.warning(
                        "No corresponding delegate folder of type '%s' found in new folder ID '%s'. Skipping member.",
                        member_content_type,
                        new_folder_id,
                    )
                    continue
            elif member_content_type == "folder":
                old_member_folder_id = member_uri.split("/")[-1]

                # Check if a folder with the same name exists in the new folder
                corresponding_new_member = next(
                    (
                        m
                        for m in new_members
                        if m.get("contentType") == "folder"
                        and m.get("name") == member_name
                    ),
                    None,
                )
                if corresponding_new_member:
                    new_member_folder_id = corresponding_new_member.get("uri").split(
                        "/"
                    )[-1]
                    logger.debug(
                        "Found corresponding folder in new folder ID '%s' with ID '%s'. Merging contents.",
                        new_folder_id,
                        new_member_folder_id,
                    )
                    merge_folders(old_member_folder_id, new_member_folder_id)
                else:
                    logger.debug(
                        "No corresponding folder named '%s' found in new folder ID '%s'. Moving the folder.",
                        member_name,
                        new_folder_id,
                    )
                    move_member(old_folder_id, new_folder_id, member_id)
            else:
                # This is where normal content would land, so we should confirm we're not going to hit a naming conflict, then move it.
                logger.debug(
                    "Validating member name '%s' for uniqueness in new folder ID '%s'.",
                    member_name,
                    new_folder_id,
                )
                is_valid_name = validate_member_name(
                    new_folder_id, member_content_type, member_name, member_type_def_name
                )
                if not is_valid_name:
                    logger.error(
                        "Member name '%s' already exists in new folder ID '%s'. Skipping this member.",
                        member_name,
                        new_folder_id,
                    )
                    continue
                logger.debug(
                    "Moving content '%s' (ID: %s) from old folder ID '%s' to new folder ID '%s'.",
                    member_name,
                    member_id,
                    old_folder_id,
                    new_folder_id,
                )
                move_member(old_folder_id, new_folder_id, member_id)
    return True


# Function Process User IDs
def process_user_ids(old_id, new_id):
    """
    Process the merging of user folders based on old and new user IDs.

    Args:
        old_id (str): The old user account ID.
        new_id (str): The new user account ID.
    """
    logger.debug(
        "process_user_ids: Processing identity pair: '%s' -> '%s'", old_id, new_id
    )

    # Get the root folder IDs for the /Users folder
    if not args.original_root_folder_id and not args.new_root_folder_id:
        logger.debug(
            "process_user_ids: No root folder IDs provided. Retrieving /Users root folder ID."
        )
        original_root_folder_id = get_users_root_folder_id()
        new_root_folder_id = original_root_folder_id
    else:
        original_root_folder_id = args.original_root_folder_id
        new_root_folder_id = args.new_root_folder_id

    # Get the folder IDs for the old and new user folders
    old_folder_id = get_user_folder_id(old_id, original_root_folder_id)
    if not old_folder_id:
        logger.warning(
            "process_user_ids: Old user folder for '%s' not found. Skipping this identity pair.",
            old_id,
        )
        return
    new_folder_id = get_user_folder_id(new_id, new_root_folder_id)
    if not new_folder_id:
        if args.merge:
            # Scenario 2: new user hasn't logged in yet, nothing to merge into
            logger.warning(
                "process_user_ids: New user folder for '%s' not found. Log in with the new ID first, then rerun with --merge.",
                new_id,
            )
            return
        # Scenario 2: grant access to old folder so new user can access content before logging in
        logger.info(
            "process_user_ids: New user folder for '%s' not found. Granting access to old folder '%s'.",
            new_id,
            old_folder_id,
        )
        create_rule(old_folder_id, new_id)
        return

    # If the --merge flag is set, merge the contents of the old folder into the new folder
    if args.merge:
        logger.debug(
            "process_user_ids: Merging contents from old folder ID '%s' to new folder ID '%s'.",
            old_folder_id,
            new_folder_id,
        )
        merge_folders(old_folder_id, new_folder_id)
    else:
        # Otherwise, just grant access to the old folder for the new user
        logger.debug(
            "process_user_ids: Granting access to old folder ID '%s' for new user '%s'.",
            old_folder_id,
            new_id,
        )
        create_rule(old_folder_id, new_id)


# End define helper functions


# Main function
def main():
    """
    Main function to process user folder merging based on provided arguments.
    """
    # If commit isn't set, log that this is a dry run
    if not args.commit:
        logger.info(
            "Dry run mode: No changes will be committed. Use --commit to apply changes."
        )

    identities = []

    # If a CSV file is provided, read the old and new user IDs from it
    if args.csv:
        logger.info("Reading user ID pairs from CSV file: %s", args.csv)
        with open(args.csv, mode="r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                identities.append(
                    {
                        "old_user_id": row.get("old_user_id"),
                        "new_user_id": row.get("new_user_id"),
                    }
                )
    else:
        # If no CSV file is provided, use the command line arguments for old and new user IDs
        identities.append({"old_user_id": args.old_id, "new_user_id": args.new_id})
    for identity in identities:
        old_id = identity["old_user_id"]
        new_id = identity["new_user_id"]
        process_user_ids(old_id, new_id)


if __name__ == "__main__":
    main()
