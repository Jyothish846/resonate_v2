from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        # Only need the 'content' field from the user
        fields = ['content'] 
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 1, 
                'placeholder': 'Type a message...',
                # Add a class for styling
                'class': 'chat-input-textarea'
            })
        }