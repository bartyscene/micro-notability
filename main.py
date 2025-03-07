from modules.dump_processor import process_dumps_with_reference_list, process_dumps_with_spacy
from modules.text_files_generator import generate_filtered_texts_from_json

if __name__ == "__main__":
    process_dumps_with_reference_list("wikipedia_metadata/parser_names/_revisions.json")
    process_dumps_with_spacy("wikipedia_metadata/spacy_names/_revisions.json")
    #generate_filtered_texts_from_json("wikipedia_metadata/filtered_wikitext/_revisions.json")