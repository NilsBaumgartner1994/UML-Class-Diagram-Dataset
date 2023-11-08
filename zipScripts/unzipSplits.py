import os
import zipfile
import argparse

def combine_files(parts_folder, output_folder):
    # Make sure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Sort the parts by name
    parts = sorted(
        [os.path.join(parts_folder, f) for f in os.listdir(parts_folder) if "part" in f],
        key=lambda x: int(x.rsplit("part", 1)[-1].split('.')[0])
    )

    combined_zip_path = os.path.join(output_folder, 'combined_file.zip')

    # Combine all parts into one file
    with open(combined_zip_path, 'wb') as combined_file:
        for part in parts:
            with open(part, 'rb') as p:
                combined_file.write(p.read())
            print(f"Combined file {part}")

    print(f"Combined file created at {combined_zip_path}")
    return combined_zip_path

def unzip_file(zip_path, output_folder):
    # Try to unzip the file if it is a zip file
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
            print(f"Extracted zip to {output_folder}")
    except zipfile.BadZipFile:
        print("The combined file is not a zip file. Please check the parts and ensure they are correct and complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Combine split parts of a zip file and extract it.")
    parser.add_argument('parts_folder', type=str, help="The folder containing the split zip parts.")
    parser.add_argument('--output-folder', type=str, default='./', help="The output folder to save the combined zip and extract its contents.")

    args = parser.parse_args()

    combined_zip_path = combine_files(args.parts_folder, args.output_folder)
    unzip_file(combined_zip_path, args.output_folder)
