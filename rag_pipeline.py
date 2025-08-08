import os
import uuid
from django.utils.text import slugify
from RAG.content_extractor import ContentExtractor
from RAG.content_preprocessor import ContentPreprocessor
from RAG.content_chunker import ContentChunker
from RAG.content_embeddings import ContentEmbeddings
from RAG.llm_interface import LLMInterface
from chat.models import Document, DocumentChunk


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation (RAG) pipeline.
    """

    def __init__(self, file_path: str, model_name: str, index_path: str = None):
        self.file_path = file_path
        self.model_name = model_name
        self.chunks = []
        self.embedder = None
        self.index = None

        # Automatically generate FAISS index path if not provided
        basename = os.path.basename(file_path)
        filename_wo_ext = os.path.splitext(basename)[0]
        safe_name = slugify(filename_wo_ext)
        self.index_path = index_path or f"faiss_indexes/{safe_name}.index"

    def build_index(self):
        """
        Build FAISS index from the input document.
        """
        # Step 1: Extract
        extractor = ContentExtractor(file_path=self.file_path)
        raw_text = extractor.extractor()

        # Step 2: Preprocess
        preprocessor = ContentPreprocessor(raw_text)
        clean_text = preprocessor.preprocess()

        # Step 3: Chunk
        chunker = ContentChunker()
        self.chunks = chunker.text_chunker(clean_text)

        # Step 4: Embedding + Index
        self.embedder = ContentEmbeddings(self.chunks)
        self.embeddings = self.embedder.generate_embeddings()
        self.index = self.embedder.create_faiss_index(self.index_path)

        # Step 5: Store Chunks in DB
        doc_name = os.path.basename(self.file_path)
        doc_slug = slugify(doc_name)

        doc, _ = Document.objects.get_or_create(name=doc_name, file=self.file_path)

        for chunk_text in self.chunks:
            DocumentChunk.objects.create(
                vector_id=uuid.uuid4(),
                document=doc,
                text=chunk_text,
            )

    def load_index(self):
        """
        Load existing FAISS index from disk.
        """
        if not self.embedder:
            self.embedder = ContentEmbeddings([])
        self.index = self.embedder.load_faiss_index(self.index_path)

        if not self.chunks:
            doc_name = os.path.basename(self.file_path)
            doc = Document.objects.filter(name=doc_name, file=self.file_path).first()
            if doc:
                self.chunks = list(
                    DocumentChunk.objects.filter(document=doc).values_list(
                        "text", flat=True
                    )
                )

    def query(self, user_question: str, top_k: int = 3) -> str:
        """
        Query the RAG system: search similar chunks and generate a Gemini response.
        """
        if not self.index or not self.embedder:
            raise RuntimeError("Index not built or loaded.")

        query_vector = self.embedder.embed_text([user_question])[0].reshape(1, -1)
        scores, indices = self.index.search(query_vector, top_k)

        # Ensure chunk index is valid
        context_chunks = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                context_chunks.append(self.chunks[idx])
        context = "\n".join(context_chunks)

        # Prompt template
        system_prompt = """
        Act as a smart AI assistant who helps the user based on provided context. If you don't find the context say I did not found the context. Learn from the context and answer in a logical and a structured flow. Please do not halucinate if did not find the context.
        """
        user_prompt = ("""
            Using the context below, answer the user's question as if you're teaching them step-by-step. Build the explanation gradually like a story—from basic understanding to deeper insight. Ensure each section flows into the next.

Focus on:
- Starting simply, then deepening intuition.
- Making smooth, logical transitions between concepts.
- Explaining like you're mentoring a curious developer or student.

Context:
{input}

Question:
{user_question}"""

        )

        llm = LLMInterface(model_name=self.model_name)
        response = llm.run(
            system_prompt,
            user_prompt,
            {"input": context, "user_question": user_question},
        )
        return response


# import os
# import uuid
# from django.utils.text import slugify
# from RAG.content_extractor import ContentExtractor
# from RAG.content_preprocessor import ContentPreprocessor
# from RAG.content_chunker import ContentChunker
# from RAG.content_embeddings import ContentEmbeddings
# from RAG.llm_interface import LLMInterface
# from chat.models import Document, DocumentChunk


# class RAGPipeline:
#     """
#     End-to-end Retrieval-Augmented Generation (RAG) pipeline.
#     """

#     def __init__(self, file_path: str, model_name: str, index_path: str = "faiss_index.index"):
#         self.file_path = file_path
#         self.model_name = model_name
#         self.index_path = index_path
#         self.chunks = []
#         self.embedder = None
#         self.index = None


#     # Extract name from file to use as index filename
#         basename = os.path.basename(file_path)
#         filename_wo_ext = os.path.splitext(basename)[0]
#         self.index_path = f"faiss_indexes/{filename_wo_ext}.index"

#     def build_index(self):
#         """
#         Build FAISS index from the input document.
#         """
#         # Step 1: Extract
#         extractor = ContentExtractor(file_path=self.file_path)
#         raw_text = extractor.extractor()

#         # Step 2: Preprocess
#         preprocessor = ContentPreprocessor(raw_text)
#         clean_text = preprocessor.preprocess()

#         # Step 3: Chunk
#         chunker = ContentChunker()
#         self.chunks = chunker.text_chunker(clean_text)

#         # Step 4: Embedding + Index
#         self.embedder = ContentEmbeddings(self.chunks)
#         self.embeddings = self.embedder.generate_embeddings()
#         self.index = self.embedder.create_faiss_index(self.index_path)

#         # Step 5: Store Chunks in DB
#         doc_name = os.path.basename(self.file_path)
#         doc_slug = slugify(doc_name)

#         doc, _ = Document.objects.get_or_create(name=doc_name, file=self.file_path)

#         for chunk_text in self.chunks:
#             DocumentChunk.objects.create(
#                 vector_id=uuid.uuid4(),
#                 document=doc,
#                 text=chunk_text,
#             )

#     def load_index(self):
#         """
#         Load existing FAISS index from disk.
#         """
#         if not self.embedder:
#             self.embedder = ContentEmbeddings([])  # Pass dummy list
#         self.index = self.embedder.load_faiss_index(self.index_path)

#         # Rebuild chunks if needed
#         if not self.chunks:
#             doc_name = os.path.basename(self.file_path)
#             doc = Document.objects.filter(name=doc_name, file=self.file_path).first()
#             if doc:
#                 self.chunks = list(DocumentChunk.objects.filter(document=doc).values_list("text", flat=True))

#     def query(self, user_question: str, top_k: int = 3) -> str:
#         """
#         Query the RAG system: search similar chunks and generate a Gemini response.
#         """
#         if not self.index or not self.embedder:
#             raise RuntimeError("Index not built or loaded.")

#         query_vector = self.embedder.embed_text([user_question])[0].reshape(1, -1)
#         scores, indices = self.index.search(query_vector, top_k)

#         context = "\n".join(self.chunks[i] for i in indices[0])

#         # Prompt template
#         system_prompt = (
#             "You are an AI assistant that provides answers based strictly on retrieved documents. "
#             "Do not generate information beyond the provided context. "
#             "You may explain topics in depth and use external sources to enhance the explanation, "
#             "but do not hallucinate or fabricate content. "
#             "If the answer cannot be found in the context, clearly state that and explain why."
#         )

#         user_prompt = "Using the context below, answer the question as accurately as possible:\n\n{input}"

#         llm = LLMInterface(model_name=self.model_name)
#         response = response = llm.run(
#             system_prompt,
#             user_prompt,
#             {"input": f"{context}\n\nQuestion: {user_question}"},
#         )
#         return response


# from RAG.content_extractor import ContentExtractor
# from RAG.content_preprocessor import ContentPreprocessor
# from RAG.content_chunker import ContentChunker
# from RAG.content_embeddings import ContentEmbeddings
# from RAG.llm_interface import LLMInterface
# from chat.models import Document, DocumentChunk, ChatSession, ChatMemory
# from django.utils.text import slugify
# import os
# import uuid


# class RAGPipeline:
#     """
#     A class to manage the end-to-end Retrieval-Augmented Generation (RAG) pipeline.

#     This pipeline performs the following steps:
#     1. Extracts text from a file.
#     2. Preprocesses the extracted text.
#     3. Splits the text into manageable chunks.
#     4. Generates embeddings for the chunks.
#     5. Builds and stores a FAISS index.
#     6. Accepts a query and retrieves top-k similar chunks.
#     7. Uses an LLM to generate a response based on the retrieved context.
#     """

#     def __init__(
#         self, file_path: str, model_name: str, index_path: str = "faiss_index.index"
#     ):
#         """
#         Initializes the RAGPipeline.

#         Args:
#             file_path (str): Path to the input document (PDF).
#             model_name (str): Name of the LLM to use (e.g., "gemini-1.5-flash").
#             index_path (str, optional): Path to save the FAISS index. Defaults to "faiss_index.index".
#         """
#         self.file_path = file_path
#         self.model_name = model_name
#         self.index_path = index_path

#     def build_index(self):
#         """
#         Executes all preprocessing steps:
#         - Extract text from the document.
#         - Clean and normalize the text.
#         - Split text into chunks.
#         - Generate embeddings for chunks.
#         - Build and save a FAISS index.
#         """
#         extractor = ContentExtractor(file_path=self.file_path)
#         raw_text = extractor.extractor()

#         preprocessor = ContentPreprocessor(raw_text)
#         clean_text = preprocessor.preprocess()

#         chunker = ContentChunker()
#         self.chunks = chunker.text_chunker(clean_text)

#         embedder = ContentEmbeddings(self.chunks)
#         self.embeddings = embedder.generate_embeddings()
#         self.index = embedder.create_faiss_index(self.index_path)
#         self.embedder = embedder

#         doc_name = os.path.basename(self.file_path)
#         doc_slug = slugify(doc_name)

#         # Ensure doc is always set
#         doc, _ = Document.objects.get_or_create(name=doc_name, file=self.file_path)

#         # Save chunks
#         for idx, chunk in enumerate(self.chunks):
#             if not DocumentChunk.objects.filter(document=doc, vector_id=idx).exists():
#                 DocumentChunk.objects.create(
#                     vector_id=uuid.uuid4(),
#                     document=doc,
#                     text=chunk,
#                 )

#     def query(self, user_question: str, top_k: int = 3) -> str:
#         """
#         Answers a user query using the RAG approach:
#         - Embeds the query.
#         - Searches top-k similar chunks.
#         - Sends context and query to LLM for response.

#         Args:
#             user_question (str): The user’s natural language query.
#             top_k (int, optional): Number of top documents to retrieve. Defaults to 3.

#         Returns:
#             str: The generated response from the language model.
#         """
#         query_vector = self.embedder.embed_text([user_question])[0].reshape(1, -1)
#         scores, indices = self.index.search(query_vector, top_k)

#         context = "\n".join(self.chunks[i] for i in indices[0])

#         llm = LLMInterface(model_name=self.model_name)
#         system_prompt = (
#             "You are an AI assistant that provides answers based strictly on retrieved documents. "
#             "Do not generate information beyond the provided context. "
#             "You may explain topics in depth and use external sources to enhance the explanation, "
#             "but do not hallucinate or fabricate content. "
#             "If the answer cannot be found in the context, clearly state that and explain why."
#         )

#         user_prompt = "Using the context below, answer the question as accurately as possible:\n\n{input}"

#         response = llm.run(
#             system_prompt,
#             user_prompt,
#             {"input": f"{context}\n\nQuestion: {user_question}"},
#         )
#         return response
