from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from .models import Route, Address, RoutePoint
from .serializers import RouteSerializer, AddressSerializer, RoutePointSerializer
from .forms import RouteForm, AddressForm
from .utils import coordinates as Coordinates, routing
import folium
import polyline


def index(request):
    """Home page view with all routes"""
    routes = Route.objects.all().order_by('-created_at')
    return render(request, 'routes/index.html', {
        'routes': routes,
        'view_name': 'index'
    })


def route_detail(request, route_id):
    """Display details for a specific route"""
    route = get_object_or_404(Route, pk=route_id)
    route_points = RoutePoint.objects.filter(route=route).order_by('sequence_number')
    # serialize points
    points = RoutePointSerializer(route_points, many=True).data
    return render(request, 'routes/route_detail.html', {
        'route': route,
        'points': points,
        'view_name': 'route_detail'
    })


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
    folium.PolyLine(decoded_points, color='blue', weight=5, opacity=0.7).add_to(folium_map)

    # generate map
    map_html = folium_map._repr_html_()

    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            return redirect('routes:route_update', route_id=route.id)
    else:
        form = RouteForm()
    return render(request, 'routes/route_form.html', {
        'view_name': 'route_create',
        'map_html': map_html,
        'form': form
    })


def route_update(request, route_id):
    """Update an existing route"""
    route = get_object_or_404(Route, pk=route_id)
    route_points = RoutePoint.objects.filter(route=route).order_by('sequence_number')

    # serialize points
    points = RoutePointSerializer(route_points, many=True).data

    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            return redirect('routes:route_detail', route_id=route_id)
    else:
        form = RouteForm(instance=route)

    address_form = AddressForm()

    return render(request, 'routes/route_form.html', {
        'form': form,
        'address_form': address_form,
        'route': route,
        'points': points,
        'view_name': 'route_update'
    })


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().order_by('-created_at')
    serializer_class = RouteSerializer


@api_view(['POST'])
def add_point(request, route_id):
    """Add a point to a route"""
    route = get_object_or_404(Route, pk=route_id)
    address_data = {
        'street': request.data.get('street', ''),
        'city': request.data.get('city', ''),
        'state': request.data.get('state', ''),
        'postal_code': request.data.get('postal_code', ''),
        'country': request.data.get('country', '')
    }

    address_serializer = AddressSerializer(data=address_data)
    if not address_serializer.is_valid():
        return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    address = address_serializer.save()

    # get coordinates
    coordinates = Coordinates.get_coordinates(address.city, address.street)
    if not coordinates:
        address.delete()
        # check if it should be code 400
        return Response({'error': 'Could not geocode address'}, status=status.HTTP_400_BAD_REQUEST)

    # create route point
    point_count = RoutePoint.objects.filter(route=route_id).count()
    sequence = 0 if point_count == 0 else None

    point_data = {
        'route': route.id,
        'address': address.id,
        # add the actual geocoding with these two properties
        'latitude': coordinates['latitude'],
        'longitude': coordinates['longitude'],
        'sequence_number': sequence
    }

    point_serializer = RoutePointSerializer(data=point_data)
    if not point_serializer.is_valid():
        address.delete()
        return Response(point_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    point_serializer.save()
    return Response(point_serializer.data, status=status.HTTP_201_CREATED)


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

    points = RoutePoint.objects.filter(route_id=route_id).order_by('sequence_number')

    if is_start_point and points.exists():
        for point in points:
            point.sequence_number = None
            point.save()

    return Response({
        'success': True,
        'start_removed': True,
    }, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def remove_route(request, route_id):
    # remove whole route
    route = get_object_or_404(Route, pk=route_id)
    route.delete()

    return Response({'success': True}, status=status.HTTP_200_OK)

@api_view(["GET"])
def optimize_route(request, route_id):
    routing.optimize_points(route_id)
    

    return redirect('routes:index')