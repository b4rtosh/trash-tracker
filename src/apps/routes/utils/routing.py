from django.shortcuts import get_object_or_404
from ..models import Route, RoutePoint
import requests
import logging
from . import held_karp


def request_distance(latitude1, longitude1, latitude2, longitude2):
    url = f"http://127.0.0.1:5000/route/v1/driving/{longitude1},{latitude1};{longitude2},{latitude2}?steps=false"
    try:
        response = requests.get(url)

        response.raise_for_status()

        data = response.json()
        if (data and isinstance(data.get("routes"), list) and len(data["routes"]) > 0 and
                isinstance(data["routes"][0], dict) and "distance" in data["routes"][0]):
            return data["routes"][0]["distance"]
        else:
            logging.warning(
                f"JSON response from {url} did not have the expected structure or 'distance' key. Response: {data}")
            return None  # Indicate that distance could not be found

    except requests.exceptions.HTTPError as http_err:
        logging.error(
            f"HTTP error occurred for {url}: {http_err} - Response: {response.text if 'api_response' in locals() else 'N/A'}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error for {url}: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error for {url}: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:  # Catch other request-related errors
        logging.error(f"Request failed for {url}: {req_err}")
        return None
    except ValueError as json_decode_err:  # Handles errors from response.json() if response is not valid JSON
        logging.error(f"JSON decoding failed for {url}: {json_decode_err}")
        return None
    except (KeyError, IndexError, TypeError) as data_access_err:  # Handles errors if structure is not as expected
        logging.error(f"Error accessing data in JSON response for {url}: {data_access_err}")
        return None
    except Exception as ex:  # A general fallback for other unexpected errors
        # Log the exception and return None
        logging.error(f"An unexpected error occurred while fetching distance from {url}: {ex}")
        return None


def create_list(route_points):
    matrix_of_points = dict()

    for i in range(len(route_points)):
        list_of_distances = []
        for j in range(len(route_points)):
            if i == j:
                list_of_distances.append(0)
            elif route_points[j].id in matrix_of_points:
                list_of_distances.append(matrix_of_points[route_points[j].id][i])
            else:
                distance = None
                try:
                    distance = request_distance(route_points[i].latitude, route_points[i].longitude,
                                                route_points[j].latitude, route_points[j].longitude)
                    if distance is None:
                        logging.warning(
                            f"Could not retrieve distance between point {route_points[i].id} ({route_points[i].latitude}, {route_points[i].longitude}) and point {route_points[j].id} ({route_points[j].latitude}, {route_points[j].longitude})")
                except Exception as e:
                    logging.error(
                        f"Unexpected error calling request_distance for points {route_points[i].id} and {route_points[j].id}: {e}")
                    distance = None  # Ensure distance is None if an unexpected error occurs here

                list_of_distances.append(distance)
        matrix_of_points[route_points[i].id] = list_of_distances
    print(matrix_of_points)
    return matrix_of_points


def optimize_points(route_id):
    route = get_object_or_404(Route, pk=route_id)
    all_route_points = (RoutePoint.objects.filter(route=route).only("id", "sequence_number", "latitude", "longitude")
                    .order_by('sequence_number'))
    # return if all sequence numbers are present
    if not all_route_points.filter(sequence_number__isnull=True).exists():
        return

    start_point = None
    other_points = []

    for point in all_route_points:
        if point.sequence_number == 0:
            start_point = point
        else:
            other_points.append(point)

    # Put the start point first in the ordered list
    ordered_points = []
    if start_point:
        ordered_points.append(start_point)
    ordered_points.extend(other_points)

    route_points_dist = {rp.id: rp for rp in ordered_points}
    distance_matrix_dict = create_list(ordered_points)
    dist, order = held_karp.held_karp(distance_matrix_dict)
    print(order)

    for index, point_id in enumerate(order):
        if point_id in route_points_dist:
            route_point = route_points_dist[point_id]
            route_point.sequence_number = index
            route_point.save()  # save to db
    return dist



