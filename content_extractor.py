import fitz
from typing import Optional
from langchain_community.document_loaders import WebBaseLoader

class ContentExtractor:
    """
    Extracts raw text from either a PDF file or a web page.
    """

    def __init__(self, file_path: Optional[str] = None, source_link: Optional[str] = None):
        self.file_path = file_path
        self.source_link = source_link
        self.raw_text = ""

    def extractor(self) -> str:
        """
        Extracts text from the given source.

        Returns:
            str: The extracted raw text.

        Raises:
            FileNotFoundError: If the PDF file cannot be opened.
            RuntimeError: If the web page cannot be loaded.
            ValueError: If neither source is provided.
        """
        if self.file_path:
            try:
                doc = fitz.open(self.file_path)
                text = "".join(page.get_text() for page in doc)
                self.raw_text = text
                return text
            except Exception as e:
                raise FileNotFoundError(f"Could not open the file: {e}")

        elif self.source_link:
            try:
                loader = WebBaseLoader(self.source_link)
                doc = loader.load()
                self.raw_text = doc[0].page_content
                return self.raw_text
            except Exception as e:
                raise RuntimeError(f"Failed to load content from web: {e}")

        else:
            raise ValueError("Either 'file_path' or 'source_link' must be provided.")
               
            

if __name__== "__main__":
    ext_obj = ContentExtractor(file_path="sample.pdf")
    content = ext_obj.extractor()
    print(content[:500])