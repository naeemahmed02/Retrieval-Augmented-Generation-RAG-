from rag_pipeline import RAGPipeline
import os

if __name__ == "__main__":
    os.environ["GOOGLE_API_KEY"] = "AIzaSyAdyt8Gf0IrybxrZvfdSiqXCFUmBnHY3Kw"

    pipeline = RAGPipeline(file_path="resources/Deep Learning Interview questions.pdf",model_name="gemini-1.5-flash")
    
    pipeline.build_index()
    
    question = "What is perceptron in deep learning and what activation function should we use?"
    answer = pipeline.query(question, top_k=3)
    
    print("\nAnswer from RAG system:\n")
    print(answer)
