import re
from rapidfuzz import process, fuzz
from modules.utils import remove_diacritics, generate_name_variations

def extract_names_from_citations(wikitext):
    if wikitext is None:
        return set()
    
    citation_pattern = r"\{\{([^}]*cite[^}]*)\}\}"
    citations = re.findall(citation_pattern, wikitext, re.IGNORECASE)

    author_pattern = r"\b\w*author\w*\s*=\s*([^|}\n]+)"
    last_name_pattern = r"last\d*\s*=\s*([^|\n]+)"
    first_name_pattern = r"first\d*\s*=\s*([^|\n]+)"

    all_names = set()

    for citation in citations:
        author_names = re.findall(author_pattern, citation, re.IGNORECASE)
        for name in author_names:
            if ',' in name:
                all_names.update(n.strip() for n in name.split(',') if n.strip())
            else:
                all_names.add(name.strip())

        last_names = re.findall(last_name_pattern, citation, re.IGNORECASE)
        first_names = re.findall(first_name_pattern, citation, re.IGNORECASE)

        for last, first in zip(last_names, first_names):
            full_name = f"{first.strip()} {last.strip()}"
            all_names.add(full_name)

    cleaned_names = set()
    for entry in all_names:
        entry = entry.replace('.', '').replace(';', ',').replace("'", '').replace(' and ', ', ')
        parts = [part.strip() for part in entry.split(',')]

        for part in parts:
            words = part.split()
            processed_words = []

            for word in words:
                if word.isupper() and 2 <= len(word) <= 3:
                    processed_words.extend(list(word))
                else:
                    processed_words.append(word)

            reconstructed = ' '.join(processed_words)

            if reconstructed and reconstructed[0].isupper() and len(reconstructed) > 1:
                reconstructed_ascii = remove_diacritics(reconstructed)
                cleaned_names.add(reconstructed_ascii)

    return cleaned_names


def find_exact_matches_with_positions(text, name_set):
    expanded_name_set = generate_name_variations(name_set)
    words_with_positions = [
        (index, word.strip()) for index, word in enumerate(text.replace(',', ' ,')
                                                            .replace(';', ' ;')
                                                            .replace(':', ' :')
                                                            .replace('.', ' .')
                                                            .replace('!', ' !')
                                                            .replace('?', ' ?')
                                                            .replace('(', ' ( ')
                                                            .replace('{', ' { ')
                                                            .replace('[', ' [ ')
                                                            .replace(')', '  )')
                                                            .replace('}', '  }')
                                                            .replace(']', '  ]')
                                                            .replace("'s", '')
                                                            .replace("'", '')
                                                            .replace('"', '')
                                                            .split())
    ]

    normalized_words_with_positions = [
        (index, remove_diacritics(word)) for index, word in words_with_positions
    ]
    
    matches = []
    i = 0

    while i < len(normalized_words_with_positions):
        index, word = normalized_words_with_positions[i]
        
        if word in expanded_name_set:
            start_position = index
            combined_word = word
            end_position = start_position

            while (
                i + 1 < len(normalized_words_with_positions)
                and normalized_words_with_positions[i + 1][1] in expanded_name_set
                and normalized_words_with_positions[i + 1][0] == end_position + 1
            ):
                next_index, next_word = normalized_words_with_positions[i + 1]
                combined_word += f" {next_word}"
                end_position = next_index
                i += 1

            matches.append({
                "word": combined_word,
                "positionStart": start_position,
                "positionEnd": end_position,
            })
        
        i += 1

    return matches


def find_exact_matches(text, name_set):
    expanded_name_set = generate_name_variations(name_set)
    text = text.replace(',', '').replace('.', '').replace("'s", '')
    text_words = set(remove_diacritics(word.strip()) for word in text.split())
    return list(text_words.intersection(expanded_name_set))


def find_approximately_matches(text, candidate_names_set, threshold=80):
    preprocessed_candidates = {name.lower(): name for name in candidate_names_set}
    pattern = r'\b(?:[A-ZŠŽĆČŁŃÓŚŹÀÁÂÄÆÇÈÉÊËÌÍÎÏÑÒÓÔÖÙÚÛÜÝÞ][^\s]*\s)*[A-ZŠŽĆČŁŃÓŚŹÀÁÂÄÆÇÈÉÊËÌÍÎÏÑÒÓÔÖÙÚÛÜÝÞ][^\s]*\b'

    potential_names = re.findall(pattern, text, re.UNICODE)
    potential_names = list(set(potential_names))

    matches = []
    for potential_name in potential_names:
        processed_name = potential_name.lower()
        best_match, score, _ = process.extractOne(processed_name, preprocessed_candidates.keys(), scorer=fuzz.token_sort_ratio)
        
        if score >= threshold:
            matches.append(preprocessed_candidates[best_match])

    return list(set(matches))