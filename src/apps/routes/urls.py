from django.urls import path, include
from . import views

app_name = 'routes'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:route_id>/', views.route_detail, name='route_detail'),
    path('create/', views.route_create, name='route_create'),
    path('<int:route_id>/update/', views.route_update, name='route_update'),
    path('distances', views.test_distances, name='test_distances')

]