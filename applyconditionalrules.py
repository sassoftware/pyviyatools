#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# applyconditionalrules.py
#
# Reads a CSV of conditional rules, converts each rule to JSON, and imports the
# rules into Viya one at a time.
#
# Change History
#
# 16NOV26  Initial development
# 18NOV26  Detect create-rules responses that report zero rules created.
#          Retry those rules with a unique temporary object URI so invalid SpEL
#          can be distinguished from the Viya conditional-rule uniqueness bug.
#          When the retry succeeds, locate the temporary rule by matching the
#          list-rules JSON and update it to the intended object URI.
#          (AI assisted update)
#
# Format of input CSV file is 7 columns
# Column 1: Object URI
# Column 2: Principal type ["group" | "user"]
# Column 3: Principal id [<groupID> | <userID>]
# Column 4: Access grant type ["grant" | "prohibit"]
# Column 5: Applicable permissions ["read","delete","add","create","remove","secure","update"]
# Column 6: Rule status ["true" | "false"]
# Column 7: Rule condition. This must contain a valid SpEL condition.
#
# Copyright 2026, SAS Institute Inc., Cary, NC, USA.  All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import copy
import csv
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime

import pandas as pd
from pandas.errors import EmptyDataError

from sharedfunctions import file_accessible, getclicommand


ZERO_CREATED_RE = re.compile(r"\b0\s+rules?\s+were\s+created\.", re.IGNORECASE)
CREATED_COUNT_RE = re.compile(
    r"\b(\d+)\s+rules?\s+were\s+created\.", re.IGNORECASE
)


def created_count(cli_output):
    """Return the final create-rules count in CLI output, or None."""
    matches = CREATED_COUNT_RE.findall(cli_output or "")
    return int(matches[-1]) if matches else None


def reported_zero_created(cli_output):
    """Return True when create-rules explicitly reports zero created rules."""
    return bool(ZERO_CREATED_RE.search(cli_output or ""))


def normalise_type(value):
    """Normalise rule type using the matching behavior from disableviyarules."""
    value = str(value or "").lower()
    if "prohibit" in value:
        return "prohibit"
    if "grant" in value:
        return "grant"
    return value


def normalise_principal(value):
    """Treat the empty principal spellings emitted by different tools equally."""
    if value in ("", None, "None"):
        return ""
    return value


def rule_matches(expected_rule, existing_rule):
    """Match a list-rules item to a rule operation from this script."""
    return (
        expected_rule.get("objectUri") == existing_rule.get("objectUri")
        and expected_rule.get("principalType")
        == existing_rule.get("principalType")
        and normalise_principal(expected_rule.get("principal"))
        == normalise_principal(existing_rule.get("principal"))
        and normalise_type(expected_rule.get("type"))
        == normalise_type(existing_rule.get("type"))
        and set(expected_rule.get("permissions", []))
        == set(existing_rule.get("permissions", []))
        and str(expected_rule.get("enabled", "")).lower()
        == str(existing_rule.get("enabled", "")).lower()
        and expected_rule.get("condition", "")
        == existing_rule.get("condition", "")
    )


def run_command(command):
    """Run a shell command quietly and return (code, combined output)."""
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    output = result.stdout or ""
    return result.returncode, output


def write_single_rule(path, rule_operation):
    """Write one create-rules operation as the one-element array it expects."""
    with open(path, "w") as output_file:
        json.dump([rule_operation], output_file, indent=2)
        output_file.write("\n")


def create_rules_command(clicommand, json_path):
    return (
        clicommand
        + " authorization create-rules --file "
        + shlex.quote(json_path)
    )


def update_rule_command(clicommand, rule_id, intended_object_uri):
    return (
        clicommand
        + " authorization update-rule -o "
        + shlex.quote(intended_object_uri)
        + " --id "
        + shlex.quote(rule_id)
    )


def list_rules_to_json(output_path):
    """Write listrules JSON to output_path and return execution diagnostics."""
    try:
        with open(output_path, "w") as output_file:
            result = subprocess.run(
                ["./listrules.py", "-o", "json", "--limit", "20000"],
                stdout=output_file,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
    except OSError as exc:
        return {
            "returncode": 1,
            "output": str(exc),
            "error": "Unable to run listrules.py: " + str(exc),
        }

    stderr_output = result.stderr or ""
    if stderr_output:
        print(stderr_output, end="" if stderr_output.endswith("\n") else "\n")

    if result.returncode != 0:
        return {
            "returncode": result.returncode,
            "output": stderr_output,
            "error": "listrules.py failed while looking up the temporary rule.",
        }

    return {"returncode": 0, "output": stderr_output, "error": ""}


def retrieve_temporary_rule_id(temp_rule, lookup_json_path):
    """Find exactly one temporary rule ID using disableviyarules-style matching."""
    list_result = list_rules_to_json(lookup_json_path)
    if list_result["returncode"] != 0:
        return {
            "rule_id": "",
            "returncode": list_result["returncode"],
            "output": list_result["output"],
            "error": list_result["error"],
        }

    try:
        with open(lookup_json_path, "r") as input_file:
            rule_data = json.load(input_file)
    except (OSError, ValueError) as exc:
        return {
            "rule_id": "",
            "returncode": 1,
            "output": list_result["output"],
            "error": "Unable to read list-rules JSON: " + str(exc),
        }

    existing_rules = rule_data.get("items", [])
    matches = []
    for existing_rule in existing_rules:
        # Match disableviyarules.py and ignore container rules.
        if existing_rule.get("containerUri"):
            continue
        if rule_matches(temp_rule, existing_rule):
            matches.append(existing_rule)

    if len(matches) != 1:
        return {
            "rule_id": "",
            "returncode": 1,
            "output": list_result["output"],
            "error": (
                "Expected exactly one temporary rule match, but found "
                + str(len(matches))
                + ". No rule was updated."
            ),
        }

    rule_id = matches[0].get("id", "")
    if not rule_id:
        return {
            "rule_id": "",
            "returncode": 1,
            "output": list_result["output"],
            "error": "The matching temporary rule did not contain an id.",
        }

    return {
        "rule_id": rule_id,
        "returncode": 0,
        "output": list_result["output"],
        "error": "",
    }


def failure_result(
    stage,
    reason,
    rule_operation,
    original_json_path,
    returncode,
    cli_output,
    original_output="",
    temp_uri="",
    temp_json_path="",
    temp_rule_id="",
    temp_created=False,
    temp_output="",
    lookup_json_path="",
    update_output="",
):
    """Build a consistent failure record for JSON/CSV reporting."""
    return {
        "success": False,
        "workaround": False,
        "operation": rule_operation,
        "failureStage": stage,
        "originalObjectUri": rule_operation["value"].get("objectUri", ""),
        "temporaryObjectUri": temp_uri,
        "temporaryRuleId": temp_rule_id,
        "temporaryRuleCreated": temp_created,
        "failureReason": reason,
        "cliReturnCode": returncode,
        "cliOutput": cli_output,
        "originalCliOutput": original_output,
        "temporaryCliOutput": temp_output,
        "updateCliOutput": update_output,
        "sourceJsonFile": original_json_path,
        "temporaryJsonFile": temp_json_path,
        "lookupJsonFile": lookup_json_path,
    }


def process_rule(
    rule_number,
    rule_operation,
    original_json_path,
    results_dir,
    runtime,
    clicommand,
    command_runner=None,
    rule_id_retriever=None,
):
    """Create one rule and apply the temporary-URI workaround when required."""
    if command_runner is None:
        command_runner = run_command
    if rule_id_retriever is None:
        rule_id_retriever = retrieve_temporary_rule_id

    original_command = create_rules_command(clicommand, original_json_path)
    original_returncode, original_output = command_runner(original_command)

    if not reported_zero_created(original_output):
        if original_returncode == 0:
            return {"success": True, "workaround": False}
        return failure_result(
            stage="original-create",
            reason="The create-rules command failed before the zero-created classifier could be used.",
            rule_operation=rule_operation, original_json_path=original_json_path,
            returncode=original_returncode, cli_output=original_output,
            original_output=original_output,
        )

    print("      Viya returned 0 rules; checking for uniqueness conflict...")
    intended_uri = rule_operation["value"].get("objectUri", "")
    temp_uri = "/applyconditionalrules-temp/" + runtime + "/" + str(os.getpid()) + "/" + str(rule_number)
    temp_operation = copy.deepcopy(rule_operation)
    temp_operation["value"]["objectUri"] = temp_uri
    temp_json_path = os.path.join(results_dir, "condrule_" + str(rule_number) + "_" + runtime + "_temporary_uri.json")
    write_single_rule(temp_json_path, temp_operation)

    temp_command = create_rules_command(clicommand, temp_json_path)
    temp_returncode, temp_output = command_runner(temp_command)
    temp_created_count = created_count(temp_output)

    if temp_created_count == 0:
        reason = "Invalid SpEL condition: create-rules returned 0 rules for both the intended and temporary URIs."
        return failure_result(
            stage="temporary-create", reason=reason, rule_operation=rule_operation,
            original_json_path=original_json_path, returncode=temp_returncode,
            cli_output=temp_output, original_output=original_output, temp_uri=temp_uri,
            temp_json_path=temp_json_path, temp_created=False, temp_output=temp_output,
        )

    if temp_created_count != 1:
        reason = "Temporary-URI retry did not report exactly 0 or 1 rules created; unable to classify safely."
        return failure_result(
            stage="temporary-create", reason=reason, rule_operation=rule_operation,
            original_json_path=original_json_path, returncode=temp_returncode,
            cli_output=temp_output, original_output=original_output, temp_uri=temp_uri,
            temp_json_path=temp_json_path, temp_created=False, temp_output=temp_output,
        )

    print("      Viya uniqueness conflict detected.")
    print("      Applying temporary-URI workaround...")
    print("      Temporary rule created.")
    lookup_json_path = os.path.join(results_dir, "temporary_rule_lookup_" + str(rule_number) + "_" + runtime + ".json")
    lookup_result = rule_id_retriever(temp_operation["value"], lookup_json_path)
    temp_rule_id = lookup_result.get("rule_id", "")

    if not temp_rule_id:
        reason = lookup_result.get("error", "The temporary rule ID could not be retrieved.")
        return failure_result(
            stage="temporary-rule-id-lookup", reason=reason, rule_operation=rule_operation,
            original_json_path=original_json_path, returncode=lookup_result.get("returncode", 1),
            cli_output=lookup_result.get("output", ""), original_output=original_output,
            temp_uri=temp_uri, temp_json_path=temp_json_path, temp_rule_id="",
            temp_created=True, temp_output=temp_output, lookup_json_path=lookup_json_path,
        )

    print("      Rule ID    : " + temp_rule_id)
    print("      Updating to intended URI...")
    update_command = update_rule_command(clicommand, temp_rule_id, intended_uri)
    update_returncode, update_output = command_runner(update_command)
    if update_returncode != 0:
        reason = "Temporary rule was created, but update-rule failed. The temporary rule was left in place for inspection."
        return failure_result(
            stage="object-uri-update", reason=reason, rule_operation=rule_operation,
            original_json_path=original_json_path, returncode=update_returncode,
            cli_output=update_output, original_output=original_output, temp_uri=temp_uri,
            temp_json_path=temp_json_path, temp_rule_id=temp_rule_id, temp_created=True,
            temp_output=temp_output, lookup_json_path=lookup_json_path, update_output=update_output,
        )

    return {"success": True, "workaround": True, "temporaryObjectUri": temp_uri, "temporaryRuleId": temp_rule_id}

def write_failure_reports(failures, results_dir, runtime):
    """Write retryable JSON plus detailed diagnostic CSV for all failures."""
    failed_rules_json = os.path.join(
        results_dir, "failed_conditional_rules_" + runtime + ".json"
    )
    failed_rules_csv = os.path.join(
        results_dir, "failed_conditional_rules_" + runtime + ".csv"
    )

    with open(failed_rules_json, "w") as output_file:
        json.dump([failure["operation"] for failure in failures], output_file, indent=2)
        output_file.write("\n")

    fieldnames = [
        "ruleNumber",
        "failureStage",
        "originalObjectUri",
        "temporaryObjectUri",
        "temporaryRuleId",
        "temporaryRuleCreated",
        "failureReason",
        "cliReturnCode",
        "cliOutput",
        "originalCliOutput",
        "temporaryCliOutput",
        "updateCliOutput",
        "sourceJsonFile",
        "temporaryJsonFile",
        "lookupJsonFile",
    ]
    with open(failed_rules_csv, "w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for failure in failures:
            writer.writerow({name: failure.get(name, "") for name in fieldnames})

    return failed_rules_json, failed_rules_csv


def document_existing_rules(results_dir):
    """Run listrules CSV and create the comparison file in results_dir."""
    verbose_path = os.path.join(results_dir, "existing_rules_verbose.csv")
    comparison_path = os.path.join(results_dir, "existing_rules.csv")

    try:
        with open(verbose_path, "w") as output_file:
            result = subprocess.run(
                ["./listrules.py", "-o", "csv"],
                stdout=output_file,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
    except OSError as exc:
        raise RuntimeError("Unable to run listrules.py: " + str(exc))

    if result.returncode != 0:
        raise RuntimeError(
            "listrules.py failed while documenting existing rules: "
            + (result.stderr or "")
        )

    dataframe = pd.read_csv(
        verbose_path,
        usecols=[
            "objectUri",
            "principalType",
            "principal",
            "setting",
            "permissions",
            "enabled",
            "condition",
        ],
    )
    dataframe["permissions"] = (
        dataframe["permissions"]
        .fillna("")
        .astype(str)
        .str[1:-1]
        .str.replace(" ", ",", regex=False)
    )
    dataframe = dataframe[
        [
            "objectUri",
            "principalType",
            "principal",
            "setting",
            "permissions",
            "enabled",
            "condition",
        ]
    ]
    dataframe["enabled"] = dataframe["enabled"].apply(lambda value: str(value))
    dataframe.to_csv(
        comparison_path, header=False, index=None, quoting=csv.QUOTE_NONNUMERIC
    )
    return verbose_path, comparison_path


def build_conditional_rules_file(input_file, comparison_file, results_dir, runtime):
    """Create the delta and conditional-rule CSV files under results_dir."""
    new_rules_path = os.path.join(results_dir, "rulesapplied_" + runtime + ".csv")
    conditional_rules_path = os.path.join(
        results_dir, "conditional_rules_" + runtime + ".csv"
    )

    with open(new_rules_path, "w") as output_file:
        grep_result = subprocess.run(
            ["grep", "-Fiv", "-f", comparison_file, input_file],
            stdout=output_file,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    # grep returns 1 when there are no selected lines; that is not an error here.
    if grep_result.returncode not in (0, 1):
        raise RuntimeError("grep comparison failed: " + (grep_result.stderr or ""))

    if os.path.getsize(new_rules_path) == 0:
        return new_rules_path, conditional_rules_path, 0

    try:
        dataframe = pd.read_csv(
            new_rules_path,
            quoting=csv.QUOTE_ALL,
            names=[
                "objectUri",
                "principalType",
                "principal",
                "setting",
                "permissions",
                "enabled",
                "condition",
            ],
        )
    except EmptyDataError:
        return new_rules_path, conditional_rules_path, 0

    dataframe = dataframe.fillna("")
    conditional_mask = dataframe["setting"].apply(
        lambda value: str(value).lower() == "grant"
        or "conditional" in str(value).lower()
    )
    condition_present_mask = dataframe["condition"].astype(str) != ""
    conditional_dataframe = dataframe[conditional_mask & condition_present_mask]

    if conditional_dataframe.empty:
        return new_rules_path, conditional_rules_path, 0

    conditional_dataframe.to_csv(
        conditional_rules_path,
        header=False,
        index=None,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    return new_rules_path, conditional_rules_path, len(conditional_dataframe)


def make_rule_operation(row):
    """Convert a seven-column CSV row into one create-rules operation."""
    access_setting = row[3].strip()
    if access_setting.lower().startswith("conditional "):
        access_setting = access_setting[len("conditional ") :]

    value = {
        "description": "Created by applyconditionalrules.py",
        "objectUri": row[0],
        "permissions": row[4].split(","),
        "principalType": row[1],
        "principal": row[2],
        "type": access_setting,
        "enabled": row[5],
        "condition": row[6],
    }
    return {"op": "add", "value": value}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Apply conditional Viya authorization rules from a CSV file"
    )
    parser.add_argument(
        "-f",
        "--file",
        help=(
            "Full path to CSV file. Format: objecturi,principaltype,"
            "principalid,grant_or_prohibit,perms,enabled,condition"
        ),
        required=True,
    )
    args = parser.parse_args(argv)
    input_file = args.file

    print("\napplyconditionalrules.py running...\n")
    if not file_accessible(input_file, "r"):
        print("ERROR: cannot read " + input_file)
        return 1

    clicommand = getclicommand()
    runtime = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.abspath(
        os.path.join(os.getcwd(), "applyconditionalrules_results")
    )
    os.makedirs(results_dir, exist_ok=True)

    print("All generated output will be written under: \033[1;34m" + results_dir + "\033[0m\n")
    print("Documenting existing rules... \n")
    try:
        _, comparison_file = document_existing_rules(results_dir)
    except (RuntimeError, OSError, ValueError) as exc:
        print("\033[1;31mERROR: " + str(exc) + "\033[0m")
        return 1

    print("Checking for new rules to apply... \n")
    try:
        _, conditional_rules_path, conditional_count = build_conditional_rules_file(
            input_file, comparison_file, results_dir, runtime
        )
    except (RuntimeError, OSError, ValueError) as exc:
        print("\033[1;31mERROR: " + str(exc) + "\033[0m")
        return 1

    if conditional_count == 0:
        print("There are \033[1;33mNO NEW CONDITIONAL RULES\033[0m to be applied. \n")
        return 0

    print(
        "\033[1;32mFound "
        + str(conditional_count)
        + "\033[0m NEW CONDITIONAL RULE(S) to be applied.\n"
    )

    failures = []
    created_rules = 0
    workaround_rules = 0
    rule_count = 0

    with open(conditional_rules_path, "r") as input_handle:
        file_contents = csv.reader(input_handle, skipinitialspace=True)
        for row in file_contents:
            rule_count += 1
            rule_operation = make_rule_operation(row)
            value = rule_operation["value"]
            single_rule_json = os.path.join(results_dir, "condrule_" + str(rule_count) + "_" + runtime + ".json")
            write_single_rule(single_rule_json, rule_operation)

            print("[" + str(rule_count) + "/" + str(conditional_count) + "] " + value.get("objectUri", ""))
            print("      Principal : " + str(value.get("principal", "")))
            print("      Permission: " + ", ".join(value.get("permissions", [])))
            print("      Applying rule...")

            outcome = process_rule(
                rule_number=rule_count, rule_operation=rule_operation,
                original_json_path=single_rule_json, results_dir=results_dir,
                runtime=runtime, clicommand=clicommand,
            )

            if outcome["success"]:
                created_rules += 1
                if outcome.get("workaround"):
                    workaround_rules += 1
                    print("      \033[1;32mSUCCESS: Conditional rule applied using temporary-URI workaround.\033[0m")
                else:
                    print("      \033[1;32mSUCCESS: Conditional rule applied.\033[0m")
            else:
                outcome["ruleNumber"] = rule_count
                failures.append(outcome)
                if outcome.get("failureStage") == "temporary-create" and "Invalid SpEL" in outcome.get("failureReason", ""):
                    print("      \033[1;31mFAILED: Invalid SpEL condition.\033[0m")
                    print("      Condition  : " + str(value.get("condition", "")))
                else:
                    print("      \033[1;31mFAILED: " + outcome["failureReason"] + "\033[0m")
            print()

    failed_rules_json = ""
    failed_rules_csv = ""
    if failures:
        failed_rules_json, failed_rules_csv = write_failure_reports(failures, results_dir, runtime)

    print("-" * 60)
    print("SUMMARY")
    print("-" * 60)
    print("Rules processed : " + str(rule_count))
    print("Applied         : " + str(created_rules))
    print("Failed          : " + str(len(failures)))
    print("Workarounds used: " + str(workaround_rules))

    if failures:
        print("\nFailed rule details:")
        print("  CSV : " + failed_rules_csv)
        print("  JSON: " + failed_rules_json)

    print("\nFinished.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
