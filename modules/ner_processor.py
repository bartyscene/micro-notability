import spacy

class NameEntityRecognizer:
    def __init__(self, use_gpu=True):
        """
        Initialize the SpaCy model with optional GPU support.

        Args:
            use_gpu (bool): Whether to require or prefer using a GPU. Defaults to True.
                            If False, forces CPU usage.
        """
        if use_gpu:
            try:
                spacy.require_gpu()
                print("GPU is enabled for SpaCy.")
            except Exception as e:
                print(f"GPU is not available. Falling back to CPU. Error: {e}")
        
        self.nlp = spacy.load("en_core_web_lg")
        self.nlp.disable_pipes("tagger", "parser", "lemmatizer")

    def extract_names(self, text):
        """
        Extract PERSON entities from the given text.

        Args:
            text (str): The input text to process.

        Returns:
            list: A list of unique PERSON entity names found in the text.
        """
        doc = self.nlp(text)
        persons_set = set()

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                persons_set.add(ent.text)

        return list(persons_set)

