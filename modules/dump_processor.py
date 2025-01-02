import os
import json
import bz2
import mwxml
from modules.reference_list_processor import extract_names_from_citations, find_names_in_wikitext
from modules.ner_processor import NameEntityRecognizer

from tqdm import tqdm

def _process_wikipedia_pages(input_path, output_path, revision_ids):
    """
    Internal helper that processes a single Wikipedia dump file (input_path)
    and writes the results for specific revisions to output_path.
    
    Steps:
    1. Read the entire dump and for each page:
       a) Build a reference_list from *all* revisions in the page.
       b) For each revision whose ID is in 'revision_ids', extract:
          - Names via wikitext (reference_list-based)
          - Names via spaCy/NER
       c) Write results to output_path.
    """

    name_entity_recognizer = NameEntityRecognizer(use_gpu=False)

    # Determine if we need to open with bz2 or plain open
    open_method = bz2.open if input_path.endswith('.bz2') else open

    with open_method(input_path, 'rb') as dump_file, open(output_path, 'w', encoding='utf-8') as out_f:
        dump = mwxml.Dump.from_file(dump_file)

        for page in tqdm(dump, desc=f"Processing {input_path}"):
            page_list = list(page)
            reference_list = set()

            # 1) Build the reference_list from all revisions in the page
            for revision in tqdm(page_list, desc="Building Candidate List for Wikipedia Article"):
                if not revision.text:
                    continue
                names = extract_names_from_citations(revision.text)
                reference_list.update(names)

            # 2) Process only the revisions in 'revision_ids'
            results_for_revisions = []
            for revision in tqdm(page_list, desc="Processing Targeted Revisions"):
                if revision.id in revision_ids and revision.text:
                    # Names found via reference list
                    wikitext_names = find_names_in_wikitext(revision.text, reference_list)
                    formatted_wikitext_names = [
                        f"{match['word']}" #(positions: {match['positionStart']} - {match['positionEnd']})
                        for match in wikitext_names
                    ]

                    # Names found via NER
                    ner_names = name_entity_recognizer.extract_names(revision.text)
                    formatted_ner_names = [
                        f"{match['word']}" #(positions: {match['positionStart']} - {match['positionEnd']})
                        for match in ner_names
                    ]

                    timestamp_str = str(revision.timestamp)
                    revision_output = (
                        f"REVISION ID: {revision.id}, TIMESTAMP: {timestamp_str}\n\n"
                        "PARSER NAMES:\n" + "\n".join(formatted_wikitext_names) + "\n\n"
                        "NER NAMES:\n" + "\n".join(formatted_ner_names) + "\n\n"
                    )
                    results_for_revisions.append(revision_output)

            # 3) Write to output file if there is any content
            if results_for_revisions:
                out_f.write(f"TITLE: {page.title}\n\n")
                out_f.write("\n".join(results_for_revisions))


def process_revisions_from_json(json_path):
    """
    Reads a JSON file (containing input_file_name, output_file_name, and ids)
    and processes each Wikipedia dump file found in 'dumps/'.
    The output files will be saved in the same directory as the JSON file.
    
    :param json_path: Path to the revisions JSON file.
    """
    # Figure out the directory in which the JSON file resides
    base_dir = os.path.dirname(json_path)
    if not base_dir:  # If json_path is in the current directory, base_dir might be empty
        base_dir = '.'

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        input_file_name = item["input_file_name"]
        output_file_name = item["output_file_name"]
        revision_ids = item["ids"]

        input_path = os.path.join("dumps", input_file_name)
        output_path = os.path.join(base_dir, output_file_name)

        print(f"Processing: {input_file_name} -> {output_file_name}")
        _process_wikipedia_pages(input_path, output_path, revision_ids)