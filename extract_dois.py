import bz2
import csv
import re
import argparse

import mwxml
from tqdm import tqdm

DOI_REGEX = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")

def process_dump(input_path: str, output_csv: str, show_total: bool=False) -> None:
    """
    Process the given bz2-compressed Wikipedia XML dump and write
    pages containing DOIs to CSV, showing a progress bar.
    
    If show_total=True and the dump header specifies a total page count,
    tqdm will show progress against that total.
    """
    with bz2.open(input_path, "rb") as f:
        dump = mwxml.Dump.from_file(f)
        total_pages = None
        if show_total and hasattr(dump, 'header') and dump.header:
            # header.total_pages exists in some dumps
            try:
                total_pages = int(dump.header.total_pages)
            except Exception:
                total_pages = None

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["NAME", "ID"])

        with bz2.open(input_path, "rb") as f:
            dump = mwxml.Dump.from_file(f)

            page_iter = dump
            if total_pages:
                page_iter = tqdm(dump, total=total_pages, desc="Pages")
            else:
                page_iter = tqdm(dump, desc="Pages", unit="pgs")

            for page in page_iter:
                if page.redirect:
                    continue

                latest_rev = None
                for rev in page:
                    if latest_rev is None or rev.timestamp > latest_rev.timestamp:
                        latest_rev = rev

                if latest_rev is None or not latest_rev.text:
                    continue

                if DOI_REGEX.search(latest_rev.text):
                    writer.writerow([page.title, page.id])


def main():
    parser = argparse.ArgumentParser(
        description="Extract pages with DOIs from a Wikipedia dump, with progress bar."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to bz2-compressed Wikipedia XML dump (e.g. enwiki-latest-pages-articles.xml.bz2)",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to output CSV file",
    )
    parser.add_argument(
        "--total",
        action="store_true",
        help="If set, try to read total page count from dump header and show it in the progress bar",
    )
    args = parser.parse_args()
    process_dump(args.input, args.output, show_total=args.total)


if __name__ == "__main__":
    main()
