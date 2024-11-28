import bz2
import mwxml
from modules.reference_list_processor import extract_names_from_citations, find_exact_matches_with_positions
from modules.utils import wikitext_to_plain
from tqdm import tqdm

def process_wikipedia_dump_file(dump_file, output):
    if dump_file.endswith('.bz2'):
        with bz2.open(dump_file, "rb") as file:
            dump = mwxml.Dump.from_file(file)
            process_wikipedia_dump(dump, output)
    else:
        with open(dump_file, "rb") as file:
            dump = mwxml.Dump.from_file(file)
            process_wikipedia_dump(dump, output)

def process_wikipedia_dump(dump, output):
    with open(output, 'w') as f:
        for page in tqdm(dump, desc="Processing Wikipedia dump"):
            page_list = list(page)
            reference_list = set()
            revision_names_list = []
            
            for revision in tqdm(page_list, desc="Building Candidate List for Wikipedia Article"):
                names = extract_names_from_citations(revision.text)
                reference_list.update(names)

            for revision in tqdm(page_list, desc="Processing Article with Candidate List"): #[-1:]
                names_found = find_exact_matches_with_positions(wikitext_to_plain(revision.text), reference_list)
                formatted_names_with_positions = [f"{match['word']} (positions: {match['positionStart']} - {match['positionEnd']})" for match in names_found]
                revision_names_list.append(", ".join(formatted_names_with_positions))
            
            reference_list_text = "\n".join(reference_list)
            revision_names = "\n".join(revision_names_list)
            f.write("TITLE: " + page.title + "\n\n")
            f.write("REFERENCE LIST:" + "\n")  
            f.write(reference_list_text + "\n\n")
            f.write("NAMES FOUND:" + "\n") 
            f.write(revision_names + "\n\n")
