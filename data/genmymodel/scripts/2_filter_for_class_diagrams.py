import os
import argparse
import xml.etree.ElementTree as ET
import shutil  # Don't forget to import this at the start of your script

def is_uml_class_diagram(xmi_content):
    try:
        # Parse the XML content
        tree = ET.ElementTree(ET.fromstring(xmi_content))
        root = tree.getroot()

        # Namespace mapping
        ns = {
            'xmi': 'http://schema.omg.org/spec/XMI/2.1',
            'uml': 'http://www.eclipse.org/uml2/5.0.0/UML',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        # Search for elements with tag 'packagedElement' and attribute '{http://www.w3.org/2001/XMLSchema-instance}type' as 'uml:Class'
        for elem in root.findall(".//packagedElement[@xsi:type='uml:Class']", ns):
            return True  # A 'packagedElement' of type 'uml:Class' was found, so it's a UML class diagram

        for elem in root.findall(".//packagedElement[@xmi:type='uml:Class']", ns):
            return True  # A 'packagedElement' of type 'uml:Class' was found, so it's a UML class diagram



        return False  # No 'packagedElement' of type 'uml:Class' found

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def process_folder(path_to_folder, output_folder):
    # Check if output directory exists, if so, delete it
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    # Recreate the output directory
    os.makedirs(output_folder)

    # Initialize counters
    total_files = 0
    processed_files = 0
    found_diagrams = 0

    # Check if the path exists and it's a directory
    if os.path.exists(path_to_folder) and os.path.isdir(path_to_folder):
        # Count total .xmi files
        for filename in os.listdir(path_to_folder):
            if filename.endswith(".xmi"):
                total_files += 1

        for filename in os.listdir(path_to_folder):
            if filename.endswith(".xmi"):
                processed_files += 1  # Update processed files counter

                filepath = os.path.join(path_to_folder, filename)
                try:
                    with open(filepath, 'rb') as file:  # Open file in binary mode
                        raw_content = file.read()
                        content = raw_content.decode('utf-8', errors='replace')  # Decode with replacement of undecodable bytes

                    if is_uml_class_diagram(content):
                        found_diagrams += 1  # Update found diagrams counter

                        # Copy UML class diagram files to the output folder
                        output_filepath = os.path.join(output_folder, filename)
                        with open(output_filepath, 'w', encoding='utf-8') as file:  # Ensure to write with utf-8 encoding
                            file.write(content)

                except Exception as e:
                    print(f"An error occurred while processing file {filename}: {e}")

                # Print progress
                print(f"Processed {processed_files}/{total_files} files - found class diagrams: {found_diagrams} amount")
    else:
        print(f"{path_to_folder} is not a valid directory")

def main():
    parser = argparse.ArgumentParser(description="Process a folder of XMI files to find UML class diagrams.")
    parser.add_argument("path_to_folder", type=str, help="Path to the folder containing the XMI files")
    parser.add_argument("--output_folder", type=str, default="2_UML-Class-Diagrams", help="Path to the output folder")

    args = parser.parse_args()

    process_folder(args.path_to_folder, args.output_folder)

if __name__ == "__main__":
    main()
