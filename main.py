from modules.dump_processor import process_revisions_from_json
from modules.text_files_generator import generate_filtered_texts_from_json

if __name__ == "__main__":
    process_revisions_from_json("wikipedia_metadata/reference_list/_revisions.json")
    #generate_filtered_texts_from_json("wikipedia_metadata/filtered_wikitext/_revisions.json")