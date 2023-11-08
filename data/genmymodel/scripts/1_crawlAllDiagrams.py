
# Print "getting information about amount projects"
# Get the amount of all pages/diagrams


# 1. Get total amount of projects from: https://app.genmymodel.com/api/projects/public?limit=12&page=0&type=UML&minDataSize=10000
# Example answer
# {"links":[{"rel":"next","href":"https:?limit=12&page=1"}],"elements":[{"links":[{"rel":"self","href":"https://app.genmymodel.com/api/projects/_ytpisGxPEe6A45N60iXn8g"},....],"totalPages":13002,"pageNumber":0,"rowsPerPage":0,"totalElements":156017}
# Print totalElements


# Now loop over all pages/items:
    # Print progress: Fetching: #Project / #TotalProjects - #Page/#TotalPages

    # Try Catch

        # #URL from GenMyModel:
            # https://app.genmymodel.com/api/projects/public?limit=12&page=0&type=UML&minDataSize=10000


        # Example element: "href":"https://app.genmymodel.com/api/projects/_ytpisGxPEe6A45N60iXn8g"


        # Now get the xmi file content from url: https://app.genmymodel.com/api/projects/_ytpisGxPEe6A45N60iXn8g/custom-xmi
        # Replace "_ytpisGxPEe6A45N60iXn8g" with the current key of the project

    # Print success of current save or not

    # Save it into the folder "UML-Diagrams"



import requests
import os
import concurrent.futures
import time
import sys
from threading import Lock
from datetime import timedelta

ITEMS_PER_PAGE = 100
MAX_CONCURRENT_DOWNLOADS = 20
START_PAGE = 0  # You can change this value to your desired starting page

def format_time(seconds):
    # Convert seconds to hours and minutes, then format as XXh YYm
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m"



def save_xmi_file(project_id, counter, lock):
    file_path = f"1_UML-Diagrams/{project_id}.xmi"
    if not os.path.exists(file_path):  # Check if file does not exist
        xmi_url = f"https://app.genmymodel.com/api/projects/{project_id}/custom-xmi"
        try:
            response = requests.get(xmi_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                with lock:  # Synchronize the counter increment
                    counter[0] += 1
                    print(f"Saved XMI for project {project_id}. Processed count: {counter[0]}")
            else:
                print(f"Failed to retrieve XMI for project {project_id}: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}", file=sys.stderr)
    else:
        print(f"XMI file for project {project_id} already exists. Skipping download.")


def get_total_projects():
    print("Getting information about the amount of projects")
    url = f"https://app.genmymodel.com/api/projects/public?limit={ITEMS_PER_PAGE}&page=0&type=UML&minDataSize=10000"
    try:
        response = requests.get(url)
        data = response.json()
        return data['totalElements'], data['totalPages']
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
    except ValueError as e:
        print(f"Invalid response: {e}", file=sys.stderr)


def main(start_page=START_PAGE):
    total_projects, total_pages = get_total_projects()
    print(f"Total projects: {total_projects}")

    if not os.path.exists("1_UML-Diagrams"):
        os.makedirs("1_UML-Diagrams")

    counter = [0]
    lock = Lock()

    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
        for page in range(start_page, total_pages):
            page_url = f"https://app.genmymodel.com/api/projects/public?limit={ITEMS_PER_PAGE}&page={page}&type=UML&minDataSize=10000"
            try:
                response = requests.get(page_url)
                projects = response.json()

                futures = [executor.submit(save_xmi_file, project['links'][0]['href'].split('/')[-1], counter, lock) for project in projects['elements']]
                concurrent.futures.wait(futures)

                elapsed_time = time.time() - start_time
                pages_processed = page - start_page + 1
                total_pages_from_start = total_pages - start_page
                progress_percentage = (pages_processed / total_pages_from_start) * 100

                if pages_processed > 1:  # Avoid division by zero on the first page
                    estimated_total_time = elapsed_time / pages_processed * total_pages_from_start
                    time_left = estimated_total_time - elapsed_time
                    print(f"Completed Page {page+1}/{total_pages} - {progress_percentage:.2f}% - Time left: {format_time(time_left)} - Elapsed: {format_time(elapsed_time)}")
                else:
                    print(f"Completed Page {page+1}/{total_pages} - {progress_percentage:.2f}% - Elapsed: {format_time(elapsed_time)}")

            except requests.RequestException as e:
                print(f"Request failed: {e}", file=sys.stderr)
            except ValueError as e:
                print(f"Invalid response: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1:  # Check if there are any command-line arguments
        try:
            start_page = int(sys.argv[1])
        except ValueError:
            print("Invalid start page. Must be an integer.")
            sys.exit(1)
        main(start_page)
    else:
        main()
