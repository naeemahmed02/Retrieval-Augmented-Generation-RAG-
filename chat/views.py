from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.files.storage import default_storage
from django.db.models import Q

from chat.models import Document, DocumentChunk, ChatSession, ChatMemory
from .forms import DocumentUploadForm
from rag_pipeline import RAGPipeline

import os
import uuid


def home(request):
    # Initialize or retrieve session_id
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = get_random_string(20)
        request.session["session_id"] = session_id

    # Get or create chat session
    chat_session, _ = ChatSession.objects.get_or_create(session_id=session_id)

    query = None
    answer = None
    form = DocumentUploadForm()
    selected_doc = None
    search = ""

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "message_form":
            query = request.POST.get("q")
            selected_doc_id = request.POST.get("selected_doc") or request.GET.get("selected_doc")

            if selected_doc_id:
                try:
                    # Safely convert to UUID
                    selected_doc_uuid = uuid.UUID(selected_doc_id)
                    selected_doc = Document.objects.get(id=selected_doc_uuid)
                    file_path = selected_doc.file.path
                except (ValueError, Document.DoesNotExist):
                    selected_doc = None
                    file_path = "RAG/resources/Deep Learning Interview questions.pdf"  # fallback
                    print("⚠️ Document not found or invalid UUID. Using fallback.")

                if query:
                    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

                    index_path = f"faiss_indexes/{selected_doc_id}.index"
                    rag_pipeline = RAGPipeline(file_path=file_path, model_name="gemini-1.5-flash", index_path=index_path)

                    if not os.path.exists(index_path):
                        print("📦 Index not found. Building new one...")
                        rag_pipeline.build_index()
                    else:
                        print("✅ Reusing existing FAISS index...")
                        rag_pipeline.load_index()

                    # Ask the query
                    answer = rag_pipeline.query(query, top_k=3)

                    # Save memory
                    if answer:
                        ChatMemory.objects.create(
                            session=chat_session,
                            user_query=query,
                            ai_response=answer,
                        )
                        if not chat_session.title:
                            chat_session.title = query[:100]
                            chat_session.save()

        elif form_type == "upload_form":
            form = DocumentUploadForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                print("📄 Document uploaded successfully!")
            else:
                print("❌ Invalid form submission.")

    # All sessions & history
    chat_history = chat_session.messages.order_by("timestamp")
    search = request.GET.get("search")
    all_session = ChatSession.objects.filter(Q(title__icontains=search)) if search else ChatSession.objects.all().order_by("-created_at")
    all_documents = Document.objects.all()

    context = {
        "query": query,
        "answer": answer,
        "chat_history": chat_history,
        "all_session": all_session,
        "form": form,
        "all_documents": all_documents,
        "selected_doc": selected_doc,
    }

    return render(request, "chat/home.html", context)


def new_chat(request):
    request.session.flush()
    session_id = get_random_string(20)
    chat_session = ChatSession.objects.create(session_id=session_id)
    request.session["session_id"] = session_id
    return redirect("home")

def switch_session(request, session_id):
    session = get_object_or_404(ChatSession, session_id = session_id)
    request.session['session_id'] = session.session_id
    return redirect('home')





















# from django.shortcuts import render, redirect
# from django.conf import settings
# from django.utils.crypto import get_random_string
# from django.core.files.storage import default_storage

# from chat.models import Document, DocumentChunk, ChatSession, ChatMemory
# from .forms import DocumentUploadForm
# from rag_pipeline import RAGPipeline

# import os


# def home(request):
#     # Initialize or retrieve session_id
#     session_id = request.session.get("session_id")
#     if not session_id:
#         session_id = get_random_string(20)
#         request.session["session_id"] = session_id

#     # Get or create chat session
#     chat_session, _ = ChatSession.objects.get_or_create(session_id=session_id)

#     query = None
#     answer = None
#     form = DocumentUploadForm()

#     if request.method == "POST":
#         form_type = request.POST.get("form_type")

#         if form_type == "message_form":
#             query = request.POST.get("q")
#             # selected_doc_id = request.POST.get("selected_doc")  # ⬅️ Reliable access
#             selected_doc_id = request.POST.get("selected_doc") or request.GET.get("selected_doc")

#             if query:
#                 try:
#                     selected_doc = Document.objects.get(id=selected_doc_id)
#                     file_path = selected_doc.file.path
#                 except Document.DoesNotExist:
#                     file_path = "RAG/resources/Deep Learning Interview questions.pdf"  # fallback
#                     print("⚠️ Document not selected. Using fallback.")

#                 # Set API key from settings
#                 os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

#                 # Index path — unique per document
#                 index_path = f"faiss_indexes/{selected_doc_id}.index"
#                 rag_pipeline = RAGPipeline(file_path=file_path, model_name="gemini-1.5-flash", index_path=index_path)

#                 if not os.path.exists(index_path):
#                     print("📦 Index not found. Building new one...")
#                     rag_pipeline.build_index()
#                 else:
#                     print("✅ Reusing existing FAISS index...")
#                     rag_pipeline.load_index()

#                 # Query
#                 answer = rag_pipeline.query(query, top_k=3)

#                 # Store chat memory
#                 if answer:
#                     ChatMemory.objects.create(
#                         session=chat_session,
#                         user_query=query,
#                         ai_response=answer,
#                     )

#                     if not chat_session.title:
#                         chat_session.title = query[:100]
#                         chat_session.save()

#         elif form_type == "upload_form":
#             form = DocumentUploadForm(request.POST, request.FILES)
#             if form.is_valid():
#                 form.save()
#                 print("📄 Document uploaded successfully!")
#             else:
#                 print("❌ Invalid form submission.")

#     # All sessions & history
#     chat_history = chat_session.messages.order_by("timestamp")
#     all_session = ChatSession.objects.all().order_by("-created_at")
#     all_documents = Document.objects.all()

#     context = {
#         "query": query,
#         "answer": answer,
#         "chat_history": chat_history,
#         "all_session": all_session,
#         "form": form,
#         "all_documents": all_documents,
#     }

#     return render(request, "chat/home.html", context)


# def new_chat(request):
#     request.session.flush()
#     session_id = get_random_string(20)
#     chat_session = ChatSession.objects.create(session_id=session_id)
#     request.session["session_id"] = session_id
#     return redirect("home")

























# from django.shortcuts import render, redirect
# import os
# from django.conf import settings
# from rag_pipeline import RAGPipeline
# from django.utils.crypto import get_random_string
# from chat.models import Document, DocumentChunk, ChatSession, ChatMemory
# from .forms import DocumentUploadForm


# def home(request):
    
#     # get or create session_id
#     session_id = request.session.get("session_id")
#     if not session_id:
#         session_id = get_random_string(20)
#         request.session["session_id"] = session_id
    
#     # Get or create Chat session
#     chat_session, _ = ChatSession.objects.get_or_create(session_id=session_id)
    
#     query = None
#     answer = None
#     form = DocumentUploadForm()
    
#     if request.method == "POST":
#         form_type = request.POST.get('form_type')
#         if form_type == "message_form":
            
#             query = request.POST.get("q")
#             if query:
#                 # get answer
#                 selected_doc_id = request.GET.get('selected_doc')
#                 print(selected_doc_id)
#                 try:
#                     selected_doc = Document.objects.get(id = selected_doc_id)
#                     file_path = selected_doc.file.path
#                     print(file_path)
#                 except Document.DoesNotExist:
#                     print("Document Does not selected.")
#                     file_path="RAG/resources/Deep Learning Interview questions.pdf"
#                 os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
#                 rag_pipeline = RAGPipeline(file_path=file_path, model_name="gemini-1.5-flash")
#                 rag_pipeline.build_index()
#                 answer = rag_pipeline.query(query, top_k=3)
                
#                 if answer:
#                     ChatMemory.objects.create(
#                         session= chat_session,
#                         user_query = query,
#                         ai_response = answer
#                     )
                    
#                     if not chat_session.title:
#                         chat_session.title = query[:100]
#                         chat_session.save()
#                         print(chat_session.title)
#         else:
#             form = DocumentUploadForm(request.POST, request.FILES)
#             if form.is_valid():
#                 form.save()
#                 print("Document saved successfully!")
#             else:
#                 form = DocumentUploadForm()
            
    
#     # Chat History
#     chat_history = chat_session.messages.order_by('timestamp')
#     all_session = ChatSession.objects.all().order_by('-created_at')
#     all_documents = Document.objects.all()
    
#     context = {
#         "query": query,
#         "answer": answer,
#         "chat_history": chat_history,
#         'all_session' : all_session,
#         'form' : form,
#         'all_documents' : all_documents
#     }
#     return render(request, "chat/home.html", context)



# def new_chat(request):
#     request.session.flush()
#     session_id = get_random_string(20)
#     chat_session = ChatSession.objects.create(session_id = session_id)
#     request.session['session_id'] = session_id
#     return redirect('home')