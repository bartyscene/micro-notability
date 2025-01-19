import re
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

    def split_into_sentences(self, text):
        """
        Split text into sentences based on punctuation or newlines.
        
        Args:
            text (str): The input text to split.
        
        Returns:
            list: A list of sentences.
        """
        text = re.sub(r'\n+', '\n', text.strip())
        sentences = re.split(r'(?<=[.!?])\s+|\n', text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

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
        sentences = self.split_into_sentences(text)
        
        persons_list = []
        for sentence in sentences:
            results = self.nlp(sentence)
            for entity in results:
                if entity['entity_group'] == "PER":
                    persons_list.append({
                        "word": entity['word'],
                        "positionStart": entity['start'],
                        "positionEnd": entity['end']
                    })

        return persons_list
