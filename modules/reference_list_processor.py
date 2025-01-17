import re
from modules.utils import  filter_wikitext, merge_adjacent_tokens_in_result_list, exclude_uniform_case_tokens

AUTHOR_PATTERN = re.compile(
    r"\bauthor\d*\s*=\s*([^|}\n]+)|"   
    r"\bauthor-link\d*\s*=\s*([^|}\n]+)|"   
    r"\bauthorlink\d*\s*=\s*([^|}\n]+)|"   
    r"\bvauthors\s*=\s*([^|}\n]+)|"     
    r"\bcoauthors\s*=\s*([^|}\n]+)|"      
    r"\bsurname\d*\s*=\s*([^|}\n]+)|"  
    r"\bauthor-last\d*\s*=\s*([^|}\n]+)|"
    r"\bauthorlast\d*\s*=\s*([^|}\n]+)|"
    r"\blast\d*\s*=\s*([^|}\n]+)|"
    r"\bgiven\d*\s*=\s*([^|}\n]+)|"
    r"\bauthor-first\d*\s*=\s*([^|}\n]+)|"    
    r"\bauthorfirst\d*\s*=\s*([^|}\n]+)|"          
    r"\bfirst\d*\s*=\s*([^|}\n]+)",           
    re.IGNORECASE
)

NAME_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE) # Regex to extract Unicode word characters


def extract_names_from_citations(wikitext):
    if wikitext is None:
        return set()
    name_parts = set()
    matches = AUTHOR_PATTERN.findall(wikitext)
    for match in matches:
        for name_field in match:
            if name_field:
                name_parts.update(NAME_PATTERN.findall(name_field))

    #tokens_to_remove = {"and", "the", "of", "for", "in", "not", "on", "an", "a", "at", "with", "And", "The", "Of", "For", "In", "Not", "On", "An", "At", "With",} 
    #name_parts -= tokens_to_remove # manually remove tokens

    return name_parts


def find_names_in_wikitext(wikitext, name_set):
    processed_text = filter_wikitext(wikitext)
    results = []
    for match in NAME_PATTERN.finditer(processed_text):
        word = match.group() 
        start = match.start()
        end = match.end() - 1
        
        if word in name_set:
            results.append({
                "word": word,
                "positionStart": start,
                "positionEnd": end
            })

    results = exclude_uniform_case_tokens(merge_adjacent_tokens_in_result_list(results))
    return results

