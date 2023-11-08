import os
import argparse
import xml.etree.ElementTree as ET
import shutil  # Don't forget to import this at the start of your script
import json
import time

ns = {
    'xmi': 'http://schema.omg.org/spec/XMI/2.1',
    'uml': 'http://www.eclipse.org/uml2/5.0.0/UML',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

def format_time(seconds):
    # Convert seconds to hours, minutes, and seconds, then format as XXh YYm ZZs
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s"

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


def getIdOfElem(elem): # TODO maybe check for a more generic approach
    return elem.get('{http://schema.omg.org/spec/XMI/2.1}id')

def getModifiers(elem):
    visibility = elem.attrib.get('visibility')
    if visibility:
        return [visibility]
    else:
        return []

def extract_field_details(elem, class_key):
    fields = {}
    for field_elem in elem.findall(".//ownedAttribute", ns):
        field_name = getName(field_elem)
        if(field_name==None):
            continue

        field_key = getIdOfElem(field_elem)
        field_type = None  # TODO: Might need to add logic for type extraction if provided in XMI
        field_hasTypeVariable = False
        field_modifiers = getModifiers(field_elem)

        fields[field_name] = {
            "name": field_name,
            "key": field_key,
            "type": field_type,
            "hasTypeVariable": field_hasTypeVariable,
            "position": None,
            "modifiers": field_modifiers,
            "ignore": False,
            "classOrInterfaceKey": class_key
        }
    return fields

def extract_method_parameters(method_elem, method_key):
    method_parameters = []
    for param_elem in method_elem.findall(".//ownedParameter", ns):
        direction = param_elem.attrib.get('direction')
        signature = param_elem.attrib.get('signature')
        if(signature):
            continue

        if(direction!="return"):
            param_name = getName(param_elem)
            if(param_name==None):
                continue

            param_key = getIdOfElem(param_elem)
            param_type = None  # TODO: Logic for parameter type extraction
            param_hasTypeVariable = False
            param_modifiers = getModifiers(param_elem)
            method_parameters.append({
                "name": param_name,
                "key": param_key,
                "type": param_type,
                "hasTypeVariable": param_hasTypeVariable,
                "position": None,
                "modifiers": param_modifiers,
                "ignore": False,
                "methodKey": method_key
            })
    return method_parameters

def extraxt_method_details(elem, class_key):
    methods = {}
    for method_elem in elem.findall(".//ownedOperation", ns):
        method_name = getName(method_elem)
        if(method_name==None):
            continue

        method_key = getIdOfElem(method_elem)
        method_type = None  # TODO: Logic for method type extraction if provided in XMI
        method_hasTypeVariable = False
        method_modifiers = getModifiers(method_elem)

        method_parameters = extract_method_parameters(method_elem, method_key)

        methods[method_name] = {
            "name": method_name,
            "key": method_key,
            "type": method_type,
            "hasTypeVariable": method_hasTypeVariable,
            "position": None,
            "modifiers": method_modifiers,
            "overrideAnnotation": False,
            "returnType": None,
            "parameters": method_parameters,
            "classOrInterfaceKey": class_key
        }
    return methods

def extract_generalizations(root, ns):
    """Extract all generalizations from the given XML root."""
    generalizations = {}
    for general_elem in root.findall(".//generalization", ns):
        specific = general_elem.attrib.get('specific')
        general = general_elem.attrib.get('general')
        if specific in generalizations:
            generalizations[specific].append(general)
        else:
            generalizations[specific] = [general]
    return generalizations

def getName(elem):
    try:
        name = elem.attrib['name']
        name = name.strip().replace(" ", "")
        return name
    except Exception as e:
        return None

def find_uml_class_elements(root, ns, namespace_prefix):
    uml_class_query = f".//packagedElement[@{namespace_prefix}:type='uml:Class']"
    return root.findall(uml_class_query, ns)

def extract_class_details(xmi_content):
    classes = {}
    """Extracts the class details from the given XMI content."""
    try:
        tree = ET.ElementTree(ET.fromstring(xmi_content))
        root = tree.getroot()

        all_generalizations = extract_generalizations(root, ns)

        elements_xsi = find_uml_class_elements(root, ns, 'xsi')
        elements_xmi = find_uml_class_elements(root, ns, 'xmi')

        all_elements = elements_xsi + elements_xmi

        all_unique_elements = list({elem: None for elem in all_elements})
        
        for elem in all_unique_elements:
            class_name = getName(elem)
            if(class_name==None):
                continue

            class_key = getIdOfElem(elem)

            class_type = "class"
            hasTypeVariable = False

            fields = extract_field_details(elem, class_key)
            methods = extraxt_method_details(elem, class_key)

            class_extends = all_generalizations.get(class_key, [])

            file_path = class_name.replace("/", "_")
            if(file_path=="."):
                file_path = class_key.replace("/", "_")

            classes[class_name] = {
                # from AstElementTypeContext
                "name": class_name,
                "key": class_key,
                "type": class_type,
                "hasTypeVariable": hasTypeVariable,
                "position": None,

                # From ClassOrInterfaceTypeContext
                "modifiers": getModifiers(elem),
                "fields": fields,
                "methods": methods,
                "file_path": "./"+file_path,
                "anonymous": False,
                "auxclass": False,
                "implements_": [],
                "extends_": [],
                "definedInClassOrInterfaceTypeKey": None,
                "innerDefinedClasses": {},
                "innerDefinedInterfaces": {}
            }

        return classes
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def process_folder(path_to_folder, output_folder):
    # Check if output directory exists, if so, delete it
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    # Recreate the output directory
    os.makedirs(output_folder)

    # Initialize counters
    total_files = 0
    processed_files = 0
    processed_classes = 0
    successfull_processed_classes = 0

    # Start the timer
    start_time = time.time()

    errors_list = []

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
                with open(filepath, 'r') as file:
                    content = file.read()

                if is_uml_class_diagram(content):
                    
                    # Extract class details from the content
                    class_details = extract_class_details(content)

                    # Create a directory with the filename (without .xmi) inside the output folder
                    output_directory_path = os.path.join(output_folder, filename.rstrip('.xmi'))
                    os.makedirs(output_directory_path, exist_ok=True)

                    error_in_parsing = False
                    amount_classes = 0

                    for class_name, details in class_details.items():
                        class_name_file_path = details["file_path"]
                        amount_classes += 1
                        class_file_path = os.path.join(output_directory_path, f"{class_name_file_path}.json")
                        try:
                            with open(class_file_path, 'w') as class_file:
                                json.dump(details, class_file, indent=4)
                        except Exception as e:
                            print("Source Filename: "+filename)
                            print(f"An error occurred: {e}")
                            print("Skipping this file")
                            error_in_parsing = True
                            errors_list.append(f"Source Filename: "+filename+" - An error occurred: {e}")

                    processed_classes += amount_classes
                    if(error_in_parsing==False):
                        successfull_processed_classes += amount_classes  # Update found diagrams counter
                    else:
                        if os.path.exists(output_directory_path):
                            shutil.rmtree(output_directory_path)

                # Calculate elapsed time and estimated time left
                elapsed_time = time.time() - start_time
                if processed_files > 1:
                    estimated_total_time = elapsed_time / processed_files * total_files
                    time_left = estimated_total_time - elapsed_time
                    print(f"Processed {processed_files}/{total_files} files - class diagrams: {successfull_processed_classes}/{processed_classes} - Time left: {format_time(time_left)} - Elapsed: {format_time(elapsed_time)}")
                else:
                    print(f"Processed {successfull_processed_classes}/{total_files} files - class diagrams: {successfull_processed_classes}/{processed_classes} - Elapsed: {format_time(elapsed_time)}")
    else:
        print(f"{path_to_folder} is not a valid directory")

    for error in errors_list:
        print(error)

    print("Finished")

def main():
    parser = argparse.ArgumentParser(description="Process a folder of XMI files to find UML class diagrams.")
    parser.add_argument("path_to_folder", type=str, help="Path to the folder containing the XMI files")
    parser.add_argument("--output_folder", type=str, default="./3_Extracted-Class-Informations", help="Path to the output folder")

    args = parser.parse_args()

    process_folder(args.path_to_folder, args.output_folder)

if __name__ == "__main__":
    main()
