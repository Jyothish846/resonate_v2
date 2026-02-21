from django import template
from accounts.models import Follow

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def is_following(user, target_user):
    """Return True if the user follows the target_user."""
    if not user.is_authenticated:
        return False
    return Follow.objects.filter(follower=user, following=target_user).exists()