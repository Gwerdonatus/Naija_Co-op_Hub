from chat.models import Message

def unread_messages(request):
    """Make unread message count available globally."""
    if request.user.is_authenticated:
        return {'unread_count': Message.objects.filter(receiver=request.user, is_read=False).count()}
    return {}
