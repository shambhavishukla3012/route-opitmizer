import requests
import itertools
from typing import List, Dict, Tuple
from flask import current_app
import logging
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in kilometers"""
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def get_coordinates(address: str) -> Tuple[float, float]:
    """Convert address to coordinates using OpenRouteService Geocoding API"""
    api_key = current_app.config["ORS_API_KEY"]
    if not api_key:
        logging.error("OpenRouteService API key is missing")
        raise ValueError("API key is not configured")

    url = "https://api.openrouteservice.org/geocode/search"

    try:
        response = requests.get(
            url,
            headers={"Authorization": api_key},
            params={"text": address, "size": 1}
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("features"):
            raise ValueError(f"Address not found: {address}")

        # OpenRouteService returns [lon, lat]
        coordinates = data["features"][0]["geometry"]["coordinates"]
        logging.debug(f"Geocoded {address} to coordinates: {coordinates}")
        # Return as (lat, lon) for consistency with other functions
        return (coordinates[1], coordinates[0])

    except requests.exceptions.RequestException as e:
        logging.error(f"Geocoding API error for address '{address}': {str(e)}")
        if hasattr(response, 'status_code'):
            if response.status_code == 401:
                raise ValueError("Invalid API key")
            elif response.status_code == 429:
                raise ValueError("API rate limit exceeded")
        raise ValueError(f"Error geocoding address: {str(e)}")

def get_route(coordinates: List[Tuple[float, float]]) -> Dict:
    """Get optimized route using OpenRouteService Directions API"""
    api_key = current_app.config["ORS_API_KEY"]
    if not api_key:
        logging.error("OpenRouteService API key is missing")
        raise ValueError("API key is not configured")

    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"

    # Convert from (lat, lon) to [lon, lat] for API
    coords = [[lon, lat] for lat, lon in coordinates]
    logging.debug(f"Sending coordinates to routing API: {coords}")

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json"
            },
            json={
                "coordinates": coords,
                "instructions": True,
                "units": "m"
            }
        )
        response.raise_for_status()
        route_data = response.json()
        logging.debug("Successfully received route data from API")
        return route_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Routing API error: {str(e)}")
        if hasattr(response, 'status_code'):
            if response.status_code == 401:
                raise ValueError("Invalid API key")
            elif response.status_code == 429:
                raise ValueError("API rate limit exceeded")
            elif response.status_code == 400:
                raise ValueError("Invalid coordinates or route not possible")
        raise ValueError(f"Error calculating route: {str(e)}")

def optimize_route(coordinates: List[Tuple[float, float]]) -> List[int]:
    """Optimize route using brute force for small sets of coordinates"""
    if len(coordinates) <= 2:
        return list(range(len(coordinates)))

    if len(coordinates) > 10:
        raise ValueError("Maximum 10 locations allowed")

    # Keep start point fixed
    start = coordinates[0]
    waypoints = coordinates[1:]

    def calculate_total_distance(order):
        """Calculate total distance for a given order of waypoints"""
        total = 0
        # Start from the first location (fixed)
        prev_lat, prev_lon = start

        # Add distances between consecutive points in the route
        for i in order:
            curr_lat, curr_lon = waypoints[i]
            total += haversine_distance(prev_lat, prev_lon, curr_lat, curr_lon)
            prev_lat, prev_lon = curr_lat, curr_lon

        return total

    # Try all possible permutations of waypoints
    best_order = None
    best_distance = float('inf')
    for perm in itertools.permutations(range(len(waypoints))):
        distance = calculate_total_distance(perm)
        if distance < best_distance:
            best_distance = distance
            best_order = perm

    logging.debug(f"Best route order found: [0, {', '.join(str(i+1) for i in best_order)}]")
    return [0] + [i+1 for i in best_order]  # Add start point (0) back to beginning