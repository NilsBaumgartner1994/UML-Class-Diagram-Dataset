import os
import argparse
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s"

def run_command(project_name, folder_path, output_directory):
    project_path = os.path.join(folder_path, project_name)
    output_path = os.path.join(output_directory, f"{project_name}.json")
    
    # Skip if the output file already exists
    if os.path.isfile(output_path):
        return f"Skipping {project_name}, output file already exists."
    
    command = f"node ./build/ignoreCoverage/cli.js --output {output_path} --path_to_project {project_path} --project_name {project_name} --source_type ast"
    os.chdir("/Users/nilsbaumgartner/Documents/GitHub/data-clumps-doctor/analyse")
    
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #subprocess.run(command, shell=True)
    return f"Processed {project_name}"

def run_command_for_projects(folder_path, output_directory):
    start_time = time.time()
    
    projects = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
    total_projects = len(projects)
    print(f"Total projects: {total_projects}")

    processed_projects = 0
    with ThreadPoolExecutor() as executor:
        future_to_project = {executor.submit(run_command, project, folder_path, output_directory): project for project in projects}
        for future in as_completed(future_to_project):
            result = future.result()
            processed_projects += 1
            elapsed_time = time.time() - start_time
            if processed_projects > 1:
                estimated_total_time = elapsed_time / processed_projects * total_projects
                time_left = estimated_total_time - elapsed_time
                print(f"{processed_projects}/{total_projects} projects processed - Time left: {format_time(time_left)} - Elapsed: {format_time(elapsed_time)}")
            else:
                print(f"{processed_projects}/{total_projects} projects processed - Elapsed: {format_time(elapsed_time)}")

    elapsed_time = time.time() - start_time
    print(f"All projects processed - Total elapsed: {format_time(elapsed_time)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run commands for projects in a given directory.")
    parser.add_argument('--projects_directory', type=str, required=True, help="The directory containing project folders.")
    parser.add_argument('--output_directory', type=str, required=True, help="The directory to save output files.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)
    
    run_command_for_projects(args.projects_directory, args.output_directory)
