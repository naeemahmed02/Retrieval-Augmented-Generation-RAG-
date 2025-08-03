from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('session/<str:session_id>/', views.switch_session, name='switch_session'),
]

