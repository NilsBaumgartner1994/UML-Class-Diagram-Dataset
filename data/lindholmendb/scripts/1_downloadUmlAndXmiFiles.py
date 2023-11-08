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

def github_url_to_raw(url):
    #print("github_url_to_raw")
    # Split the URL into parts
    parts = url.split('/')
    #print("Url splitted")
    
    # Check if URL is a valid GitHub URL
    if not url.startswith("https://www.github.com/") and not url.startswith("https://github.com/"):
        print("Not valid github URL")
        raise ValueError("URL must start with 'https://www.github.com/' or 'https://github.com/'")

    # Extract the parts of the URL needed to construct the raw URL
    #print("extract the parts")
    user = parts[3]
    repository = parts[4]
    branch = parts[parts.index("tree") + 1]

    # Construct the path to the file
    file_path = '/'.join(parts[parts.index(branch) + 1:])

    #print("Construct")

    # Construct the raw URL
    raw_url = f"https://raw.githubusercontent.com/{user}/{repository}/{branch}/{file_path}"

    #print("Final url: "+raw_url)

    return raw_url

def download_file(url, output_path):
    # Check if url ends with .xml .xmi .uml

    _, extension = os.path.splitext(url)
    if extension.lower() not in ['.xml', '.xmi', '.uml']:
        return "skipped"


    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        #print("Before replace: "+url)
        raw_url = github_url_to_raw(url)

        # from                https://github.com/0003088/libelektra-qt-gui-test/blob/master/doc/images/overview_plugins.xmi
        # to   https://raw.githubusercontent.com/0003088/libelektra-qt-gui-test/tree/master/doc/images/overview_plugins.xmi
        #print("After replace: "+raw_url)
        # Format the filename based on the URL
        file_name = url.replace(":", "_").replace("/", "_")
        file_path = os.path.join(output_path, file_name)

        if os.path.isfile(file_path):
            return "exists"

        response = requests.get(raw_url, timeout=10)
        response.raise_for_status()

        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return "downloaded"
    except requests.RequestException as e:
        #print(f"Download failed for {url}, error: {e}")
        return "failed"


def download_url(url, output_path, download_stats, lock, total_files):
    #print(f"Download url: {url}")
    result = download_file(url, output_path)
    current_time = time.time()

    with lock:  # Ensure thread-safe operations
        if result == "downloaded":
            download_stats["downloaded"] += 1
        elif result == "exists":
            download_stats["exists"] += 1
        elif result == "skipped":
            download_stats["skipped"] += 1
        else:
            download_stats["failed"] += 1
            download_stats["failed_urls"].add(url)

        elapsed_time = current_time - start_time
        completed = download_stats['downloaded'] + download_stats['exists'] + download_stats['failed'] + download_stats['skipped']
        remaining = total_files - completed
        estimated_total_time = elapsed_time / completed * total_files if completed > 0 else 0
        estimated_remaining_time = estimated_total_time - elapsed_time

        
        
        message = f"Skipped: {download_stats['skipped']} - Downloaded: {download_stats['downloaded']} / Already downloaded: {download_stats['exists']} / Failed: {download_stats['failed']} - completed {completed} out of {total_files} files."
        message += f" Elapsed time: {format_time(elapsed_time)}. Estimated time remaining: {format_time(estimated_remaining_time)}."

        print(message)

def process_csv_file(file_path, output_path, download_stats, lock):
    try:
        print(f"Read file {file_path}")
        df = pd.read_csv(file_path)
        total_files = len(df)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(download_url, url, output_path, download_stats, lock, total_files) for url in df['Model Link - Github']]
            for future in as_completed(futures):
                future.result()  # This will re-raise any exceptions caught
    except Exception as e:
        with lock:  # Ensure thread-safe operation on the shared download_stats object
            download_stats["failed_urls"].add(str(file_path) + ": " + str(e))

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <csv_file_path> <output_path>")
        sys.exit(1)

    print(f"Get CSV File")
    csv_file_path = sys.argv[1]
    output_path = sys.argv[2]
    failed_downloads_path = "failed_downloads.txt"

    if not os.path.exists(csv_file_path):
        print(f"Error: The specified CSV file does not exist: {csv_file_path}")
        sys.exit(1)

    download_stats = {"downloaded": 0, "skipped": 0, "exists": 0, "failed": 0, "failed_urls": set()}
    lock = Lock()  # Lock for synchronizing access to download_stats

    print(f"Start process csv file")
    process_csv_file(csv_file_path, output_path, download_stats, lock)

    # Write the failed downloads to a file
    with open(failed_downloads_path, 'w') as f:
        for item in download_stats["failed_urls"]:
            f.write("%s\n" % item)

    elapsed_time = time.time() - start_time
    print(f"{download_stats['downloaded']} downloaded / {download_stats['exists']} already existed / {download_stats['failed']} failed in {format_time(elapsed_time)}.")

if __name__ == "__main__":
    main()
