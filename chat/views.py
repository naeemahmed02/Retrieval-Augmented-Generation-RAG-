from django.shortcuts import render, redirect
import os
from django.conf import settings
from rag_pipeline import RAGPipeline
from django.utils.crypto import get_random_string
from chat.models import Document, DocumentChunk, ChatSession, ChatMemory
from .forms import DocumentUploadForm


def home(request):
    
    # get or create session_id
    session_id = request.session.get("session_id") or request.session.get("session_id")
    if not session_id:
        session_id = get_random_string(20)
        request.session["session_id"] = session_id
    
    # Get or create Chat session
    chat_session, _ = ChatSession.objects.get_or_create(session_id=session_id)
    
    query = None
    answer = None
    
    if request.method == "POST":
        query = request.POST.get("q")
        if query:
            print(query)
            # get answer
            os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
            rag_pipeline = RAGPipeline(file_path="RAG/resources/Deep Learning Interview questions.pdf", model_name="gemini-1.5-flash")
            rag_pipeline.build_index()
            answer = rag_pipeline.query(query, top_k=3)
            
            if answer:
                ChatMemory.objects.create(
                    session= chat_session,
                    user_query = query,
                    ai_response = answer
                )
                
                if not chat_session.title:
                    chat_session.title = query[:100]
                    chat_session.save()
                    print(chat_session.title)
    
    # Chat History
    chat_history = chat_session.messages.order_by('timestamp')
    all_session = ChatSession.objects.all().order_by('-created_at')
    
    context = {
        "query": query,
        "answer": answer,
        "chat_history": chat_history,
        'all_session' : all_session
    }
    return render(request, "chat/home.html", context)



def new_chat(request):
    request.session.flush()
    session_id = get_random_string(20)
    chat_session = ChatSession.objects.create(session_id = session_id)
    request.session['session_id'] = session_id
    return redirect('home')