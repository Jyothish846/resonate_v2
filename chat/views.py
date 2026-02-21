from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import ChatThread, Message
from .forms import MessageForm 

User = get_user_model()


# =========================================================
# 1. INBOX VIEW (Lists all active conversations)
# =========================================================
@login_required
def inbox_view(request):
    """Lists all chat threads the current user is a part of."""
    
    # Find all threads where the current user is either user1 OR user2
    threads = ChatThread.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).distinct()

    context = {
        'threads': threads,
        'page_title': 'Message Inbox'
    }
    return render(request, 'chat/inbox.html', context)


# =========================================================
# 2. START THREAD VIEW (Creates or finds a thread with another user)
# =========================================================
@login_required
def start_thread_view(request, username):
    """
    Redirects to an existing thread or creates a new one 
    with the specified username.
    """
    
    other_user = get_object_or_404(User, username=username)
    current_user = request.user
    
    # Prevent starting a chat with yourself
    if other_user == current_user:
        return redirect('inbox') # Or an error page

    # Find an existing thread between the two users (regardless of order)
    thread = ChatThread.objects.filter(
        Q(user1=current_user, user2=other_user) | 
        Q(user1=other_user, user2=current_user)
    ).first()

    # If no thread exists, create one
    if not thread:
        thread = ChatThread.objects.create(user1=current_user, user2=other_user)
    
    # Redirect to the thread view
    return redirect('thread', thread_id=thread.id)


# =========================================================
# 3. THREAD VIEW (Displays messages and handles new messages)
# =========================================================
@login_required
def thread_view(request, thread_id):
    """
    Displays messages in a thread and handles the message POST request.
    This is the core chat room logic.
    """
    
    thread = get_object_or_404(ChatThread, id=thread_id)
    
    # Security check: Ensure the user is a participant in this thread
    if request.user not in [thread.user1, thread.user2]:
        return redirect('inbox') # Deny access

    messages = thread.messages.all()
    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # Create the message and link it to the current user and thread
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()
            
            # Update the thread's 'updated' timestamp
            thread.save()
            
            # Since we're not using JS, we must redirect back to the page
            # to show the newly saved message.
            return redirect('thread', thread_id=thread.id) 

    # Determine the other user for display purposes
    other_user = thread.user1 if thread.user2 == request.user else thread.user2

    context = {
        'thread': thread,
        'messages': messages,
        'form': form,
        'other_user': other_user, # Pass the other user to the template
        'page_title': f'Chat with {other_user.username}'
    }
    return render(request, 'chat/thread.html', context)