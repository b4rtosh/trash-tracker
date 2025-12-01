from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth.views import LoginView


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("routes:index")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


class MyLoginView(LoginView):
    template_name = "registration/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/routes/")
        return super().dispatch(request, *args, **kwargs)
