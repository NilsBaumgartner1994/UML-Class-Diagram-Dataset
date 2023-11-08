import os
import argparse

def split_file(input_file, output_folder, max_size):
    if not os.path.isfile(input_file):
        print(f"The file {input_file} does not exist.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    part_number = 1
    with open(input_file, 'rb') as f:
        while True:
            chunk = f.read(max_size)
            if not chunk:
                break

            part_filename = os.path.join(output_folder, f"{os.path.basename(input_file)}_part{part_number}")
            with open(part_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)

            print(f"Created: {part_filename}")
            part_number += 1

    print("Splitting complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Split a file into multiple parts.")
    parser.add_argument('input_file', type=str, help="The input file to be split.")
    parser.add_argument('--output-folder', type=str, default='./split_files', help="The output folder to save the split files.")
    parser.add_argument('--max-size', type=int, default=50, help="The maximum size (in MB) for each split file.")

    args = parser.parse_args()

    # Convert max_size from MB to bytes
    max_size_bytes = args.max_size * 1024 * 1024

    split_file(args.input_file, args.output_folder, max_size_bytes)
