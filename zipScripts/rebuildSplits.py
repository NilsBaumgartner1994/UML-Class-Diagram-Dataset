import os
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

    # Get the common prefix of the part files to name the combined file
    # First strip the part numbering (e.g., "_part1") and then find the common prefix
    stripped_names = [name.rsplit('_part', 1)[0] for name in parts]
    common_prefix = os.path.commonprefix(stripped_names)

    # Ensure the combined file has the correct '.zip' extension
    combined_name = common_prefix + '.zip' if not common_prefix.lower().endswith('.zip') else common_prefix

    combined_zip_path = os.path.join(output_folder, os.path.basename(combined_name))

    # Combine all parts into one file
    with open(combined_zip_path, 'wb') as combined_file:
        for part in parts:
            with open(part, 'rb') as p:
                combined_file.write(p.read())
            print(f"Combined file {part}")

    print(f"Combined file created at {combined_zip_path}")
    return combined_zip_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Combine split parts of a zip file.")
    parser.add_argument('parts_folder', type=str, help="The folder containing the split zip parts.")
    parser.add_argument('--output-folder', type=str, default='./', help="The output folder to save the combined zip.")

    args = parser.parse_args()

    combine_files(args.parts_folder, args.output_folder)
