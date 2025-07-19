#!/usr/bin/env python3
import csv
import os
import re
from datetime import datetime


def parse_date(date_str):
    """Convert mm/dd/yy format to yyyy-mm-dd format"""
    if not date_str or date_str.strip() == "":
        return ""

    # Handle the case where date is in mm/dd/yy format
    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2})", date_str.strip())
    if match:
        month, day, year = match.groups()
        # Convert 2-digit year to 4-digit year
        # Assuming years 00-50 are 2000-2050, years 51-99 are 1951-1999
        year_int = int(year)
        if year_int <= 50:
            full_year = 2000 + year_int
        else:
            full_year = 1900 + year_int

        return f"{full_year:04d}-{int(month):02d}-{int(day):02d}"

    return ""


def parse_period(period_str):
    """Parse the period string and return start and end dates"""
    # Remove HTML entities
    period_clean = period_str.replace("&ndash;", "–").strip()

    # Handle the current period case (no end date)
    if period_clean.endswith("–") or period_clean.endswith("—"):
        # Extract start date only
        start_part = period_clean.rstrip("–—").strip()
        start_date = parse_date(start_part)
        return start_date, ""

    # Split by various dash characters
    parts = re.split(r"[–—-]", period_clean, maxsplit=1)
    if len(parts) == 2:
        start_date = parse_date(parts[0].strip())
        end_date = parse_date(parts[1].strip())
        return start_date, end_date

    # If only one part, treat as start date
    return parse_date(parts[0].strip()), ""


# Read the markdown file and extract table data
table_data = []

with open("/Users/monodera/tmp/hscfeu_doc/HSC_FEU_config.md", "r") as f:
    lines = f.readlines()

# Find the table section
in_table = False
for line in lines:
    line = line.strip()

    # Skip empty lines and header separator
    if not line or line.startswith("| :---"):
        continue

    # Check if this is a table header line
    if line.startswith("| Periods (mm/dd/yy)"):
        in_table = True
        continue

    # Process table data rows
    if in_table and line.startswith("|"):
        # Split by | and clean up
        parts = [part.strip() for part in line.split("|")]
        # Remove empty first and last elements
        if parts[0] == "":
            parts = parts[1:]
        if parts and parts[-1] == "":
            parts = parts[:-1]

        if len(parts) >= 7:  # Should have 7 columns
            period_str = parts[0]
            opt_top = parts[1]
            opt_mid = parts[2]
            opt_bot = parts[3]
            ir_top = parts[4]
            ir_mid = parts[5]
            ir_bot = parts[6]

            # Parse the period
            start_date, end_date = parse_period(period_str)

            table_data.append(
                [
                    start_date,
                    end_date,
                    opt_top,
                    opt_mid,
                    opt_bot,
                    ir_top,
                    ir_mid,
                    ir_bot,
                ]
            )

# Write to CSV file
output_path = "/Users/monodera/tmp/hscfeu_doc/docs/hsc_feu_configuration.csv"

# Create the docs directory if it doesn't exist
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write header
    writer.writerow(
        [
            "date_begin",
            "date_end",
            "opt_top",
            "opt_mid",
            "opt_bot",
            "ir_top",
            "ir_mid",
            "ir_bot",
        ]
    )

    # Write data
    for row in table_data:
        writer.writerow(row)

print(f"Successfully converted table to CSV: {output_path}")
print(f"Total rows: {len(table_data)}")
