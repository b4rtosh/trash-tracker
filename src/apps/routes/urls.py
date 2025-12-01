from django.urls import path
from . import views

app_name = "routes"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:route_id>/", views.route_detail, name="route_detail"),
    path("create/", views.route_create, name="route_create"),
    path("<int:route_id>/update/", views.route_update, name="route_update"),
    path("admin/", views.admin_routes, name="admin_routes"),
    path("all/", views.all_routes, name="all_routes"),
    path("demo/osrm/", views.osrm_demo_view, name="osrm_demo"),
]
