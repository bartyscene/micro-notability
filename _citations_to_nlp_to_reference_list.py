# python _citations_to_nlp_to_reference_list.py ./dumps/02_light_emitting_diode.xml 1.txt
import argparse
import sys
import re

import mwxml
from transformers import pipeline

pattern = re.compile(r'(?i){{\s*cite\b.*?}}')

def extract_cite_templates(text):
    return pattern.findall(text)

def main():
    parser = argparse.ArgumentParser(
        description="Extract all PERSON entities from cite templates in a Wikipedia XML dump using a Transformer NER model")
    parser.add_argument("input_xml", help="Path to the Wikipedia XML dump file")
    parser.add_argument("output_txt", help="Path to write the extracted PERSON entities (one per line)")
    args = parser.parse_args()

    refs_seen = set()
    try:
        with open(args.input_xml, 'rb') as dumpfile:
            dump = mwxml.Dump.from_file(dumpfile)
            for page in dump:
                for revision in page:
                    wikitext = revision.text or ""
                    for tpl in extract_cite_templates(wikitext):
                        refs_seen.add(tpl)
    except FileNotFoundError:
        sys.stderr.write(f"Error: could not open input file {args.input_xml}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error while parsing XML: {e}\n")
        sys.exit(1)

    ner = pipeline(
        "ner",
        model="dbmdz/bert-large-cased-finetuned-conll03-english",
        tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english",
        grouped_entities=True
    )

    persons_seen = set()
    for tpl in refs_seen:
        for ent in ner(tpl):
            if ent["entity_group"] in ("PER", "PERSON"):
                persons_seen.add(ent["word"])

    try:
        with open(args.output_txt, 'w', encoding='utf-8') as out:
            for person in sorted(persons_seen):
                out.write(person + "\n")
    except Exception as e:
        sys.stderr.write(f"Error writing to output file {args.output_txt}: {e}\n")
        sys.exit(1)

    print(f"Done: extracted {len(persons_seen)} unique PERSON entities to {args.output_txt}")

if __name__ == "__main__":
    main()
