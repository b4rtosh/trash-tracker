import os

from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from .models import Route, RoutePoint
from .serializers import RouteSerializer, AddressSerializer, RoutePointSerializer
from .forms import RouteForm, AddressForm
from .utils import coordinates as Coordinates, routing
import folium
import polyline
import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


OSRM_BASE_URL = os.environ.get("OSRM_BASE_URL", "http://localhost:5000")


@login_required(login_url="/")
def index(request):
    """Home page view with user's own routes"""
    routes = Route.objects.filter(user=request.user).order_by("-created_at")
    return render(
        request, "routes/index.html", {"routes": routes, "view_name": "index"}
    )


@login_required(login_url="/")
def all_routes(request):
    if not request.user.is_superuser:
        return redirect("routes:index")  # zwykły user nie ma dostępu

    routes = Route.objects.all().order_by("-created_at")
    return render(
        request, "routes/all_routes.html", {"routes": routes, "view_name": "all_routes"}
    )


@login_required(login_url="/")
def route_detail(request, route_id):
    """Display details for a specific route"""
    route = get_object_or_404(Route, pk=route_id)

    if not request.user.is_staff:
        if route.user != request.user:
            # jeśli user próbuje wejść w cudzą route -> redirect
            return redirect("/routes")  # <-- ZMIEŃ na swoją nazwę URL
    points = RoutePoint.objects.filter(route=route).order_by("sequence_number")

    needs_optimization = points.filter(sequence_number__isnull=True).exists()

    # Ensure all coordinates are float (avoid Decimal serialization issues)
    coords = [
        (float(point.longitude), float(point.latitude)) for point in points
    ]  # OSRM: lon, lat
    coords.append(
        (float(points[0].longitude), float(points[0].latitude))
    ) if coords else None

    # Default map center
    map_center = (coords[0][1], coords[0][0]) if coords else (51.107883, 17.038538)
    folium_map = folium.Map(location=map_center, zoom_start=15)

    # Collect all coordinates for fitting the map bounds
    all_locations = []

    # Add markers for each route point
    for point in points:
        popup_text = f"{point.id}. {point.address.street}, {point.address.city}"
        location = [float(point.latitude), float(point.longitude)]
        all_locations.append(location)

        if point.sequence_number == 0:
            # Special START marker
            folium.Marker(
                location=location,
                popup=f"START: {popup_text}",
                tooltip="Start Point",
                icon=folium.Icon(color="red", icon="play"),
            ).add_to(folium_map)
        else:
            # Regular marker
            folium.Marker(
                location=location,
                popup=popup_text,
                tooltip=popup_text,
                icon=folium.Icon(color="green", icon="map-marker"),
            ).add_to(folium_map)

    # Call OSRM only if 2 or more points and no optimization is needed

    if len(coords) >= 2 and not needs_optimization:
        coords_str = ";".join(f"{lon},{lat}" for lon, lat in coords)
        osrm_url = f"{OSRM_BASE_URL}/route/v1/driving/{coords_str}?overview=full"
        print(osrm_url)
        response = requests.get(osrm_url)
        if response.status_code == 200:
            osrm_data = response.json()
            geometry = osrm_data["routes"][0]["geometry"]

            route.distance = f"{round(osrm_data['routes'][0]['distance'] / 1000, 2)} km"
            route.duration = f"{round(osrm_data['routes'][0]['duration'] / 60, 2)} min"

            decoded_path = polyline.decode(geometry)  # (lat, lon)
            folium.PolyLine(
                locations=decoded_path, color="blue", weight=5, opacity=0.8
            ).add_to(folium_map)

            # Add polyline points to all_locations for fitting
            all_locations.extend(
                [[float(lat), float(lon)] for lat, lon in decoded_path]
            )

    # Adjust map to fit all points
    if all_locations:
        folium_map.fit_bounds(all_locations)

    map_html = folium_map._repr_html_()
    serialized_points = RoutePointSerializer(points, many=True).data
    return render(
        request,
        "routes/route_detail.html",
        {
            "route": route,
            "points": serialized_points,
            "map_html": map_html,
            "view_name": "route_detail",
            "needs_optimization": needs_optimization,
        },
    )


@login_required(login_url="/")
def route_create(request):
    # encoded route
    encoded_polyline = "_f}vH_q|fBLGJKBA@AFGDE@ABCPURU@AN]BGFWBEBMH[F[BK@GHi@@EDW@KVcBBMDY@IBUBSBKFc@BSFa@@IJu@Hu@Fa@Fa@T}ADQRaAJe@@E?E@CBO@KFi@Dg@Bw@@I?Q@]?C?K?Y?K?W@yA?uB?K?k@Ay@C{@Gi@Ie@EUI]EO"

    # decode paths
    decoded_points = polyline.decode(encoded_polyline)

    # Średnie współrzędne do wyśrodkowania mapy
    lat_center = sum(p[0] for p in decoded_points) / len(decoded_points)
    lon_center = sum(p[1] for p in decoded_points) / len(decoded_points)

    # create map
    folium_map = folium.Map(location=[lat_center, lon_center], zoom_start=13)
    folium.PolyLine(decoded_points, color="blue", weight=5, opacity=0.7).add_to(
        folium_map
    )

    # generate map
    map_html = folium_map._repr_html_()

    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.user = request.user
            route.save()
            return redirect("routes:route_update", route_id=route.id)
    else:
        form = RouteForm()
    return render(
        request,
        "routes/route_form.html",
        {"view_name": "route_create", "map_html": map_html, "form": form},
    )


@login_required(login_url="/")
def route_update(request, route_id):
    """Update an existing route"""
    route = get_object_or_404(Route, pk=route_id)

    # Get all route points
    route_points = RoutePoint.objects.filter(route=route).order_by("sequence_number")

    # Default center coordinates
    if route_points.exists():
        lat_center = sum(point.latitude for point in route_points) / len(route_points)
        lon_center = sum(point.longitude for point in route_points) / len(route_points)
    else:
        lat_center, lon_center = 51.107883, 17.038538  # Fallback

    # Create map centered on points or Wroclaw
    folium_map = folium.Map(
        location=[lat_center, lon_center],
        zoom_start=13 if route_points.exists() else 12,
    )

    # Add markers for each point
    for point in route_points:
        popup_text = f"{point.id}. {point.address.street}, {point.address.city}"
        folium.Marker(
            location=[point.latitude, point.longitude],
            popup=popup_text,
            tooltip=popup_text,
            icon=folium.Icon(color="green", icon="map-marker"),
        ).add_to(folium_map)

    # Optional: draw lines between points
    if route_points.count() > 1:
        coordinates = [(point.latitude, point.longitude) for point in route_points]
        # For the blue line connecting the points, uncomment the line below:
        # folium.PolyLine(coordinates, color='blue', weight=5, opacity=0.7).add_to(folium_map)

    # generate map
    map_html = folium_map._repr_html_()

    # serialize points
    points = RoutePointSerializer(route_points, many=True).data
    if request.method == "POST":
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            return redirect("routes:route_detail", route_id=route_id)
    else:
        form = RouteForm(instance=route)

    address_form = AddressForm()

    return render(
        request,
        "routes/route_form.html",
        {
            "form": form,
            "address_form": address_form,
            "route": route,
            "points": points,
            "view_name": "route_update",
            "map_html": map_html,
        },
    )


class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer

    def get_queryset(self):
        return Route.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["POST"])
def add_point(request, route_id):
    """Add a point to a route"""
    try:
        route = get_object_or_404(Route, pk=route_id, user=request.user)
        address_data = {
            "street": request.data.get("street", ""),
            "city": request.data.get("city", ""),
            "state": request.data.get("state", ""),
            "postal_code": request.data.get("postal_code", ""),
            "country": request.data.get("country", ""),
        }

        address_serializer = AddressSerializer(data=address_data)
        if not address_serializer.is_valid():
            return Response(
                address_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        address = address_serializer.save()

        # get coordinates
        coordinates = Coordinates.get_coordinates(address.city, address.street)
        if not coordinates:
            address.delete()
            # check if it should be code 400
            return Response(
                {"error": "Could not geocode address"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_first = not RoutePoint.objects.filter(route_id=route.id).exists()
        point_data = {
            "route": route.id,
            "address": address.id,
            # add the actual geocoding with these two properties
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "sequence_number": 0 if is_first else None,
        }

        point_serializer = RoutePointSerializer(data=point_data)
        if not point_serializer.is_valid():
            address.delete()
            return Response(point_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        point_serializer.save()
        return Response(point_serializer.data, status=status.HTTP_201_CREATED)
    except Exception as ex:
        print(ex)


@api_view(["DELETE"])
def remove_point(request, point_id):
    """Remove the point from the route"""
    point = get_object_or_404(RoutePoint, pk=point_id)
    route_id = point.route.id

    # check if start
    is_start_point = point.sequence_number == 0

    address = point.address
    point.delete()
    address.delete()

    points = RoutePoint.objects.filter(route_id=route_id).order_by("sequence_number")

    if is_start_point and points.exists():
        for point in points:
            point.sequence_number = None
            point.save()

    return Response(
        {
            "success": True,
            "start_removed": is_start_point,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
def remove_route(request, route_id):
    # remove whole route
    route = get_object_or_404(Route, pk=route_id)
    route.delete()

    return Response({"success": True}, status=status.HTTP_200_OK)


@api_view(["GET"])
def optimize_route(request, route_id):
    try:
        dist = routing.optimize_points(route_id)
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return redirect("routes:route_detail", route_id=route_id)


@api_view(["PUT"])
def set_start_point(reqeust, route_id, point_id):
    route = get_object_or_404(Route, pk=route_id)
    new_start_point = get_object_or_404(RoutePoint, pk=point_id)

    new_start_point.sequence_number = 0
    new_start_point.save()

    return Response(
        {"success": True, "message": "New starting point set successfully"},
        status=status.HTTP_200_OK,
    )


@staff_member_required
def admin_routes(request):
    routes = Route.objects.select_related("user").order_by("-created_at")
    return render(request, "routes/admin_routes.html", {"routes": routes})


# OSRM_BASE_URL = "http://localhost:5000"


def osrm_demo_view(request):
    """
    Public demo – OSRM route from up to 3 points.
    Does NOT use DB. Only calculates & returns map HTML.
    """
    try:
        points = request.GET.getlist("points[]")  # expected: ["lat,lon", "lat,lon"]
        if len(points) < 2:
            return JsonResponse({"error": "Need at least 2 points"}, status=400)
        if len(points) > 3:
            return JsonResponse({"error": "Max 3 points allowed"}, status=400)

        # Convert to float tuples
        coords = [tuple(map(float, p.split(","))) for p in points]

        # OSRM wants lon,lat
        osrm_coords = ";".join([f"{lon},{lat}" for lat, lon in coords])

        url = f"{OSRM_BASE_URL}/route/v1/driving/{osrm_coords}?overview=full"
        r = requests.get(url)
        if r.status_code != 200:
            return JsonResponse({"error": "OSRM error"}, status=500)

        data = r.json()
        geometry = data["routes"][0]["geometry"]

        # folium map
        folium_map = folium.Map(location=coords[0], zoom_start=14)
        for i, (lat, lon) in enumerate(coords):
            folium.Marker(
                location=(lat, lon),
                popup=f"Point {i + 1}",
                icon=folium.Icon(color="green"),
            ).add_to(folium_map)

        decoded = polyline.decode(geometry)
        folium.PolyLine(decoded, color="blue", weight=5).add_to(folium_map)

        map_html = folium_map._repr_html_()

        return JsonResponse(
            {
                "map": map_html,
                "distance": round(data["routes"][0]["distance"] / 1000, 2),
                "duration": round(data["routes"][0]["duration"] / 60, 2),
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
