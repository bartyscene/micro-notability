import unicodedata
import mwparserfromhell
import re

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