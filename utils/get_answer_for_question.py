from rag_pipeline import RAGPipeline
import os
from django.conf import settings

def rag_setup():
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    rag_pipeline = RAGPipeline(file_path="RAG/resources/Deep Learning Interview questions.pdf", model_name="gemini-1.5-flash")
    rag_pipeline.build_index()

def get_answer(question:str, k:int = 3) -> str:
    
    # return rag_pipeline.query(question, k)
    pass

        
