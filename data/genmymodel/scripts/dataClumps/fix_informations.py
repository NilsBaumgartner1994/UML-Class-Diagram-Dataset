import os
import json
import argparse
import time
from concurrent.futures import ThreadPoolExecutor

# Your provided time formatting function
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s"

def process_json_file(file_path):
    with open(file_path, 'r+', encoding='utf-8') as f:
        data = json.load(f)

        # Replace project_url and set project_version and project_commit_hash to null
        project_name = data['project_info']['project_name']
        data['project_info']['project_url'] = f"https://app.genmymodel.com/explore/{project_name}"
        data['project_info']['project_version'] = None
        data['project_info']['project_commit_hash'] = None
        data['project_info']['project_commit_date'] = None
        data['target_language'] = "UML Class Diagram"
        
        # Add additional URL to additional field
        data['project_info']['additional'] = {
            "download": f"https://app.genmymodel.com/api/projects/{project_name}/custom-xmi"
        }

        # Move the file pointer to the beginning and truncate the file
        f.seek(0)
        f.truncate()
        
        # Save the modified data back to the file
        json.dump(data, f, indent=2)

def main(folder_path):
    json_files = [os.path.join(folder_path, name) for name in os.listdir(folder_path) if name.endswith('.json')]
    total_projects = len(json_files)
    print(f"Total projects: {total_projects}")

    start_time = time.time()
    processed_projects = 0
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(process_json_file, file_path): file_path for file_path in json_files}
        for future in future_to_file:
            future.result()  # Waiting for the file to be processed
            processed_projects += 1
            elapsed_time = time.time() - start_time
            if processed_projects > 1:
                estimated_total_time = elapsed_time / processed_projects * total_projects
                time_left = estimated_total_time - elapsed_time
                print(f"{processed_projects}/{total_projects} projects processed - Time left: {format_time(time_left)} - Elapsed: {format_time(elapsed_time)}")
            else:
                print(f"{processed_projects}/{total_projects} projects processed - Elapsed: {format_time(elapsed_time)}")

if __name__ == "__main__":   
    parser = argparse.ArgumentParser(description="Run commands for projects in a given directory.")
    parser.add_argument('--projects_directory', type=str, required=True, help="The directory containing project folders.")
    
    args = parser.parse_args()
    main(args.projects_directory)


