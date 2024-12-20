from modules.dump_processor import process_wikipedia_dump_file

if __name__ == "__main__":
    input_dump = "dumps/01_wearable_computer.xml"
    output_file = "output/01_wearable_computer_output.txt"
    process_wikipedia_dump_file(input_dump, output_file)