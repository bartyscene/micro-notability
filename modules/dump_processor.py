import os
import json
import bz2
import mwxml
from tqdm import tqdm
from modules.reference_list_processor import extract_names_from_citations, find_names_in_wikitext
from modules.spacy_processor import SpacyNameEntityRecognizer
from modules.roberta_processor import RobertaNameEntityRecognizer

def _build_reference_list(page_list):
    """
    Builds a reference list from all revisions in the given page list.
    
    :param page_list: List of revisions for a Wikipedia page.
    :return: Set of unique names extracted from all revisions' citations.
    """
    reference_list = set()
    tokens_to_remove = {
        "and", "the", "of", "for", "in", "not", "on", "an", "a", "at", "with",
        "And", "The", "Of", "For", "In", "Not", "On", "An", "At", "With",
    }

    for revision in tqdm(page_list, desc="Building Reference List for Wikipedia Article"):
        if not revision.text:
            continue
        names = extract_names_from_citations(revision.text)
        reference_list.update(names)

    # Remove undesired tokens
    reference_list -= tokens_to_remove
    return reference_list

def _extract_names_with_reference_list(text, reference_list):
    """
    Finds names in the given text using a reference list.
    
    :param text: Text content to search.
    :param reference_list: Set of reference names to match.
    :return: List of matched names with positions (if applicable).
    """
    matches = find_names_in_wikitext(text, reference_list)
    formatted_matches = [
        f"{match['word']}" for match in matches
    ]
    return formatted_matches

def _extract_names_with_ner(text, name_entity_recognizer):
    """
    Extracts names from the given text using spacy named entity recognition (NER).
    
    :param text: Text content to process.
    :param name_entity_recognizer: An instance of NameEntityRecognizer.
    :return: List of matched names with positions (if applicable).
    """
    matches = name_entity_recognizer.extract_names(text)
    formatted_matches = [
        f"{match['word']}" for match in matches
    ]
    return formatted_matches

def _extract_names_from_revision(revision, reference_list, spacy_ner, roberta_ner):
    """
    Processes a single revision to extract names using reference list and spacy.
    
    :param revision: The revision object to process.
    :param reference_list: Set of names extracted from citations.
    :param name_entity_recognizer: An instance of NameEntityRecognizer.
    :return: A formatted string of the revision results.
    """
    if not revision.text:
        return None

    # Names found via reference list
    parser_names = _extract_names_with_reference_list(revision.text, reference_list)
    # Names found via NER
    spacy_ner_names = _extract_names_with_ner(revision.text, spacy_ner)
    roberta_ner_names = _extract_names_with_ner(revision.text, roberta_ner)

    timestamp_str = str(revision.timestamp)
    return (
        f"REVISION ID: {revision.id}, TIMESTAMP: {timestamp_str}\n\n"
        "PARSER NAMES:\n" + "\n".join(parser_names) + "\n\n"
        "SPACY NER NAMES:\n" + "\n".join(spacy_ner_names) + "\n\n"
        "ROBERTA NER NAMES:\n" + "\n".join(roberta_ner_names) + "\n\n"
    )

def _process_wikipedia_pages(input_path, output_path, revision_ids):
    """
    Internal helper that processes a single Wikipedia dump file (input_path)
    and writes the results for specific revisions to output_path.
    If 'revision_ids' is empty, processes all revisions.
    """
    spacy = SpacyNameEntityRecognizer(use_gpu=False)
    roberta = RobertaNameEntityRecognizer()
    open_method = bz2.open if input_path.endswith('.bz2') else open
    with open_method(input_path, 'rb') as dump_file, open(output_path, 'w', encoding='utf-8') as out_f:
        dump = mwxml.Dump.from_file(dump_file)
        for page in tqdm(dump, desc=f"Processing {input_path}"):
            page_list = list(page)
            
            reference_list = _build_reference_list(page_list) # Build the reference list from all revisions in the page

            # Process revisions
            results_for_revisions = []
            for revision in tqdm(page_list, desc="Processing Revisions"):
                if not revision_ids or revision.id in revision_ids:
                    revision_output = _extract_names_from_revision(revision, reference_list, spacy, roberta)
                    if revision_output:
                        results_for_revisions.append(revision_output)

            # Write to output file if there is any content
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
    base_dir = os.path.dirname(json_path) or '.'

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        input_file_name = item["input_file_name"]
        output_file_name = item["output_file_name"]
        revision_ids = item.get("ids", [])  # Default to empty list if 'ids' is missing

        input_path = os.path.join("dumps", input_file_name)
        output_path = os.path.join(base_dir, output_file_name)

        print(f"Processing: {input_file_name} -> {output_file_name}")
        _process_wikipedia_pages(input_path, output_path, revision_ids)