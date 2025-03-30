# Route Optimizer
A Flask-based web application that helps users plan and visualize efficient travel routes with interactive mapping capabilities.
Enter list of locations and it will return the optimized path and best way to go to each location to minimize drive time.

## Features
- Interactive map visualization using Leaflet.js
- Address geocoding and route optimization
- Turn-by-turn directions
- Distance and duration calculations
- Responsive design with light/dark theme
- PostgreSQL database for route history

## Prerequisites
1. Python 3.11+
2. PostgreSQL database
3. OpenRouteService API key (Get it from [OpenRouteService](https://openrouteservice.org/dev/#/signup))

## Local Development Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd route-optimizer
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
# On macOS/Linux
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install flask flask-sqlalchemy psycopg2-binary python-dotenv requests gunicorn email-validator
```

4. Set up PostgreSQL:
- Install PostgreSQL on your system if not already installed
- Create a new database:
```sql
CREATE DATABASE route_optimizer;
```

5. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/route_optimizer
ORS_API_KEY=your_openrouteservice_api_key
SESSION_SECRET=your_secret_key
```

Replace:
- `<user>` with your PostgreSQL username
- `<password>` with your PostgreSQL password
- `your_openrouteservice_api_key` with your OpenRouteService API key
- `your_secret_key` with a random string for session security

6. Initialize the database:
```bash
# Start Python shell 
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

## Running the Application

1. Start the Flask development server:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

The application will be running with:
- Debug mode enabled
- Auto-reload on code changes
- Database connection pooling configured
- API request logging enabled

## Usage

1. Enter locations in the input fields (minimum 2, maximum 10 locations)
2. Click "Add Location" to add more stops
3. Click "Optimize Route" to generate the optimal route
4. View the route on the map and check turn-by-turn directions
5. Toggle between light and dark themes using the theme switcher

## Project Structure

```
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── form.js
│       └── map.js
├── templates/
│   ├── base.html
│   └── index.html
├── app.py
├── main.py
├── models.py
├── routes.py
└── utils.py
```

## API Integration

This application uses the OpenRouteService API for:
- Geocoding addresses to coordinates
- Calculating optimal routes
- Generating turn-by-turn directions

## Database Schema

The application uses PostgreSQL with the following schema:

- `locations`: Stores address and coordinate information
  - `id`: Primary key
  - `address`: Location address
  - `latitude`: Geographical latitude
  - `longitude`: Geographical longitude
  - `created_at`: Timestamp

- `routes`: Stores route summary information
  - `id`: Primary key
  - `total_distance`: Route distance in meters
  - `total_duration`: Route duration in seconds
  - `created_at`: Timestamp

- `route_locations`: Links routes and locations with sequence order
  - `route_id`: Foreign key to routes
  - `location_id`: Foreign key to locations
  - `sequence`: Order in the route

## Common Issues

1. Database Connection:
   - Ensure PostgreSQL is running
   - Check database credentials in .env file
   - Verify database exists and is accessible

2. API Key:
   - Make sure your OpenRouteService API key is valid
   - Check daily API usage limits
   - Verify the key has proper permissions

3. Address Input:
   - Use complete addresses for better geocoding results
   - Include city and country for more accurate results

## Development Notes

- The application uses Flask's development server by default
- Debug mode is enabled for development
- PostgreSQL connection pooling is configured for better performance
- API requests are logged for debugging purposes
