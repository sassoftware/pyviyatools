#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# importpackages.py
# March 2018
#
# Import package files from a directory using the Viya transfer REST API.
#
# Copyright © 2019, SAS Institute Inc., Cary, NC, USA. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the License); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
import argparse
import json
import os
import sys
import time

from sharedfunctions import callrestapi


IMPORT_REQUEST_CONTENT_TYPE = "application/vnd.sas.transfer.import.request+json"
RUNNING_IMPORT_STATES = {"pending", "queued", "running"}


def load_mapping(mapping_path, exclude_authorization):
	if mapping_path:
		with open(mapping_path) as map_file:
			mapping_data = json.load(map_file)
		if not isinstance(mapping_data, dict):
			raise ValueError("Mapping file must contain a JSON object.")
	else:
		mapping_data = None

	if exclude_authorization:
		no_authorization_options = {
			"version": 1,
			"options": {"promoteAuthorization": False},
		}
		if mapping_data is None:
			mapping_data = no_authorization_options
		else:
			mapping_data.update(no_authorization_options)

	return mapping_data


def upload_and_start_import(package_path, mapping_data=None):
	filename = os.path.basename(package_path)
	with open(package_path, "rb") as package_file:
		package_data = callrestapi(
			"/transfer/packages",
			"postmultipart",
			acceptType="application/json",
			data={"file": (filename, package_file, "application/json")},
		)

	package_id = package_data.get("id") if isinstance(package_data, dict) else None
	if not package_id:
		raise RuntimeError("Transfer service did not return an uploaded package ID.")

	package_name = package_data.get("name") or os.path.splitext(filename)[0]
	import_request = {
		"version": 2,
		"name": package_name,
		"description": "",
		"packageUri": "/transfer/packages/" + package_id,
		"options": {},
	}
	if mapping_data is not None:
		import_request["mapping"] = mapping_data

	return callrestapi(
		"/transfer/importJobs",
		"post",
		acceptType="application/json",
		contentType=IMPORT_REQUEST_CONTENT_TYPE,
		data=import_request,
	)


def import_job_uri(job):
	for link in job.get("links", []):
		if link.get("rel") == "self":
			return link["href"]

	job_id = job.get("id")
	if not job_id:
		raise RuntimeError("Transfer service did not return an import job ID.")
	return "/transfer/importJobs/" + job_id


def wait_for_import(job, timeout=600, poll_interval=2):
	if not isinstance(job, dict):
		raise RuntimeError("Transfer service returned no import job status.")
	deadline = time.monotonic() + timeout
	while str(job.get("state", "")).lower() in RUNNING_IMPORT_STATES:
		if time.monotonic() >= deadline:
			raise RuntimeError("Timed out waiting for transfer import job " + str(job.get("id")))
		time.sleep(poll_interval)
		job = callrestapi(import_job_uri(job), "get")
		if not isinstance(job, dict):
			raise RuntimeError("Transfer service returned no import job status.")
	return job


def report_import(job):
	state = str(job.get("state", "unknown"))
	print("Import job ID: " + str(job.get("id", "unknown")))
	print("Import job state: " + state)

	tasks = callrestapi(import_job_uri(job) + "/tasks", "get")
	has_task_errors = False
	for task in tasks.get("items", []) if isinstance(tasks, dict) else []:
		task_state = str(task.get("state", "unknown"))
		if task_state.lower() != "completed":
			has_task_errors = True
			name = task.get("name") or task.get("resourceName") or task.get("id", "unknown")
			message = task.get("message", "")
			print("Import task " + str(name) + " state: " + task_state)
			if message:
				print(message)

	return 0 if state.lower() == "completed" and not has_task_errors else 1


def main(argv=None):
	parser = argparse.ArgumentParser(
		description="Import JSON files from directory. All package files in directory will be imported."
	)
	parser.add_argument("-d", "--directory", help="Directory that contains package files to import", required=True)
	parser.add_argument("-m", "--mapping", help="A mapping file to use with the import.", default=None)
	parser.add_argument("-ea", "--excludeauthorization", help="Exclude the import of authorization rules.", action="store_true")
	parser.add_argument("-q", "--quiet", help="Suppress the are you sure prompt.", action="store_true")
	args = parser.parse_args(argv)

	if not os.path.isdir(args.directory):
		print("ERROR: Directory does not exist")
		return 1

	if not args.quiet:
		prompt = "WARNING: If content from the packages already exists in folders it will be replaced. Continue? (Y)"
		if input(prompt).upper() != "Y":
			print("NOTE: Operation cancelled")
			return 0

	try:
		mapping_data = load_mapping(args.mapping, args.excludeauthorization)
	except (OSError, ValueError) as error:
		print("ERROR: Cannot read mapping file: " + str(error))
		return 1

	status = 0
	for filename in os.listdir(args.directory):
		if not filename.lower().endswith((".json", ".spk", ".egp")):
			continue

		package_path = os.path.join(args.directory, filename)
		try:
			job = upload_and_start_import(package_path, mapping_data)
			job = wait_for_import(job)
			if report_import(job):
				status = 1
			else:
				print("NOTE: Viya content imported from package " + filename)
		except (OSError, ValueError, RuntimeError) as error:
			print("ERROR: Import failed for " + filename + ": " + str(error))
			status = 1

	return status


if __name__ == "__main__":
	sys.exit(main())