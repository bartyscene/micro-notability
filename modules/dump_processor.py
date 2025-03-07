import os
import json
import bz2
import mwxml
from tqdm import tqdm
from modules.reference_list_processor import extract_names_from_citations, extract_raw_names_from_citations, find_names_in_wikitext
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
        #names = extract_raw_names_from_citations(revision.text)
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

def _process_wikipedia_pages_with_reference_list(input_path, revision_mapping):
    """
    Processes a Wikipedia dump file using reference list extraction.
    revision_mapping: dict mapping revision id (as int) to output file name.
    """
    open_method = bz2.open if input_path.endswith('.bz2') else open
    with open_method(input_path, 'rb') as dump_file:
        dump = mwxml.Dump.from_file(dump_file)
        for page in tqdm(dump, desc=f"Processing {input_path}"):
            page_list = list(page)
            # Build the reference list for the entire page (using all its revisions)
            reference_list = _build_reference_list(page_list)
            for revision in tqdm(page_list, desc="Processing Revisions", leave=False):
                if not revision.text:
                    continue
                if revision.id in revision_mapping:
                    names = _extract_names_with_reference_list(revision.text, reference_list)
                    result = {
                        "revision_id": str(revision.id),
                        "names": names
                    }
                    output_path = revision_mapping[revision.id]
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as out_f:
                        json.dump(result, out_f, indent=4, ensure_ascii=False)

def _process_wikipedia_pages_with_spacy(input_path, revision_mapping, spacy_ner):
    """
    Processes a Wikipedia dump file using NER extraction.
    revision_mapping: dict mapping revision id (as int) to output file name.
    """
    open_method = bz2.open if input_path.endswith('.bz2') else open
    with open_method(input_path, 'rb') as dump_file:
        dump = mwxml.Dump.from_file(dump_file)
        for page in tqdm(dump, desc=f"Processing {input_path}"):
            for revision in tqdm(list(page), desc="Processing Revisions", leave=False):
                if not revision.text:
                    continue
                if revision.id in revision_mapping:
                    spacy_names = _extract_names_with_ner(revision.text, spacy_ner)
                    result = {
                        "revision_id": str(revision.id),
                        "names": spacy_names,
                    }
                    output_path = revision_mapping[revision.id]
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as out_f:
                        json.dump(result, out_f, indent=4, ensure_ascii=False)


def process_dumps_with_reference_list(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        input_path = item["input_file_name"]
        revision_mapping = {rev["id"]: rev["output_file_name"] for rev in item["revisions"]}
        print(f"Processing {input_path} with reference list extraction...")
        _process_wikipedia_pages_with_reference_list(input_path, revision_mapping)


def process_dumps_with_spacy(json_path):
    spacy_ner = SpacyNameEntityRecognizer(use_gpu=False)
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        input_path = item["input_file_name"]
        revision_mapping = {rev["id"]: rev["output_file_name"] for rev in item["revisions"]}
        print(f"Processing {input_path} with NER extraction...")
        _process_wikipedia_pages_with_spacy(input_path, revision_mapping, spacy_ner)