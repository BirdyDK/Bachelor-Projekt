#!/usr/bin/env python3
"""
Display a selected row from quest_data.csv in a human‑readable format.
Usage: python display.py [row_number]
If no row number is given, shows the first row.
"""

import csv
import json
import sys
import os
from typing import Optional

def display_row(row_num: int, csv_path: str):
    """Print the given row (1‑based) in a nicely formatted way."""
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, quoting=csv.QUOTE_ALL)
            header = next(reader)  # skip header
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    if row_num < 1 or row_num > len(rows):
        print(f"Row {row_num} out of range. File has {len(rows)} rows.")
        sys.exit(1)

    row = rows[row_num - 1]   # 0‑based index
    # Unpack (in case some fields are empty, but we expect all five)
    world_json, player_json, atomic_json, quest_json, narrative = row

    # Helper to print a section
    def print_section(title: str, content: str, is_json: bool = True):
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
        if is_json:
            try:
                # Re‑parse and pretty‑print to be sure (though it should already be pretty)
                parsed = json.loads(content)
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                print(content)   # fallback to raw string
        else:
            print(content)

    print_section("WORLD STATE", world_json)
    print_section("PLAYER STATE", player_json)
    print_section("ATOMIC ACTIONS", atomic_json)
    print_section("QUEST STRUCTURE", quest_json)
    print_section("NARRATIVE", narrative, is_json=False)

def main():
    csv_path = os.path.join("quest_generator", "quest_data.csv")
    if len(sys.argv) > 1:
        try:
            row_num = int(sys.argv[1])
        except ValueError:
            print("Please provide a valid row number (integer).")
            sys.exit(1)
    else:
        row_num = 1   # default to first row

    display_row(row_num, csv_path)

if __name__ == "__main__":
    main()