import re
from modules.utils import  filter_wikitext, process_results, filter_results


def extract_names_from_citations(wikitext):
    if wikitext is None:
        return set()
    
    citation_pattern = r"\{\{cite[^}]*?\}\}"
    citations = re.findall(citation_pattern, wikitext, re.IGNORECASE)

    author_pattern = re.compile(
        r"(?:\b\w*author\w*\s*=\s*([^|}\n]+))|"  # Match author field
        r"(?:last\d*\s*=\s*([^|\n]+))|"          # Match last name field
        r"(?:first\d*\s*=\s*([^|\n]+))",         # Match first name field
        re.IGNORECASE
    )

    # Regex to extract Unicode word characters
    name_part_pattern = re.compile(r"[^\W\d_]+", re.UNICODE)
    name_parts = set()

    for citation in citations:
        matches = author_pattern.findall(citation)
        for match in matches:
            for name_field in match:
                if name_field:
                    name_parts.update(name_part_pattern.findall(name_field))

    tokens_to_remove = {"and", "the", "of", "for"} 
    name_parts -= tokens_to_remove # manually remove tokens

    return name_parts


def find_names_in_wikitext(wikitext, name_set):
        
    processed_text = filter_wikitext(wikitext)

    pattern = re.compile(r"[^\W\d_]+", re.UNICODE)
    results = []
    for match in pattern.finditer(processed_text):
        word = match.group() 
        start = match.start()
        end = match.end() - 1
        
        if word in name_set:
            results.append({
                "word": word,
                "positionStart": start,
                "positionEnd": end
            })

    results = filter_results(process_results(results))
    print(len(results))

    return results

