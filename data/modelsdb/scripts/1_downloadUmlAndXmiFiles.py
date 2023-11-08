#!/usr/bin/env python3

import os
import sys
import time
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from threading import Lock

start_time = time.time()

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m"

def download_file(url, output_path):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        file_name = os.path.basename(urlparse(url).path)
        file_path = os.path.join(output_path, file_name)

        if os.path.isfile(file_path):
            return "exists"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return "downloaded"
    except requests.RequestException as e:
        #print(f"Download failed for {url}, error: {e}")
        return "failed"


def download_url(row, output_path, download_stats, lock, total_files):
    url = row.iloc[0]
    #print(f"Download url: {url}")
    result = download_file(url, output_path)
    current_time = time.time()

    with lock:  # Ensure thread-safe operations
        message = ""
        if result == "downloaded":
            download_stats["downloaded"] += 1
        elif result == "exists":
            download_stats["exists"] += 1
        else:
            len_before = len(download_stats["failed_urls"])
            #print(f"Increase failed counter from {len_before}")
            download_stats["failed"] += 1
            download_stats["failed_urls"].add(url)
            len_after = len(download_stats["failed_urls"])
            #print(f"to {len_after}")

        elapsed_time = current_time - start_time
        completed = download_stats['downloaded'] + download_stats['exists'] + download_stats['failed']
        remaining = total_files - completed
        estimated_total_time = elapsed_time / completed * total_files if completed > 0 else 0
        estimated_remaining_time = estimated_total_time - elapsed_time
        
        message = f"Downloaded: {download_stats['downloaded']} / Already downloaded: {download_stats['exists']} / Failed: {download_stats['failed']} - completed {completed} out of {total_files} files."
        message += f" Elapsed time: {format_time(elapsed_time)}. Estimated time remaining: {format_time(estimated_remaining_time)}."

        print(message)

def process_excel_file(file_path, output_path, download_stats, lock, total_files):
    try:
        xls = pd.ExcelFile(file_path)
        #print(f"Process exel file: {file_path}")
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for sheet_name in xls.sheet_names:
                #print(f"Process sheet: {sheet_name}")
                combined_output_path = os.path.join(output_path, sheet_name.replace(" ", "_").replace(".", "_"))
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)  # No header as columns are unnamed

                for _, row in df.iterrows():
                    futures.append(executor.submit(download_url, row, combined_output_path, download_stats, lock, total_files))
            for future in as_completed(futures):
                future.result()  # This will re-raise any exceptions caught
    except Exception as e:
        with lock:  # Ensure thread-safe operation on the shared download_stats object
            download_stats["failed_urls"].add(str(file_path) + ": " + str(e))

def main():
    start_time = time.time()

    if len(sys.argv) != 3:
        print("Usage: python script.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    failed_downloads_path = "failed_downloads.txt"

    if not os.path.exists(input_path):
        print(f"Error: The specified input path does not exist: {input_path}")
        sys.exit(1)

    download_stats = {"downloaded": 0, "exists": 0, "failed": 0, "failed_urls": set()}
    lock = Lock()  # Lock for synchronizing access to download_stats

    xlsx_files = [f for f in os.listdir(input_path) if f.endswith(".xlsx")]
    total_files = 0

    for file in xlsx_files:
        file_path = os.path.join(input_path, file)
        print(f"Count item in file: {file_path}")
        try:
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)  # No header as columns are unnamed
                items_in_sheet = len(df)
                #print(f"Found in that sheet {sheet_name} {items_in_sheet}")
                total_files += items_in_sheet
        except Exception as e:
            with lock:  # Ensure thread-safe operation on the shared download_stats object
                download_stats["failed_urls"].add(str(file_path) + ": " + str(e))

    print(f"Total items found to download/check: {total_files}")

    for file in xlsx_files:
        file_path = os.path.join(input_path, file)
        process_excel_file(file_path, output_path, download_stats, lock, total_files)

    # Write the failed downloads to a file
    with open(failed_downloads_path, 'w') as f:
        for item in download_stats["failed_urls"]:
            f.write("%s\n" % item)

    elapsed_time = time.time() - start_time
    print(f"{download_stats['downloaded']} downloaded / {download_stats['exists']} already existed / {download_stats['failed']} failed out of {total_files} files processed in {format_time(elapsed_time)}.")

if __name__ == "__main__":
    main()
