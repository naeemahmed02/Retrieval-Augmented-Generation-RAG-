import re
import logging
from content_extractor import ContentExtractor

logging.basicConfig(level=logging.INFO)

class ContentPreprocessor:
    """
    Cleans and standardizes raw text extracted from documents or webpages.
    """
    
    def __init__(self, extracted_text: str):
        self.extracted_text = extracted_text
        self.preprocessed_text = ""
        
    def preprocess(self) -> str:
        """
        Applies cleaning operations:
        - Lowercase
        - Whitespace normalization
        - Unicode character removal
        - Quote standardization
        - Remove unwanted special characters

        Returns:
            str: Preprocessed clean text
        """
        text = self.extracted_text
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'[“”‘’]', '"', text)
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        self.preprocessed_text = text.strip()
        return self.preprocessed_text
    
    
if __name__ == "__main__":
    try:
        extractor = ContentExtractor(file_path="sample.pdf")
        text = extractor.extractor()

        preprocessor = ContentPreprocessor(text)
        processed_text = preprocessor.preprocess()

        print(processed_text[:500])
    except Exception as e:
        logging.error(f"Error: {e}")
