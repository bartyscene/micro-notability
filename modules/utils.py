import unicodedata
import mwparserfromhell
import re

def filter_wikitext(wikitext):
    combined_pattern = re.compile(
        r"(?:"  # Start non-capturing group
        r"\{\{[cC]ite[^}]*?\}\}|"  # Matches {{cite ...}}
        r"<ref(?: name=\"[^\"]*\")?\/>|"  # Matches self-closing <ref .../>
        r"<ref(?: name=\"[^\"]*\")?>.*?<\/ref>|"  # Matches <ref ...>...</ref>
        r"<!--.*?-->"  # Matches HTML comments
        r")",  # End non-capturing group
        re.DOTALL
    )
    
    # Replace matches with spaces
    processed_text = re.sub(combined_pattern, lambda m: ' ' * (m.end() - m.start()), wikitext)
    
    return processed_text

def process_results(results):
    i = 0
    while i < len(results) - 1:
        current = results[i]
        next_token = results[i + 1]

        # Case 1: Merge if distance is 2
        if current["positionEnd"] + 2 == next_token["positionStart"]:
            current["word"] += " " + next_token["word"]
            current["positionEnd"] = next_token["positionEnd"]
            results.pop(i + 1)
            continue  # Recheck this token for further merging

        # Case 2: Merge with a period if distance is 3 and last token is uppercase
        current_words = current["word"].split()
        if (
            len(current_words[-1]) == 1 and  # Last token in current is a single character
            current_words[-1].isupper() and  # It's an uppercase character
            current["positionEnd"] + 3 == next_token["positionStart"]
        ):
            current["word"] += ". " + next_token["word"]
            current["positionEnd"] = next_token["positionEnd"]
            results.pop(i + 1)
            continue  # Recheck this token for further merging

        i += 1  # Move to the next token only if no merging occurred

    return results

def filter_results(results):
    filtered_results = []
    for item in results:
        tokens = item["word"].split()
        # Keep only if not all lowercase or not all uppercase
        if not (all(token.islower() for token in tokens) or all(token.isupper() for token in tokens)):
            filtered_results.append(item)
    return filtered_results


def normalize_token(input_str):
    """
    Normalize a token by removing diacritics, stripping non-letter characters,
    and handling possessives (removing "'s").
    """
    if input_str.lower().endswith("'s"):
        input_str = input_str[:-2]
    
    normalized_str = unicodedata.normalize('NFD', input_str)
    no_diacritics = ''.join(c for c in normalized_str if not unicodedata.combining(c))
    
    cleaned_str = re.sub(r'[^a-zA-Z\s]', '', no_diacritics)
    return cleaned_str

def remove_diacritics(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    return ''.join(c for c in normalized_str if not unicodedata.combining(c))

def wikitext_to_plain(wikitext_string):
    if not wikitext_string:
        return ""
    parsed_text = mwparserfromhell.parse(wikitext_string)
    return parsed_text.strip_code()

def generate_name_variations(names):
    variations = set()
    for name in names:
        name = name.strip()
        if not name:
            continue
        words = name.split()
        for word in words:
            if word[0].isupper() and len(word) > 1:
                variations.add(word)
    return variations