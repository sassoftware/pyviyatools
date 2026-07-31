#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setdefaultqkb.py
# March 2026
#
# Set the default QKB locale and QKB name for SAS Viya CAS and Compute engines.
# Reads the current configuration, updates only if needed, applies via
# setconfigurationproperties.py, and validates the result.
#
# Change History
#
# MAR2026 Initial version
# APR 2026 Code Review
# JULY 2026 Final Code Review
# 
#
# Copyright 2026, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from __future__ import print_function
import argparse
import json
import subprocess

# AFTER
from sharedfunctions import getconfigurationproperty, updateconfigurationproperty, getclicommand

# call getdefaultqkb.py as a subprocess and return current locale and qkb for the given engine
def get_current_qkb_from_script(engine):

    cmd = ["python3", "getdefaultqkb.py", "--engine", engine, "--output", "json"]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Failed to run getdefaultqkb.py")

    try:
        data = json.loads(result.stdout)
    except Exception:
        print("Raw output:", result.stdout)
        raise RuntimeError("Failed to parse JSON from getdefaultqkb.py")

    if engine not in data:
        raise RuntimeError("No data returned for engine: " + engine)

    engine_data = data[engine]

    return {
        "locale": engine_data.get("locale"),
        "qkb": engine_data.get("default QKB")
    }


# parse command-line arguments
def parse_args():

    parser = argparse.ArgumentParser(
        description="Set the default QKB locale and QKB name for SAS Viya CAS and Compute engines."
    )

    parser.add_argument(
        "--engine",
        nargs="*",
        choices=["cas", "compute"],
        required=True,
        help="Engine(s) to update: cas, compute, or both."
    )

    parser.add_argument(
        "--locale",
        required=True,
        help="Locale to set, e.g. ENUSA."
    )

    parser.add_argument(
        "--qkb",
        required=True,
        help="QKB name to set, e.g. 'QKB CI 33'."
    )

    parser.add_argument(
        "--output-file",
        default="/tmp/qkb_update.json",
        help="Path for the temporary JSON payload file. Default: /tmp/qkb_update.json"
    )

    return parser.parse_args()


# retrieve the configuration item and its raw contents for the given engine
def get_engine_config(engine):

    if engine == "cas":
        config_def = "sas.cas.instance.config"
        item_name = "config"
    else:
        config_def = "sas.compute.server"
        item_name = "configuration_options"

    config_data = getconfigurationproperty(config_def)

    for item in config_data["items"]:
        if item.get("name") == item_name:
            return item, item.get("contents", "")

    raise RuntimeError("Config item not found for engine: " + engine)


# return True if the current state does not match the target locale and qkb
def needs_update(current, target_locale, target_qkb):

    return not (
        current["locale"] == target_locale and
        current["qkb"] == target_qkb
    )


# edit the raw contents string to set the new locale and qkb values
# compute uses SAS option format: -DQLOCALE (ENUSA) and -DQSETUPLOC 'QKB CI 33'
# cas uses property format: cas.DQLOCALE="ENUSA" and cas.DQSETUPLOC="QKB CI 33"
def update_contents(contents, new_locale, new_qkb, engine):

    updated_lines = []
    found_locale = False
    found_qkb = False

    for line in contents.splitlines():
        stripped = line.strip()

        if engine == "compute":
            if "DQLOCALE" in stripped:
                line = "-DQLOCALE (" + new_locale + ")"
                found_locale = True
            elif "DQSETUPLOC" in stripped:
                line = "-DQSETUPLOC '" + new_qkb + "'"
                found_qkb = True

        elif engine == "cas":
            if "DQLOCALE" in stripped:
                line = 'cas.DQLOCALE="' + new_locale + '"'
                found_locale = True
            elif "DQSETUPLOC" in stripped:
                line = 'cas.DQSETUPLOC="' + new_qkb + '"'
                found_qkb = True

        updated_lines.append(line)

    # append keys if they were not already present in the contents
    if not found_locale:
        if engine == "compute":
            updated_lines.append("-DQLOCALE (" + new_locale + ")")
        else:
            updated_lines.append('cas.DQLOCALE="' + new_locale + '"')

    if not found_qkb:
        if engine == "compute":
            updated_lines.append("-DQSETUPLOC '" + new_qkb + "'")
        else:
            updated_lines.append('cas.DQSETUPLOC="' + new_qkb + '"')

    return "\n".join(updated_lines)


# build the JSON payload by inserting updated contents into the original item
def build_payload(original_item, updated_contents):

    updated_item = dict(original_item)
    updated_item["contents"] = updated_contents
    return {"items": [updated_item]}


# write the JSON payload to disk
def write_payload(payload, filepath):

    with open(filepath, "w") as f:
        json.dump(payload, f, indent=4)


# AFTER
def apply_config(filepath):
    clicommand = getclicommand()
    command = clicommand + " configuration configurations update --file " + filepath
    updateconfigurationproperty(command)

# orchestrate the full read-compare-update-validate flow for a single engine
def process_engine(engine, locale, qkb, output_file):

    print("\nProcessing " + engine.upper() + "...")

    current = get_current_qkb_from_script(engine)

    if not needs_update(current, locale, qkb):
        print("No changes needed.")
        return

    item, contents = get_engine_config(engine)

    updated_contents = update_contents(contents, locale, qkb, engine)

    payload = build_payload(item, updated_contents)
    write_payload(payload, output_file)

    print("Payload written to " + output_file)

    apply_config(output_file)

    # validate that the change landed correctly
    new_state = get_current_qkb_from_script(engine)

    if new_state["locale"] == locale and new_state["qkb"] == qkb:
        print("Validation successful.")
    else:
        print("NOTE: Validation failed. Current state does not match target.")
        print("  Expected locale : " + locale)
        print("  Got locale      : " + str(new_state["locale"]))
        print("  Expected qkb    : " + qkb)
        print("  Got qkb         : " + str(new_state["qkb"]))


def main():

    args = parse_args()

    for engine in args.engine:

        output_file = args.output_file

        # use separate output files per engine when processing both at once
        if len(args.engine) > 1:
            output_file = "/tmp/qkb_update_" + engine + ".json"

        process_engine(engine, args.locale, args.qkb, output_file)


if __name__ == "__main__":
    main()

# Example
# python3 setdefaultqkb.py --engine compute --locale ENUSA --qkb "QKB CI 33"
# python3 setdefaultqkb.py --engine cas compute --locale ENUSA --qkb "QKB CI 33"