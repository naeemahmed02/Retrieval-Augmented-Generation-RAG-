from django.contrib import admin

from django.contrib import admin
from .models import Document, DocumentChunk, ChatMemory, ChatSession

admin.site.register(Document)
admin.site.register(DocumentChunk)
admin.site.register(ChatMemory)
admin.site.register(ChatSession)