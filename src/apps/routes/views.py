from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Route
# from .forms import RouteForm

def index(request):
    """Home page view"""
    return render(request, 'routes/index.html', {
        'view_name': 'index'
    })

def route_detail(request, route_id):
    """Display details for a specific route"""
    # route = get_object_or_404(Route, pk=route_id)
    return render(request, 'routes/route_detail.html', {
        # 'route': route,
        'view_name': 'route_detail'
    })

def route_create(request):
    """Create a new route"""
    # if request.method == 'POST':
    #     form = RouteForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('routes:route_list')
    # else:
    #     form = RouteForm()
    
    return render(request, 'routes/route_form.html', {
        # 'form': form,
        'view_name': 'route_create'
    })

def route_update(request, route_id):
    """Update an existing route"""
    # route = get_object_or_404(Route, pk=route_id)
    
    # if request.method == 'POST':
    #     form = RouteForm(request.POST, instance=route)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('routes:route_detail', route_id=route_id)
    # else:
    #     form = RouteForm(instance=route)
    
    return render(request, 'routes/route_form.html', {
        # 'form': form,
        # 'route': route,
        'view_name': 'route_update'
    })

def route_delete(request, route_id):
    """Delete a route"""
    # route = get_object_or_404(Route, pk=route_id)
    
    # if request.method == 'POST':
    #     route.delete()
    #     return redirect('routes:route_list')
    
    return render(request, 'routes/route_delete.html', {
        # 'route': route,
        'view_name': 'route_delete'
    })