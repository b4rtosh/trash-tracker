from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.route_create, name='route_create'),
    path('<int:route_id>/', views.route_detail, name='route_detail'),
    path('update/<int:route_id>/', views.route_update, name='route_update'),
    path('delete/<int:route_id>/', views.route_delete, name='route_delete'),
]