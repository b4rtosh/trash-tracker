from django.shortcuts import get_object_or_404
from ..models import Route, RoutePoint, RouteSegment
import requests
import random


def request_distance(latitude1, longitude1, latitude2, longitude2):
    rn = random
    return rn.randint(1, 10)


def create_list(route_id):
    route = get_object_or_404(Route, pk=route_id)
    route_points = (RoutePoint.objects.filter(route=route).only("id", "sequence_number", "latitude", "longitude")
                    .order_by('sequence_number'))

    matrix_of_points = dict()

    for i in range(len(route_points)):
        list_of_distances = []
        for j in range(len(route_points)):
            if i == j:
                list_of_distances.append(0)
            elif route_points[j].id in matrix_of_points:
                list_of_distances.append(matrix_of_points[route_points[j].id][i])
            else:
                distance = request_distance(route_points[i].latitude, route_points[i].longitude,
                                            route_points[j].latitude, route_points[j].longitude)
                list_of_distances.append(distance)
        matrix_of_points[route_points[i].id] = list_of_distances
    print(matrix_of_points)
    return matrix_of_points



