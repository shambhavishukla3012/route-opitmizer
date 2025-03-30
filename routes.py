from flask import render_template, request, jsonify
from app import app, db
from models import Location, Route, RouteLocation
from utils import get_coordinates, get_route, optimize_route
import logging

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        logging.debug(f"Received optimization request with data: {data}")

        if not data or 'addresses' not in data:
            logging.error("Invalid request: missing addresses")
            return jsonify({'error': 'Please provide addresses'}), 400

        addresses = data['addresses']
        if not addresses or len(addresses) < 2:
            logging.error("Invalid request: insufficient addresses")
            return jsonify({'error': 'Please provide at least 2 addresses'}), 400

        if len(addresses) > 10:
            logging.error("Invalid request: too many addresses")
            return jsonify({'error': 'Maximum 10 locations allowed'}), 400

        # Get coordinates for all addresses
        coordinates = []
        locations = []
        for address in addresses:
            try:
                logging.debug(f"Geocoding address: {address}")
                lat, lon = get_coordinates(address)
                coordinates.append((lat, lon))
                location = Location(
                    address=address,
                    latitude=lat,
                    longitude=lon
                )
                locations.append(location)
                db.session.add(location)
            except ValueError as e:
                logging.error(f"Geocoding error: {str(e)}")
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                logging.error(f"Unexpected error during geocoding: {str(e)}")
                return jsonify({'error': 'Error processing address'}), 500

        try:
            # Optimize route
            logging.debug(f"Optimizing route for coordinates: {coordinates}")
            optimized_indices = optimize_route(coordinates)
            optimized_coordinates = [coordinates[i] for i in optimized_indices]

            # Get detailed route
            logging.debug("Fetching detailed route")
            route_data = get_route(optimized_coordinates)

            # Extract route summary from GeoJSON response
            properties = route_data['features'][0]['properties']
            summary = properties['summary']

            # Create route record
            route = Route(
                total_distance=float(summary['distance']),
                total_duration=float(summary['duration'])
            )
            db.session.add(route)

            # Create route locations with proper sequence
            for idx, i in enumerate(optimized_indices):
                route_location = RouteLocation(
                    route=route,
                    location=locations[i],
                    sequence=idx
                )
                db.session.add(route_location)

            db.session.commit()
            logging.debug("Successfully saved route to database")

            return jsonify({
                'route': route_data,
                'coordinates': optimized_coordinates,
                'addresses': [addresses[i] for i in optimized_indices]
            })

        except ValueError as e:
            db.session.rollback()
            logging.error(f"Route optimization error: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error during route optimization: {str(e)}")
            return jsonify({'error': 'Error calculating route'}), 500

    except Exception as e:
        if db.session.is_active:
            db.session.rollback()
        logging.error(f"Unhandled error in optimize endpoint: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500