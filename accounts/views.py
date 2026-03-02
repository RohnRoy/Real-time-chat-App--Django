from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.utils import timezone
from .forms import RegisterForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_online = True
            user.last_seen = None
            user.save(update_fields=["is_online", "last_seen"])
            login(request, user)
            return redirect("user_list")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


class UserLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        user = form.get_user()
        response = super().form_valid(form)
        user.is_online = True
        user.last_seen = None
        user.save(update_fields=["is_online", "last_seen"])
        return response


class UserLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            request.user.is_online = False
            request.user.last_seen = timezone.now()
            request.user.save(update_fields=["is_online", "last_seen"])
        return super().post(request, *args, **kwargs)
