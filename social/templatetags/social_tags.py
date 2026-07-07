from django import template
from social.models import Follow, Like

register = template.Library()


@register.filter
def is_liked_by(post, user):
    """Check if a post is liked by a user."""
    if not user or not user.is_authenticated:
        return False
    return Like.objects.filter(post=post, user=user).exists()


@register.filter
def is_following(current_user, target_user):
    """Check if current_user follows target_user."""
    if not current_user or not current_user.is_authenticated:
        return False
    return Follow.objects.filter(follower=current_user, following=target_user).exists()
