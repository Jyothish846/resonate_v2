from django.urls import path
from . import views

urlpatterns = [
    # Shows the list of all active conversations (the "Inbox")
    path('', views.inbox_view, name='inbox'),
    
    # Opens a specific conversation thread
    path('<int:thread_id>/', views.thread_view, name='thread'),
    
    # Allows a user to start a new chat thread from another user's profile
    path('start/<str:username>/', views.start_thread_view, name='start_thread'),
]