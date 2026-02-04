#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# comparecontent.py
# Sep 2024 (updated Feb 2026)
#
# Compare two content list CSV files and report differences.
# - Validates header match (or match after dropping date columns).
# - Can ignore creationTimeStamp and modifiedTimeStamp.
# - Compares order-insensitive (so different row ordering does not count as a difference).
#
# usage:
#   python comparecontent.py --file1 <path> --file2 <path> [--file1label <label>] [--file2label <label>] [-d|--debug] [--ignore-dates]
#

import argparse
import csv
import io
import os
import sys
from collections import Counter


def read_lines(path):
    """Read file as a list of lines with normalized newlines, skipping empty lines."""
    with open(path, "r", newline="") as f:
        # splitlines() removes \n and \r\n cleanly
        lines = f.read().splitlines()
    # drop completely empty lines
    return [ln for ln in lines if ln.strip()]


def parse_header(line):
    """Parse a CSV header line into a list of column names (raw + stripped)."""
    cols = next(csv.reader([line]))
    stripped = [c.strip() for c in cols]
    return cols, stripped


def row_to_line(row):
    """Render a CSV row consistently (stable quoting + stable newline)."""
    sio = io.StringIO()
    csv.writer(sio, lineterminator="\n").writerow(row)
    return sio.getvalue()


def normalize_body(lines, drop_cols=None):
    """
    Normalize body lines:
    - Parse CSV rows
    - Drop drop_cols indices (if provided)
    - Render back to consistent CSV lines
    Returns:
      norm_lines: list[str] normalized rows
      norm_to_orig: dict[str, list[str]] mapping normalized line -> original line(s)
    """
    if drop_cols is None:
        drop_cols = set()
    else:
        drop_cols = set(drop_cols)

    norm_lines = []
    norm_to_orig = {}

    for orig in lines:
        # parse a row safely
        row = next(csv.reader([orig]))
        kept = [v for i, v in enumerate(row) if i not in drop_cols]
        norm = row_to_line(kept)
        norm_lines.append(norm)
        norm_to_orig.setdefault(norm, []).append(orig)

    return norm_lines, norm_to_orig


def multiset_diff(norm1, map1, norm2, map2):
    """
    Order-insensitive comparison with duplicate support.
    Returns lists of original lines only in file1 and only in file2.
    """
    c1 = Counter(norm1)
    c2 = Counter(norm2)

    only1 = []
    only2 = []

    # For deterministic output, iterate sorted keys
    for norm in sorted((c1 - c2).keys()):
        needed = (c1 - c2)[norm]
        only1.extend(map1.get(norm, [norm])[:needed])

    for norm in sorted((c2 - c1).keys()):
        needed = (c2 - c1)[norm]
        only2.extend(map2.get(norm, [norm])[:needed])

    return only1, only2


def main():
    parser = argparse.ArgumentParser(description="Compare two content lists.")
    parser.add_argument("-f1", "--file1", required=True, help="Full path to the first content file.")
    parser.add_argument("-f2", "--file2", required=True, help="Full path to the second content file.")
    parser.add_argument("-f1l", "--file1label", default="First file.", help="Optional label for file1.")
    parser.add_argument("-fl2", "--file2label", default="Second file.", help="Optional label for file2.")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug output")
    parser.add_argument("--ignore-dates", action="store_true",
                        help="Ignore creationTimeStamp and modifiedTimeStamp columns when comparing")
    parser.add_argument("--ignore-ownership", action="store_true",
                        help="Ignore createdByand modifiedBy columns when comparing")                    

    args = parser.parse_args()

    file1 = args.file1
    file2 = args.file2
    label1 = args.file1label
    label2 = args.file2label

    if not os.path.exists(file1):
        print(f"ERROR: The file '{file1}' does not exist.")
        sys.exit(2)

    if not os.path.exists(file2):
        print(f"ERROR: The file '{file2}' does not exist.")
        sys.exit(2)

    lines1 = read_lines(file1)
    lines2 = read_lines(file2)

    if not lines1 or not lines2:
        print("ERROR: One or both files are empty (or contain only blank lines).")
        sys.exit(2)

    # Parse headers
    header1_raw, header1 = parse_header(lines1[0])
    header2_raw, header2 = parse_header(lines2[0])

    # Decide which columns to drop (by name)
    drop_cols = []
    if args.ignore_dates:

        date_cols = {"creationTimeStamp", "modifiedTimeStamp"}

        if args.ignore_ownership: date_cols = {"creationTimeStamp", "modifiedTimeStamp","createdBy","modifiedby"}

        drop_cols = [i for i, name in enumerate(header1) if name in date_cols]

        # Validate header equality AFTER dropping date columns
        h1_dropped = [c for i, c in enumerate(header1) if i not in drop_cols]
        h2_dropped = [c for i, c in enumerate(header2) if i not in drop_cols]
        if h1_dropped != h2_dropped:
            print("ERROR: Headers do not match after dropping date columns.")
            if args.debug:
                print("DEBUG: header1_dropped:", h1_dropped)
                print("DEBUG: header2_dropped:", h2_dropped)
            sys.exit(2)
    else:
        # Validate header equality EXACTLY (original behavior)
        if lines1[0] != lines2[0]:
            print("ERROR: Files must have a matching header line in the first line.")
            if args.debug:
                print("DEBUG: file1 header:", lines1[0])
                print("DEBUG: file2 header:", lines2[0])
            sys.exit(2)

    # Normalize bodies
    body1 = lines1[1:]
    body2 = lines2[1:]

    if args.ignore_dates:
        norm1, map1 = normalize_body(body1, drop_cols=drop_cols)
        norm2, map2 = normalize_body(body2, drop_cols=drop_cols)
    else:
        # Still normalize line endings & CSV formatting to reduce false diffs
        norm1, map1 = normalize_body(body1, drop_cols=[])
        norm2, map2 = normalize_body(body2, drop_cols=[])

    # Compare order-insensitive
    only_in_file1, only_in_file2 = multiset_diff(norm1, map1, norm2, map2)

    print(f"NOTE: Compare the content of file1 ({label1}) and file2 ({label2})")
    print("NOTE: SUMMARY")
    if only_in_file1:
        print(f"NOTE: There is content in file1 ({label1}) that is not in file2 ({label2}).")
    if only_in_file2:
        print(f"NOTE: There is content in file2 ({label2}) that is not in file1 ({label1}).")

    if only_in_file1 or only_in_file2:
        print("NOTE: DETAILS")
    else:
        print("NOTE: Files are the same.")

    # Print header line for context
    if only_in_file1:
        print(f"NOTE: The content listed below is in file1 ({label1}) but not in file2 ({label2}):")
        print(lines1[0])
        for line in only_in_file1:
            print(line)

    if only_in_file2:
        print(f"NOTE: The content listed below is in file2 ({label2}) but not in file1 ({label1}):")
        print(lines2[0])
        for line in only_in_file2:
            print(line)

    if args.debug:
        print("DEBUG: rows file1:", len(body1))
        print("DEBUG: rows file2:", len(body2))
        print("DEBUG: ignore_dates:", args.ignore_dates)
        print("DEBUG: drop_cols:", drop_cols)


if __name__ == "__main__":
    main()
