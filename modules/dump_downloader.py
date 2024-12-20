import xml.etree.ElementTree as ET
import os
import subprocess

class DumpDownloader:
    def __init__(self):
        self._namespace = {"mw": "http://www.mediawiki.org/xml/export-0.11/"}
        ET.register_namespace("", self._namespace["mw"])  # Register namespace for writing XML

    def _fetch_wiki_dump(self, page, limit):
        offset = "1"
        base_url = "https://en.wikipedia.org/w/index.php?title=Special:Export"
        files_downloaded = []
        filename = f"{page}_offset_{offset}.xml"

        while True:
            # Execute the curl command
            curl_command = [
                "curl",
                "-d", "",
                f"{base_url}&pages={page}&limit={limit}&offset={offset}",
                "-o", filename
            ]
            subprocess.run(curl_command)

            # Check if the file has content
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                print(f"No data fetched. Deleting {filename}.")
                if os.path.exists(filename):
                    os.remove(filename)
                break

            # Parse the XML to get the last <timestamp>
            try:
                tree = ET.parse(filename)
                root = tree.getroot()

                # Check if the file contains a <page> element
                page_element = root.find("mw:page", namespaces=self._namespace)
                if page_element is None:
                    print(f"File {filename} does not contain a <page> element. Deleting it.")
                    os.remove(filename)
                    break

                # Add the file to the list of downloaded files
                files_downloaded.append(filename)

                # Find all <timestamp> elements
                timestamps = root.findall(".//mw:timestamp", namespaces=self._namespace)
                if timestamps:
                    last_timestamp = timestamps[-1].text
                    print(f"Last timestamp: {last_timestamp}")
                    offset = last_timestamp
                    filename = f"{page}_offset_{offset.replace(':', '_').replace('-', '_')}.xml"
                else:
                    print("No <timestamp> found in the file. Stopping.")
                    break
            except ET.ParseError as e:
                print(f"Error parsing XML: {e}. Deleting {filename}.")
                os.remove(filename)
                break

        return files_downloaded

    def _merge_multiple_wiki_dumps(self, xml_files, output_file):
        # Parse the first XML file (base file)
        base_tree = ET.parse(xml_files[0])
        base_root = base_tree.getroot()

        # Find the <page> element in the base file
        base_page = base_root.find("mw:page", self._namespace)
        if base_page is None:
            raise ValueError("The first XML file must contain a <page> element.")

        # Iterate through the rest of the files and merge their <revision> elements
        for xml_file in xml_files[1:]:
            # Parse the current XML file
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Find the <page> element
            page = root.find("mw:page", self._namespace)
            if page is None:
                raise ValueError(f"File {xml_file} does not contain a <page> element.")

            # Find all <revision> elements and append them to the base file's <page>
            revisions = page.findall("mw:revision", self._namespace)
            for revision in revisions:
                base_page.append(revision)

        # Write the merged XML to the output file
        base_tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"Merged XML written to {output_file}")

    def automate_wiki_dump_process(self, page, output_file, limit=1000):
        print(f"Fetching Wiki dumps for page: {page}...")
        downloaded_files = self._fetch_wiki_dump(page, limit)
        
        if downloaded_files:
            print(f"Downloaded {len(downloaded_files)} files. Merging...")
            self._merge_multiple_wiki_dumps(downloaded_files, output_file)

            # Cleanup downloaded files
            for file in downloaded_files:
                os.remove(file)
            print(f"All temporary files have been removed.")
        else:
            print("No files downloaded. Nothing to merge.")