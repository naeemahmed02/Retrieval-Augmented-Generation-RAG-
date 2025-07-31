from content_extractor import ContentExtractor
from content_preprocessor import ContentPreprocessor
from content_chunker import ContentChunker
from content_embeddings import ContentEmbeddings
from llm_interface import LLMInterface
import os


class RAGPipeline:
    """
    A class to manage the end-to-end Retrieval-Augmented Generation (RAG) pipeline.
    
    This pipeline performs the following steps:
    1. Extracts text from a file.
    2. Preprocesses the extracted text.
    3. Splits the text into manageable chunks.
    4. Generates embeddings for the chunks.
    5. Builds and stores a FAISS index.
    6. Accepts a query and retrieves top-k similar chunks.
    7. Uses an LLM to generate a response based on the retrieved context.
    """

    def __init__(self, file_path: str, model_name: str, index_path: str = "faiss_index.index"):
        """
        Initializes the RAGPipeline.

        Args:
            file_path (str): Path to the input document (PDF).
            model_name (str): Name of the LLM to use (e.g., "gemini-1.5-flash").
            index_path (str, optional): Path to save the FAISS index. Defaults to "faiss_index.index".
        """
        self.file_path = file_path
        self.model_name = model_name
        self.index_path = index_path

    def build_index(self):
        """
        Executes all preprocessing steps:
        - Extract text from the document.
        - Clean and normalize the text.
        - Split text into chunks.
        - Generate embeddings for chunks.
        - Build and save a FAISS index.
        """
        extractor = ContentExtractor(file_path=self.file_path)
        raw_text = extractor.extractor()

        preprocessor = ContentPreprocessor(raw_text)
        clean_text = preprocessor.preprocess()

        chunker = ContentChunker()
        self.chunks = chunker.text_chunker(clean_text)

        embedder = ContentEmbeddings(self.chunks)
        self.embeddings = embedder.generate_embeddings()
        self.index = embedder.create_faiss_index(self.index_path)
        self.embedder = embedder

    def query(self, user_question: str, top_k: int = 3) -> str:
        """
        Answers a user query using the RAG approach:
        - Embeds the query.
        - Searches top-k similar chunks.
        - Sends context and query to LLM for response.

        Args:
            user_question (str): The user’s natural language query.
            top_k (int, optional): Number of top documents to retrieve. Defaults to 3.

        Returns:
            str: The generated response from the language model.
        """
        query_vector = self.embedder.embed_text([user_question])[0].reshape(1, -1)
        scores, indices = self.index.search(query_vector, top_k)

        context = "\n".join(self.chunks[i] for i in indices[0])

        llm = LLMInterface(model_name=self.model_name)
        system_prompt = "You are an AI assistant that answers based on retrieved documents."
        user_prompt = "Based on the following context, answer the question:\n\n{input}"

        response = llm.run(
            system_prompt,
            user_prompt,
            {"input": f"{context}\n\nQuestion: {user_question}"}
        )
        return response
