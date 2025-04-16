from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Route, Address, RoutePoint
from .forms import RouteForm, AddressForm
import json
import requests


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
    points = RoutePoint.objects.filter(route=route).order_by('sequence_number')
    return render(request, 'routes/route_detail.html', {
        'route': route,
        'points': points,
        'view_name': 'route_detail'
    })


def route_create(request):
    """Create a new route"""
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            return redirect('routes:route_update', route_id=route.id)
    else:
        form = RouteForm()
    return render(request, 'routes/route_form.html', {
        'view_name' : 'route_create',
        'form': form
    }) 
        
    
def route_update(request, route_id):
    """Update an existing route"""
    route = get_object_or_404(Route, pk=route_id)
    points = RoutePoint.objects.filter(route=route).order_by('sequence_number')
    
    if request.method == 'POST':
        form = RouteForm(request.POST, intstance=route)
        if form.is_valid():
            form.save()
            return redirect('routes:route_detail', route_id=route_id)
    else:
        form = RouteForm(instance=Route)
    
    address_form = AddressForm()

    return render(request, 'routes/route_form.html', {
        'form': form,
        'address_form': address_form,
        'route': route,
        'points': points,
        'view_name': 'route_update' 
    })


@require_http_methods(['POST'])
def add_point(request, route_id):
    """Add a point to a route"""
    route = get_object_or_404(Route, pk=route_id)
    data = json.loads(request.body)

    address = Address.objects.create(
        street = data.get('street', ''),
        city = data.get('city', ''),
        state = data.get('city', ''),
        state = data.get('state', ''),
        posta_code = data.get('postal_code', ''),
        country = data.get('country', '')
    )

    coordinates = coordinates

    if not coordinates:
        address.delete()
        # check if it should be code 400
        return JsonResponse({'error': 'Could not geocode address'}, status=400)
    
    sequence = RoutePoint.objects.filter(route=route).count()

    point = RoutePoint.objects.create(
        route = route,
        address = address,
        # add the actual geocoding with these two properties
        latitude = coordinates.latitude,
        longitude = coordinates.longitude,
        sequence_number = sequence
    )

    return JsonResponse({
        'id': point.id,
        'address_id': address.id,
        'latitude': point.latitude,
        'longitude': point.longitude,
        'sequence_number': point.sequence_number,
        # wtf do I return address_text
        'address_text': f"{address.street}, {address.city}"
    })

def route_delete(request, route_id):
    """Delete a route"""
    route = get_object_or_404(Route, pk=route_id)

    if request.method == 'POST':
        route.delete()
        return redirect('routes:index')
    
    return render(request, 'routes/route_delete.html', {
        'route': route,
        'view_name': 'route_delete'
    })

@require_http_methods(["POST"])
def remove_point(request, point_id):
    """Remove the point from the route"""
    point = get_object_or_404(RoutePoint, pk=point_id)
    route_id = point.route.id

    address = point.address
    point.delete()
    address.delete()

    points = RoutePoint.objects.filter(route_id=route_id).order_by('sequence_number')
    for i, point in enumerate(points):
        point.sequence_number = i
        point.save()

    return JsonResponse({'success': True})