#!/usr/bin/env python3
"""
Script to clean up CSV files and create just two files with specifications:
- With tags
- About 1% invalid cycle time (<= 0)
- No grp column
- No date columns
"""

import pandas as pd
import numpy as np
import os
import shutil


def create_clean_csv(input_file, output_file, target_percentage=0.01):
    """
    Create a clean CSV file with the specified requirements

    Args:
        input_file (str): Path to input CSV file with tags
        output_file (str): Path to output CSV file
        target_percentage (float): Target percentage of rows with cycle_time <= 0 to keep
    """

    print(f"Processing {input_file}...")

    # Read the data
    df = pd.read_csv(input_file)

    print(f"Original data shape: {df.shape}")
    print(f"Original columns: {df.columns.tolist()}")

    # Keep only id, cycle_time_days, and tags columns
    if "tags" in df.columns:
        df = df[["id", "cycle_time_days", "tags"]].copy()
    else:
        print(f"Warning: No 'tags' column found in {input_file}")
        return None

    print(f"After column filtering: {df.shape}")

    # Split data into two groups
    zero_or_negative = df[df["cycle_time_days"] <= 0].copy()
    positive = df[df["cycle_time_days"] > 0].copy()

    print(
        f"  - Rows with cycle_time <= 0: {len(zero_or_negative)} ({len(zero_or_negative)/len(df)*100:.2f}%)"
    )
    print(
        f"  - Rows with cycle_time > 0: {len(positive)} ({len(positive)/len(df)*100:.2f}%)"
    )

    # Calculate how many rows to keep from zero_or_negative group
    target_count = int(len(df) * target_percentage)
    current_zero_count = len(zero_or_negative)

    if target_count >= current_zero_count:
        print(
            f"Warning: Target count ({target_count}) >= current zero/negative count ({current_zero_count})"
        )
        print("Keeping all zero/negative rows")
        filtered_zero = zero_or_negative
    else:
        # Randomly sample the target percentage of zero/negative rows
        filtered_zero = zero_or_negative.sample(n=target_count, random_state=42)
        print(
            f"Sampling {target_count} rows from {current_zero_count} zero/negative rows"
        )

    # Combine the filtered data
    filtered_df = pd.concat([filtered_zero, positive], ignore_index=True)

    # Reset index for clean numbering
    filtered_df = filtered_df.reset_index(drop=True)

    print(f"\nFiltered data shape: {filtered_df.shape}")
    print(f"Filtered data info:")
    print(f"  - Total rows: {len(filtered_df)}")

    # Recalculate statistics
    filtered_zero_count = len(filtered_df[filtered_df["cycle_time_days"] <= 0])
    filtered_positive_count = len(filtered_df[filtered_df["cycle_time_days"] > 0])

    print(
        f"  - Rows with cycle_time <= 0: {filtered_zero_count} ({filtered_zero_count/len(filtered_df)*100:.2f}%)"
    )
    print(
        f"  - Rows with cycle_time > 0: {filtered_positive_count} ({filtered_positive_count/len(filtered_df)*100:.2f}%)"
    )

    # Save the filtered data
    print(f"Saving to {output_file}...")
    filtered_df.to_csv(output_file, index=False)
    print("Done!")

    return filtered_df


def main():
    # Create backup directory
    backup_dir = "data/backup"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")

    # Move all existing CSV files to backup
    csv_files = [f for f in os.listdir("data") if f.endswith(".csv")]
    for csv_file in csv_files:
        src = os.path.join("data", csv_file)
        dst = os.path.join(backup_dir, csv_file)
        shutil.move(src, dst)
        print(f"Moved {csv_file} to backup")

    # Create the two clean files
    print("\n" + "=" * 50)
    print("Creating clean CSV files...")
    print("=" * 50)

    # File 1: Based on data_with_tags.csv
    input_file1 = os.path.join(backup_dir, "data_with_tags.csv")
    output_file1 = "data/data1.csv"

    if os.path.exists(input_file1):
        df1 = create_clean_csv(input_file1, output_file1, target_percentage=0.01)
    else:
        print(f"Error: {input_file1} not found in backup!")
        return

    print("\n" + "=" * 50)

    # File 2: Based on data2_with_tags.csv
    input_file2 = os.path.join(backup_dir, "data2_with_tags.csv")
    output_file2 = "data/data2.csv"

    if os.path.exists(input_file2):
        df2 = create_clean_csv(input_file2, output_file2, target_percentage=0.01)
    else:
        print(f"Error: {input_file2} not found in backup!")
        return

    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    print(f"Created 2 clean CSV files:")
    print(f"1. {output_file1} - {len(df1)} rows")
    print(f"2. {output_file2} - {len(df2)} rows")
    print(f"\nAll original files moved to {backup_dir}/")
    print(f"New files contain only: id, cycle_time_days, tags")
    print(f"Each file has ~1% rows with cycle_time <= 0")


if __name__ == "__main__":
    main()
