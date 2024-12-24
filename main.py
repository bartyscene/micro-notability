from modules.dump_processor import process_wikipedia_dump_file
from modules.text_files_generator import process_json_file
from modules.dump_downloader import DumpDownloader


if __name__ == "__main__":
    input_dump = "dumps/15_crispr.xml"
    output_file = "output/crispr_output.txt"
    process_wikipedia_dump_file(input_dump, output_file)
    #process_json_file("wikitext/filtered_text.json")