from django.db import models
from django.contrib.auth import get_user_model

# Get the custom User model defined in your Django project (likely in 'accounts' or similar)
User = get_user_model() 


# ------------------------------------------------------------------
# 1. ChatThread Model (Represents a conversation between two users)
# ------------------------------------------------------------------
class ChatThread(models.Model):
    """Represents a private conversation between two users."""
    
    # The users involved in this specific thread.
    # The related_name is important for filtering threads per user.
    user1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chat_threads_as_user1'
    )
    user2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='chat_threads_as_user2'
    )
    
    # Timestamp of the last message sent in this thread (useful for sorting inbox)
    updated = models.DateTimeField(auto_now=True) 
    # Timestamp when the thread was first created
    timestamp = models.DateTimeField(auto_now_add=True) 

    class Meta:
        # Ensures that a thread between two users (e.g., A and B) 
        # is unique, regardless of the order (A, B) or (B, A).
        unique_together = ('user1', 'user2')
        # Order by the latest activity
        ordering = ['-updated'] 

    def __str__(self):
        return f"Thread between {self.user1.username} and {self.user2.username}"


# ------------------------------------------------------------------
# 2. Message Model (Represents a single message within a thread)
# ------------------------------------------------------------------
class Message(models.Model):
    """Represents a single message sent within a ChatThread."""
    
    # Link to the conversation thread this message belongs to
    thread = models.ForeignKey(
        ChatThread, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    # The user who sent the message
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    # The actual content of the message
    content = models.TextField()
    # When the message was created
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Messages should always be retrieved in chronological order
        ordering = ['timestamp']

    def __str__(self):
        return f"Message by {self.sender.username} in Thread {self.thread.id}"