from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from modules.utils import filter_wikitext

class RobertaNameEntityRecognizer:
    def __init__(self):
        """
        Initialize the Hugging Face model and tokenizer pipeline for NER.
        """
        self.tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/roberta-large-ner-english")
        self.model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/roberta-large-ner-english")
        self.nlp = pipeline('ner', model=self.model, tokenizer=self.tokenizer, aggregation_strategy="simple")

    def extract_names(self, wikitext):
        """
        Extract PERSON entities from the given text.

        Args:
            wikitext (str): The input text to process.

        Returns:
            list: A list of objects containing PERSON entity information:
                  {
                      "word": word,
                      "positionStart": start,
                      "positionEnd": end
                  }
        """
        text = filter_wikitext(wikitext)
        results = self.nlp(text)
        persons_list = []

        for entity in results:
            if entity['entity_group'] == "PER":
                persons_list.append({
                    "word": entity['word'],
                    "positionStart": entity['start'],
                    "positionEnd": entity['end']
                })

        return persons_list
