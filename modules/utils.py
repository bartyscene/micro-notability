import re

COMBINED_PATTERN = re.compile(
    r"(?:"
        r"\{\{cite[^}]*?\}\}|"                    # Matches {{cite ...}}
        r"\{\{citation[^}]*?\}\}|"                # Matches {{citation ...}}
        r"\{\{harvard citation[^}]*?\}\}|"        # Matches {{citation ...}}
        r"\{\{rvnb[^}]*?\}\}|"                    # Matches {{rvnb ...}}
        r"\{\{harv[^}]*?\}\}|"                    # Matches {{harv ...}}
        r"\{\{harvtxt[^}]*?\}\}|"                 # Matches {{harvtxt ...}}
        r"\{\{harvcoltxt[^}]*?\}\}|"              # Matches {{harvcoltxt ...}}
        r"\{\{harvcol[^}]*?\}\}|"                 # Matches {{harvcol ...}}
        r"\{\{harvcolnb[^}]*?\}\}|"               # Matches {{harvcolnb ...}}
        r"\{\{harvs[^}]*?\}\}|"                   # Matches {{harvs ...}}
        r"\{\{harvp[^}]*?\}\}|"                   # Matches {{harvp ...}}
        r"\{\{harvc[^}]*?\}\}|"                   # Matches {{harvc ...}}
        r"\{\{citec[^}]*?\}\}|"                   # Matches {{citec ...}}
        r"\{\{sfn[^}]*?\}\}|"                     # Matches {{sfn ...}}
        r"\{\{sfnp[^}]*?\}\}|"                    # Matches {{sfnp ...}}
        r"\{\{sfnm[^}]*?\}\}|"                    # Matches {{sfnm ...}}
        r"\{\{sfnmp[^}]*?\}\}|"                   # Matches {{sfnmp ...}}
        r"\{\{efn[^}]*?\}\}|"                     # Matches {{efn ...}}
        r"<ref[^>]*?\/>|"                         # Matches self-closing <ref .../>
        r"<ref[^>]*?>.*?<\/ref>|"                 # Matches <ref ...>...</ref>
        r"<!--.*?-->|"                            # Matches HTML comments
        r"==\s*(?:External links|See also|Further reading)\s*==[\s\S]*"  # Matches headings and everything after
    r")",
    re.DOTALL | re.IGNORECASE
)

PIPE_PATTERN = re.compile(r"\[\[[^|\]]+\|([^|\]]+)\]\]")  # Matches [[...|...]] pattern

LETTER_FILTER_PATTERN = re.compile(r"[^\w\s.,!?;:'-]", re.UNICODE)  # Matches non-letter characters


def filter_wikitext(wikitext):
    if wikitext is None:
        return ""
    
    # Replace all matches with spaces preserving the original length
    processed_text = re.sub(
        COMBINED_PATTERN, 
        lambda m: ' ' * (m.end() - m.start()), 
        wikitext
    )

    processed_text = re.sub(
        PIPE_PATTERN,
        lambda m: m.group(0)[:2] + ' ' * (m.start(1) - m.start(0) - 2) + m.group(0)[m.start(1) - m.start(0):],
        processed_text
    )

    processed_text = re.sub(LETTER_FILTER_PATTERN, " ", processed_text)
    
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
            current["word"] += " " + next_token["word"]
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