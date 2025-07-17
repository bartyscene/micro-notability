# python _extract_doi_from_artickle.py ./dumps/02_light_emitting_diode.xml 1.txt
import argparse
import sys
import re

import mwxml

# Matches strings like "10.1000/xyz123" according to DOI syntax rules
TEST_1 = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9+<>]+)\b")

TEST_2 = re.compile(r'\b(10\.[0-9]{4,}(?:\.[0-9]+)*/(?:(?!["&\'<>])\S)+)\b')

DOI_REGEX = re.compile(r'\b(10\.[0-9]{4,}(?:\.[0-9]+)*/[^\s"\'<>|]+)(?=\b|\|)')

#ISBN-13 ^(?:97[89])[\-\ ]?(?:\d[\-\ ]?){10}\d$
#ISBN-10 ^(?:\d[\-\ ]?){9}[0-9X]$

def extract_dois(text):
    """Return all DOI matches in the given text."""
    return DOI_REGEX.findall(text or "")

def main():
    parser = argparse.ArgumentParser(
        description="Extract all DOIs from all revisions in a Wikipedia XML dump")
    parser.add_argument("input_xml", help="Path to the Wikipedia XML dump file")
    parser.add_argument("output_txt", help="Path to write the extracted DOIs (one per line)")
    args = parser.parse_args()

    dois_seen = set()

    # 1) Open and iterate through the XML dump
    try:
        with open(args.input_xml, 'rb') as dumpfile:
            dump = mwxml.Dump.from_file(dumpfile)
            for page in dump:
                for revision in page:
                    wikitext = revision.text
                    if not wikitext:
                        continue
                    # 2) Extract any DOIs in this revision’s text
                    for doi in extract_dois(wikitext):
                        dois_seen.add(doi)
    except FileNotFoundError:
        sys.stderr.write(f"Error: could not open input file {args.input_xml}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error while parsing XML: {e}\n")
        sys.exit(1)

    # 3) Write unique DOIs out, one per line
    try:
        with open(args.output_txt, 'w', encoding='utf-8') as out:
            for doi in sorted(dois_seen):
                out.write(doi + "\n")
    except Exception as e:
        sys.stderr.write(f"Error writing to output file {args.output_txt}: {e}\n")
        sys.exit(1)

    print(f"Done: extracted {len(dois_seen)} unique DOIs to {args.output_txt}")

if __name__ == "__main__":
    main()

