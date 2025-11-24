import argparse
import json
import logging
import os
import tempfile

from deepdiff import DeepDiff
from sharedfunctions import (
    getinputjson,
    getconfigurationproperty,
    updateconfigurationproperty,
    getclicommand
)

# get cli location from properties, check that cli is there if not ERROR and stop
clicommand=getclicommand()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Import JSON files that update Viya configuration."
    )
    parser.add_argument("-o", "--output", choices=["csv", "json", "simple", "simplejson"], default="json")
    parser.add_argument("-f", "--file", help="The JSON configuration definition to import")
    parser.add_argument("--ignore-items-keys", nargs="*", default=["id", "links"])
    parser.add_argument("--ignore-metadata-keys", nargs="*", default=["createdBy","creationTimeStamp", "modifiedBy", "modifiedTimeStamp"])
    parser.add_argument("--include-keys", nargs="*", default=["version", "accept", "name", "items"])
    parser.add_argument("--dryrun", action="store_true", help="Simulate the operation without applying changes")
    return parser.parse_args()

# Extracts the config definition from a json file.
# Example sas.identities.providers.ldap.user

def extract_config_definition(data):
    media_type = data["items"][0]["metadata"]["mediaType"]
    return media_type.split(".config.")[-1].split("+")[0]

# Filters json by include top level keys, ignoring keys in items, and ignoring keys under metadata.

def filter_json(data, include_keys, ignore_items_keys=None, ignore_metadata_keys=None):
    result = {}
    for key in include_keys:
        if key not in data:
            continue
        if key == "items":
            result["items"] = [
                {
                    k: (
                        {mk: mv for mk, mv in v.items() if mk not in (ignore_metadata_keys or [])}
                        if k == "metadata" and isinstance(v, dict)
                        else v
                    )
                    for k, v in item.items() if k not in (ignore_items_keys or [])
                }
                for item in data["items"]
            ]
        else:
            result[key] = data[key]
    return result

# validate_changes
# Function to compare current to target json and validate the changes before processing

def validate_changes(diff):
    unexpected = [k for k in diff if k != "values_changed"]

    if unexpected:
        print("❌ Disallowed changes detected:")
        for key in unexpected:
            print(f" - {key}: {diff[key]}")
        raise SystemExit("Dry run failed: Only value changes are allowed.")

    for path, change in diff.get("values_changed", {}).items():
        if "metadata']['mediaType" in path:
            print("❌ mediaType has changed!")
            print(f"Old: {change['old_value']}")
            print(f"New: {change['new_value']}")
            raise SystemExit("❌ mediaType' cannot be modified. Please update the target JSON file with the correct mediaType before retrying.")

        print(f"{path}: {change['old_value']} → {change['new_value']}")

        if "root['version']" in path:
            old_version = change['old_value']
            new_version = change['new_value']
            if new_version <= old_version:
                raise SystemExit("❌: Attempted to set version to {new_version}, but current version is {old_version}. The new version must be greater.")


def apply_changes(filtered_data):
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "filtered_target.json")
        # write the JSON file
        with open(filepath, "w") as f:
            json.dump(filtered_data, f, indent=4)

        # build the command string
        command = clicommand + ' configuration configurations update --file ' + filepath

        # now open the tmp file you just wrote and print its contents
        with open(filepath, "r") as f:
            print(f.read())

        # run the update
        updateconfigurationproperty(command)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO)

    if args.file and not os.path.isfile(args.file):
        raise FileNotFoundError(f"File not found: {args.file}")

    target_data = getinputjson(args.file)

    config_definition = extract_config_definition(target_data)
    logging.info(f"config definition = {config_definition}")

    current_data = getconfigurationproperty(config_definition)

    # Filter the current and target json to include only the keys we require when updating.
    # Include the following keys at the top level - include_keys
    # Exclude the following keys at the items level - ignore_items_keys
    # Exclude the following keys at the metadata level - ignore_metadata_keys

    filtered_target = filter_json(target_data, args.include_keys, args.ignore_items_keys, args.ignore_metadata_keys)
    filtered_current = filter_json(current_data, args.include_keys, args.ignore_items_keys, args.ignore_metadata_keys)

    diff = DeepDiff(filtered_current, filtered_target, ignore_order=True)

    if not diff:
        logging.info("✅ No changes detected.")
    else:
        diff = diff.to_dict()  # convert only when differences exist
        validate_changes(diff)

        if args.dryrun:
            logging.info("✅ Dryrun detected, no changes will be applied")
        else:
            apply_changes(filtered_target)




if __name__ == "__main__":
    main()