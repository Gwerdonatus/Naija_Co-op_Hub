from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message
from marketplace.models import Product
from django.contrib.auth.models import User
from .forms import MessageForm

@login_required
def chat_box(request, product_id=None, receiver_id=None):
    """Display chat messages and handle message sending (text, images, voice)."""
    receiver = get_object_or_404(User, id=receiver_id)
    product = get_object_or_404(Product, id=product_id) if product_id else None

    # Fetch messages between the sender and receiver
    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user))
    ).order_by('timestamp')

    if product:
        messages = messages.filter(product=product)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.product = product
            message.save()
            return redirect('chat:chat_box', product_id=product.id if product else '', receiver_id=receiver.id)
    else:
        form = MessageForm()

    return render(request, 'chat/chat_box.html', {
        'product': product,
        'receiver': receiver,
        'messages': messages,
        'form': form
    })


@login_required
def inbox(request):
    """Show the latest messages from each chat conversation."""
    user = request.user
    latest_messages = {}

    messages = Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-timestamp')

    for msg in messages:
        chat_user = msg.sender if msg.receiver == user else msg.receiver
        if chat_user not in latest_messages:
            latest_messages[chat_user] = msg  # Store only the latest message per user

    return render(request, 'chat/inbox.html', {'conversations': latest_messages})


@login_required
def chat_detail(request, username):
    """Show full chat with a specific user."""
    user = request.user
    receiver = get_object_or_404(User, username=username)

    messages = Message.objects.filter(
        Q(sender=user, receiver=receiver) | Q(sender=receiver, receiver=user)
    ).order_by('timestamp')

    # Mark messages as read
    messages.filter(receiver=user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            return redirect('chat:chat_detail', username=username)
    else:
        form = MessageForm()

    return render(request, 'chat/chat_detail.html', {
        'messages': messages,
        'receiver': receiver,
        'form': form
    })


@login_required
def send_message(request, username):
    """Send a message to a user, supporting text, images, and voice notes."""
    receiver = get_object_or_404(User, username=username)
    if request.method == "POST":
        form = MessageForm(request.POST, request.FILES)
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id) if product_id else None

        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.product = product
            message.save()
        return redirect('chat:chat_detail', username=username)
    else:
        # For GET requests, redirect to the chat detail view.
        return redirect('chat:chat_detail', username=username)
