from modules.dump_processor import process_revisions_from_json
from modules.text_files_generator import process_json_file
from modules.dump_downloader import DumpDownloader


if __name__ == "__main__":
    #process_revisions_from_json("parser_and_spacy_names/_revisions.json")
    process_json_file("wikitext/_revisions.json")