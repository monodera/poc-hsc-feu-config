#!/usr/bin/env python3
"""
Script to fetch HSC FEU configuration from remote CSV and find configuration for a specific date.

Usage:
    python fetch_hsc_feu_config.py [date] [--url URL]

Arguments:
    date: Date in YYYY-MM-DD format (defaults to today if not provided)

Options:
    --url URL: URL to fetch the CSV data from

Examples:
    python fetch_hsc_feu_config.py 2025-07-15
    python fetch_hsc_feu_config.py  # Uses today's date
    python fetch_hsc_feu_config.py --url https://example.com/custom.csv
"""

import argparse
import sys
from datetime import datetime
from typing import Optional

import pandas as pd


def fetch_csv_data(url: str) -> Optional[pd.DataFrame]:
    """
    Fetch CSV data from the given URL and return as pandas DataFrame.

    Args:
        url: URL to fetch the CSV data from

    Returns:
        DataFrame with the CSV data, or None if fetching fails
    """
    try:
        df = pd.read_csv(url)

        # Convert date columns to datetime, specifying format and handling empty/invalid dates
        # The CSV uses YYYY-MM-DD format for dates
        df["Date Begin"] = pd.to_datetime(
            df["Date Begin"], format="%Y-%m-%d", errors="coerce"
        )
        df["Date End"] = pd.to_datetime(
            df["Date End"], format="%Y-%m-%d", errors="coerce"
        )

        return df

    except Exception as e:
        print(f"Error fetching data from {url}: {e}", file=sys.stderr)
        return None


def find_configuration_for_date(
    df: pd.DataFrame, target_date: datetime
) -> Optional[pd.Series]:
    """
    Find the configuration row that contains the target date using pandas operations.

    Args:
        df: DataFrame containing configuration data
        target_date: Target date to find configuration for

    Returns:
        Series containing the configuration row, or None if not found
    """
    if df is None or df.empty:
        return None

    target_date = pd.to_datetime(target_date)

    # Find rows where target_date falls within the date range
    # Handle cases where end_date is NaT (ongoing configuration)
    mask = (df["Date Begin"] <= target_date) & (
        df["Date End"].isna() | (df["Date End"] >= target_date)
    )

    matching_rows = df[mask]

    if not matching_rows.empty:
        # Sort by Date Begin descending to get the most recent configuration
        # that was active on the target date
        sorted_rows = matching_rows.sort_values("Date Begin", ascending=False)
        return sorted_rows.iloc[0]

    return None


def format_configuration_output(config: Optional[pd.Series]) -> str:
    """
    Format configuration data for readable output.

    Args:
        config: Configuration Series

    Returns:
        Formatted string representation of the configuration
    """
    if config is None:
        return "No configuration found for the specified date."

    output = []
    output.append("HSC FEU Configuration:")
    output.append("=" * 30)

    for key, value in config.items():
        # Format dates nicely, handle NaT values
        if pd.isna(value):
            value_str = "N/A"
        elif isinstance(value, pd.Timestamp):
            value_str = value.strftime("%Y-%m-%d")
        else:
            value_str = str(value)

        output.append(f"{key:<12}: {value_str}")

    return "\n".join(output)


def main():
    """Main function to handle command line arguments and execute the script."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Fetch HSC FEU configuration for a specific date",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_hsc_feu_config.py 2025-07-15
  python fetch_hsc_feu_config.py  # Uses today's date
        """,
    )

    parser.add_argument(
        "date",
        nargs="?",  # Make date optional
        help="Date in YYYY-MM-DD format (defaults to today if not provided)",
    )

    parser.add_argument(
        "--url",
        default="https://www.naoj.org/staff/monodera/hsc_feu_config/hsc_feu_configuration.csv",
        help="URL to fetch the CSV data from (default: %(default)s)",
    )

    args = parser.parse_args()

    # Get target date from command line argument or use today
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(
                f"Error: Invalid date format '{args.date}'. Please use YYYY-MM-DD format.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        target_date = datetime.now()
        print(f"No date provided, using today: {target_date.strftime('%Y-%m-%d')}")

    print(f"Fetching configuration for date: {target_date.strftime('%Y-%m-%d')}")
    print(f"From URL: {args.url}")
    print()

    # Fetch CSV data
    data = fetch_csv_data(args.url)
    if data is None:
        print("Failed to fetch or parse CSV data.", file=sys.stderr)
        sys.exit(1)

    # At this point, data is guaranteed to be a DataFrame
    assert data is not None  # Type hint for static analysis
    print(f"Successfully fetched {len(data)} configuration entries.")
    print()

    # Find configuration for the target date
    config = find_configuration_for_date(data, target_date)

    # Output results
    print(format_configuration_output(config))

    if config is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
