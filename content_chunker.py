from langchain.text_splitter import RecursiveCharacterTextSplitter
from content_extractor import ContentExtractor
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class ContentChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[str] = []

    def text_chunker(self, text: str) -> List[str]:
        """
        Splits the given text into overlapping chunks using LangChain's RecursiveCharacterTextSplitter.

        Args:
            text (str): Raw or preprocessed input text.

        Returns:
            List[str]: List of text chunks.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text must be a non-empty string.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "]
        )
        self.chunks = splitter.split_text(text)
        logging.info(f"Chunked into {len(self.chunks)} segments.")
        return self.chunks


if __name__ == "__main__":
    try:
        ext_obj = ContentExtractor(file_path="sample.pdf")
        content = ext_obj.extractor()

        chunker_obj = ContentChunker()
        chunks = chunker_obj.text_chunker(content)

        print(f"First chunk (length={len(chunks[0])}):\n{chunks[0]}")

    except Exception as e:
        logging.error(f"Failed during chunking: {e}")
