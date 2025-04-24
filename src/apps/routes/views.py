from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Route
import folium
import polyline
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

def map_view(request):
    # Zakodowana trasa
    encoded_polyline = "_f}vH_q|fBLGJKBA@AFGDE@ABCPURU@AN]BGFWBEBMH[F[BK@GHi@@EDW@KVcBBMDY@IBUBSBKFc@BSFa@@IJu@Hu@Fa@Fa@T}ADQRaAJe@@E?E@CBO@KFi@Dg@Bw@@I?Q@]?C?K?Y?K?W@yA?uB?K?k@Ay@C{@Gi@Ie@EUI]EO"

    # Dekodowanie trasy
    decoded_points = polyline.decode(encoded_polyline)

    # Średnie współrzędne do wyśrodkowania mapy
    lat_center = sum(p[0] for p in decoded_points) / len(decoded_points)
    lon_center = sum(p[1] for p in decoded_points) / len(decoded_points)

    # Tworzenie mapy
    folium_map = folium.Map(location=[lat_center, lon_center], zoom_start=13)
    folium.PolyLine(decoded_points, color='blue', weight=5, opacity=0.7).add_to(folium_map)

    # Generowanie HTML
    map_html = folium_map._repr_html_()
    print(map_html)
    return render(request, 'routes/route_form.html', {'map_html': map_html})
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