from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    else:
        notifications = Notification.objects.none()  # returns an empty QuerySet
    
    return {
        'notification_count': notifications.count()
    }

