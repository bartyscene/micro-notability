import json
import os
import mwxml
from modules.utils import filter_wikitext

def list_files_in_folder(folder_path):
    try:
        # Check if the given path exists
        if not os.path.exists(folder_path):
            print(f"The folder '{folder_path}' does not exist.")
            return
        
        # List all files in the folder
        print(f"Files in '{folder_path}':")
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):  # Check if it is a file
                print(file_name)
    except Exception as e:
        print(f"An error occurred: {e}")

def generate_filtered_texts_from_json(json_file_path):
    # Load the JSON file
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"JSON file {json_file_path} not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    # Determine the directory in which the JSON file resides
    output_dir = os.path.dirname(json_file_path)

    # Iterate over the JSON structure
    for file_data in json_data:
        # Get the input file name from the JSON
        input_file_name = file_data[0]["input_file_name"]
        input_file_path = os.path.join("dumps", input_file_name)
        
        # Process the XML file using mwxml
        try:
            with open(input_file_path, "rb") as xml_file:
                dump = mwxml.Dump.from_file(xml_file)
                for page in dump:
                    for revision in page:
                        for item in file_data[1:]:
                            output_file_name = item["output_file_name"]
                            id_to_find = item["id"]

                            # If there's no ID, skip
                            if id_to_find is None:
                                continue
                            
                            # Match the revision ID
                            if revision.id == id_to_find:
                                # Filter and process the wikitext
                                processed_text = filter_wikitext(revision.text)
                                # Write to a file in the same directory as the JSON
                                output_file_path = os.path.join(output_dir, output_file_name)
                                with open(output_file_path, "w", encoding="utf-8") as output_file:
                                    output_file.write(processed_text)
                                print(f"Processed and saved to {output_file_path}")
        except FileNotFoundError:
            print(f"File {input_file_path} not found.")
        except Exception as e:
            print(f"An error occurred while processing {input_file_name}: {e}")