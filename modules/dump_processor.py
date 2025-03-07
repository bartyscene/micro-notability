import os
import json
import bz2
import mwxml
import logging
from tqdm import tqdm
from typing import List, Set, Dict, Any

from modules.reference_list_processor import (
    extract_names_from_citations,
    extract_raw_names_from_citations,
    find_names_in_wikitext
)
from modules.spacy_processor import SpacyNameEntityRecognizer
from modules.roberta_processor import RobertaNameEntityRecognizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKENS_TO_REMOVE: Set[str] = {
    "and", "the", "of", "for", "in", "not", "on", "an", "a", "at", "with",
    "And", "The", "Of", "For", "In", "Not", "On", "An", "At", "With",
}

def _build_reference_list(page_list: List[Any]) -> Set[str]:
    """
    Builds a reference list from all revisions in the given page list.

    :param page_list: List of revisions for a Wikipedia page.
    :return: Set of unique names extracted from all revisions' citations.
    """
    reference_list: Set[str] = set()
    for revision in tqdm(page_list, desc="Building Reference List for Wikipedia Article"):
        if not getattr(revision, "text", None):
            continue
        try:
            # names = extract_raw_names_from_citations(revision.text)
            names = extract_names_from_citations(revision.text)
            reference_list.update(names)
        except Exception as e:
            logger.error(f"Error extracting names from revision {revision.id}: {e}")
    
    # Remove undesired tokens
    reference_list -= TOKENS_TO_REMOVE
    return reference_list

def _extract_names_with_reference_list(text: str, reference_list: Set[str]) -> List[str]:
    """
    Finds names in the given text using a reference list.

    :param text: Text content to search.
    :param reference_list: Set of reference names to match.
    :return: List of matched names.
    """
    try:
        matches = find_names_in_wikitext(text, reference_list)
    except Exception as e:
        logger.error(f"Error finding names in wikitext: {e}")
        return []
    
    return [match.get('word', '') for match in matches if 'word' in match]

def _extract_names_with_ner(text: str, name_entity_recognizer: Any) -> List[str]:
    """
    Extracts names from the given text using a NER processor.

    :param text: Text content to process.
    :param name_entity_recognizer: An instance of a name entity recognizer.
    :return: List of extracted names.
    """
    try:
        matches = name_entity_recognizer.extract_names(text)
    except Exception as e:
        logger.error(f"Error during NER extraction: {e}")
        return []
    
    return [match.get('word', '') for match in matches if 'word' in match]

def _process_wikipedia_pages_with_reference_list(input_path: str, revision_mapping: Dict[int, str]) -> None:
    """
    Processes a Wikipedia dump file using reference list extraction.
    
    :param input_path: Path to the Wikipedia dump file.
    :param revision_mapping: Mapping from revision id (int) to output file name.
    """
    open_method = bz2.open if input_path.endswith('.bz2') else open
    try:
        with open_method(input_path, 'rb') as dump_file:
            dump = mwxml.Dump.from_file(dump_file)
            for page in tqdm(dump, desc=f"Processing {input_path}"):
                page_list = list(page)
                # Build the reference list for the entire page
                reference_list = _build_reference_list(page_list)
                for revision in tqdm(page_list, desc="Processing Revisions", leave=False):
                    if not getattr(revision, "text", None):
                        continue
                    if revision.id in revision_mapping:
                        names = _extract_names_with_reference_list(revision.text, reference_list)
                        result = {
                            "revision_id": str(revision.id),
                            "names": names
                        }
                        output_path = revision_mapping[revision.id]
                        try:
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            with open(output_path, 'w', encoding='utf-8') as out_f:
                                json.dump(result, out_f, indent=4, ensure_ascii=False)
                        except Exception as e:
                            logger.error(f"Error writing output for revision {revision.id}: {e}")
    except Exception as e:
        logger.error(f"Error processing dump file {input_path}: {e}")

def _process_wikipedia_pages_with_spacy(input_path: str, revision_mapping: Dict[int, str],
                                        spacy_ner: SpacyNameEntityRecognizer) -> None:
    """
    Processes a Wikipedia dump file using NER extraction.
    
    :param input_path: Path to the Wikipedia dump file.
    :param revision_mapping: Mapping from revision id (int) to output file name.
    :param spacy_ner: Instance of SpacyNameEntityRecognizer.
    """
    open_method = bz2.open if input_path.endswith('.bz2') else open
    try:
        with open_method(input_path, 'rb') as dump_file:
            dump = mwxml.Dump.from_file(dump_file)
            for page in tqdm(dump, desc=f"Processing {input_path}"):
                for revision in tqdm(list(page), desc="Processing Revisions", leave=False):
                    if not getattr(revision, "text", None):
                        continue
                    if revision.id in revision_mapping:
                        spacy_names = _extract_names_with_ner(revision.text, spacy_ner)
                        result = {
                            "revision_id": str(revision.id),
                            "names": spacy_names,
                        }
                        output_path = revision_mapping[revision.id]
                        try:
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            with open(output_path, 'w', encoding='utf-8') as out_f:
                                json.dump(result, out_f, indent=4, ensure_ascii=False)
                        except Exception as e:
                            logger.error(f"Error writing output for revision {revision.id}: {e}")
    except Exception as e:
        logger.error(f"Error processing dump file {input_path}: {e}")

def process_dumps_with_reference_list(json_path: str) -> None:
    """
    Processes dumps using reference list extraction based on a JSON configuration file.

    :param json_path: Path to the JSON configuration file.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON config from {json_path}: {e}")
        return

    for item in data:
        input_path = item.get("input_file_name")
        revision_mapping = {rev["id"]: rev["output_file_name"] for rev in item.get("revisions", [])}
        logger.info(f"Processing {input_path} with reference list extraction...")
        _process_wikipedia_pages_with_reference_list(input_path, revision_mapping)

def process_dumps_with_spacy(json_path: str) -> None:
    """
    Processes dumps using Spacy NER extraction based on a JSON configuration file.

    :param json_path: Path to the JSON configuration file.
    """
    try:
        spacy_ner = SpacyNameEntityRecognizer(use_gpu=False)
    except Exception as e:
        logger.error(f"Failed to initialize SpacyNameEntityRecognizer: {e}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON config from {json_path}: {e}")
        return

    for item in data:
        input_path = item.get("input_file_name")
        revision_mapping = {rev["id"]: rev["output_file_name"] for rev in item.get("revisions", [])}
        logger.info(f"Processing {input_path} with NER extraction...")
        _process_wikipedia_pages_with_spacy(input_path, revision_mapping, spacy_ner)