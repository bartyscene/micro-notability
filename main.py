from modules.dump_processor import process_wikipedia_dump_file

if __name__ == "__main__":
    input_dump = "dumps/rna.xml"
    output_file = "output/rna_output.txt"
    process_wikipedia_dump_file(input_dump, output_file)