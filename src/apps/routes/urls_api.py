from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'routes'

router = DefaultRouter()
router.register(r'routes', views.RouteViewSet, basename='route')

urlpatterns = [
    # api endpoints for dynamic resource managing
    path('', include(router.urls)),
    path('routes/<int:route_id>/points', views.add_point, name='add_point'),
    path('points/<int:point_id>', views.remove_point, name='remove_point'),
    path('routes/<int:route_id>', views.remove_route, name='remove_route'),
    path('routes/<int:route_id>/optimize', views.optimize_route, name='optimize_points'),
    path('routes/<int:route_id>/points/<int:point_id>/set-start/', views.set_start_point, name='set_start_point'),
]
