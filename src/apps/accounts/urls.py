from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import MyLoginView

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]