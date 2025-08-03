from typing import List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import logging

logging.basicConfig(level=logging.INFO)


class ContentEmbeddings:
    """
    Handles the generation of text embeddings using SentenceTransformers
    and indexing them using FAISS for efficient similarity search.
    """

    def __init__(self, chunks: List[str], model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the embedding class.

        Args:
            chunks (List[str]): Text segments to be embedded.
            model_name (str): Name of the sentence-transformer model.
        """
        self.chunks = chunks
        self.embeddings: Optional[np.ndarray] = None
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self) -> np.ndarray:
        """
        Generates normalized embeddings for provided text chunks.

        Returns:
            np.ndarray: Array of embedding vectors.
        
        Raises:
            ValueError: If no chunks are provided.
        """
        if not self.chunks:
            raise ValueError("No chunks provided for embedding.")

        logging.info("Generating embeddings...")
        self.embeddings = self.model.encode(
            self.chunks, convert_to_numpy=True, normalize_embeddings=True
        )
        return self.embeddings
    
    def embed_text(self, texts: List[str]) -> np.ndarray:
        """
        Generates normalized embeddings for new input texts (e.g., user queries).

        Args:
            texts (List[str]): List of input strings.

        Returns:
            np.ndarray: Embedding vectors for the input texts.
        """
        return self.model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )
        

    def create_faiss_index(self, index_path: str = "faiss_index.index") -> faiss.Index:
        """
        Creates a FAISS index with cosine similarity (via inner product)
        and saves it to disk.

        Args:
            index_path (str): Path to save the FAISS index.

        Returns:
            faiss.Index: The FAISS index object.

        Raises:
            ValueError: If embeddings have not been generated.
        """
        if self.embeddings is None:
            raise ValueError("Embeddings not generated yet.")

        dim = self.embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(self.embeddings)

        faiss.write_index(index, index_path)
        logging.info(f"FAISS index saved to {index_path} with {index.ntotal} vectors.")

        return index
    
    
    def load_faiss_index(self, index_path: str = "faiss_index.index") -> faiss.Index:
        """
        Loads a FAISS index from disk.

        Args:
            index_path (str): Path to the FAISS index file.

        Returns:
            faiss.Index: The loaded FAISS index.

        Raises:
            FileNotFoundError: If the index file does not exist.
        """
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index file not found: {index_path}")

        index = faiss.read_index(index_path)
        logging.info(f"FAISS index loaded from {index_path} with {index.ntotal} vectors.")
        return index

