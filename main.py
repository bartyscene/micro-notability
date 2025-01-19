from modules.dump_processor import process_revisions_from_json
from modules.text_files_generator import generate_filtered_texts_from_json

if __name__ == "__main__":
    process_revisions_from_json("parser_and_spacy_names/_revisions.json")
    #generate_filtered_texts_from_json("filtered_wikitext/_revisions.json")