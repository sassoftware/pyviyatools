#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# removecaslibs.py
# Delete CASLIBs defined by JSON files in a directory (follows importcaslibs.py pattern)
#
# Usage: removecaslibs.py -d <directory> [-q] [-su] [-v]
#
import argparse, sys, subprocess, os, json, shlex
from sharedfunctions import callrestapi, getapplicationproperties, file_accessible, getclicommand

parser = argparse.ArgumentParser(description="Delete CASLIBs defined in JSON files in a directory.")
parser.add_argument("-d","--directory", help="Directory containing JSON caslib definition files", required=True)
parser.add_argument("-q","--quiet", help="Suppress the are you sure prompt.", action='store_true')
parser.add_argument("-su","--superuser", help="Run commands with superuser permissions.", action='store_true')
parser.add_argument("-v","--verbose", help="Show merged stdout/stderr for successful commands.", action='store_true')
args = parser.parse_args()

basedir = args.directory
quietmode = args.quiet
su = args.superuser
verbose = args.verbose

clicommand = getclicommand()

version = int(str(sys.version_info[0]))

if not quietmode:
    if version > 2:
        areyousure = input("WARNING: This will DELETE caslibs. Are you sure? (Y)")
    else:
        areyousure = raw_input("WARNING: This will DELETE caslibs. Are you sure? (Y)")
else:
    areyousure = "Y"

trydelete = 0

if areyousure.upper() == 'Y':
    if os.path.isdir(basedir):
        for filename in os.listdir(basedir):
            fullfile = os.path.join(basedir, filename)
            if filename.lower().endswith('.json'):
                if '_authorization_' in filename:
                    # skip authorization files
                    continue

                with open(fullfile) as json_file:
                    try:
                        data = json.load(json_file)
                    except Exception as e:
                        print("ERROR: Failed to parse JSON file {}".format(filename))
                        print(str(e))
                        continue

                if 'name' not in data or 'server' not in data:
                    print("ERROR: Missing required keys in file {}".format(filename))
                    continue

                caslibname = data['name']
                casserver = data['server']

                # build safe argument list for subprocess
                cmd_args = [clicommand, 'cas', 'caslibs', 'delete', '--server', casserver, '--name', caslibname, '--force']
                if su:
                    # insert --su before --server
                    if '--server' in cmd_args:
                        cmd_args.insert(cmd_args.index('--server'), '--su')
                    else:
                        cmd_args.insert(3, '--su')

                print("NOTE: Viya Caslib delete attempted for caslib {} (file {})".format(caslibname, filename))
                print("RUN: " + ' '.join(shlex.quote(str(a)) for a in cmd_args))

                try:
                    result = subprocess.run(
                        cmd_args,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                    print("RETURN CODE: " + str(result.returncode))
                    if result.returncode != 0:
                        if result.stdout:
                            print("OUTPUT:")
                            print(result.stdout)
                        print("ERROR: Command failed for file {}".format(filename))
                        continue
                    else:
                        if result.stdout:
                            if verbose:
                                print("OUTPUT:")
                            else:
                                print("STDOUT:")
                            print(result.stdout)
                except Exception as e:
                    print("ERROR executing command for file {}".format(filename))
                    print(str(e))
                    continue

                trydelete += 1

        if not trydelete:
            print("NOTE: No caslib files were deleted.")
    else:
        print("ERROR: Directory does not exist.")
else:
    print("NOTE: Operation cancelled.")