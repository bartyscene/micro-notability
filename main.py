from modules.dump_processor import process_wikipedia_dump_file

if __name__ == "__main__":
    input_dump = "dumps/llm.xml"
    output_file = "output/llm_output.txt"
    process_wikipedia_dump_file(input_dump, output_file)