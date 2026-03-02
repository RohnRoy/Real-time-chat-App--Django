from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.models import User
from .models import Message


@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "chat/user_list.html", {"users": users})


@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user],
    ).order_by("timestamp")

    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False,
    ).update(is_read=True)

    return render(
        request,
        "chat/chat.html",
        {"other_user": other_user, "messages": messages},
    )