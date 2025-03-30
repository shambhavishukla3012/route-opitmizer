// Handle form submission
document.getElementById('routeForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const inputs = document.querySelectorAll('.location-input');
    const addresses = Array.from(inputs).map(input => input.value.trim()).filter(val => val);

    if (addresses.length < 2) {
        showError('Please enter at least 2 locations');
        return;
    }

    if (addresses.length > 10) {
        showError('Maximum 10 locations allowed');
        return;
    }

    showLoading(true);
    hideError();

    try {
        const response = await fetch('/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ addresses })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to optimize route');
        }

        // Update map
        addMarkers(data.coordinates, data.addresses);
        drawRoute(data.route);

        // Update results
        showResults(data);

    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
});

// Add new location input field
function addLocationField() {
    const locations = document.getElementById('locations');
    const inputs = locations.querySelectorAll('.location-input');

    if (inputs.length >= 10) {
        showError('Maximum 10 locations allowed');
        return;
    }

    const div = document.createElement('div');
    div.className = 'mb-3';
    div.innerHTML = `
        <div class="input-group">
            <input type="text" class="form-control location-input" required>
            <button type="button" class="btn btn-danger" onclick="removeLocationField(this)">
                Remove
            </button>
        </div>
    `;

    locations.appendChild(div);
}

// Remove location input field
function removeLocationField(button) {
    button.closest('.mb-3').remove();
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('d-none');
}

// Hide error message
function hideError() {
    const errorDiv = document.getElementById('error');
    errorDiv.classList.add('d-none');
}

// Show/hide loading state
function showLoading(loading) {
    const submitBtn = document.querySelector('button[type="submit"]');
    submitBtn.disabled = loading;
    submitBtn.innerHTML = loading ? 
        '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...' :
        'Optimize Route';
}

// Display results
function showResults(data) {
    const results = document.getElementById('results');
    const directions = document.getElementById('directions');

    // Extract route details from GeoJSON response
    const route = data.route.features[0].properties;

    // Show optimized location sequence
    const locationSequence = document.getElementById('locationSequence');
    locationSequence.innerHTML = data.addresses
        .map((address, index) => `
            <li class="location-sequence-item">
                <div class="sequence-number">${index + 1}</div>
                <div class="location-address">${address}</div>
            </li>
        `)
        .join('');

    // Show total distance and duration
    document.getElementById('totalDistance').textContent = 
        `${(route.summary.distance / 1000).toFixed(2)} km`;
    document.getElementById('totalDuration').textContent = 
        `${Math.round(route.summary.duration / 60)} minutes`;

    // Show turn-by-turn directions
    directions.innerHTML = route.segments
        .flatMap(segment => segment.steps)
        .map(step => `
            <div class="direction-step">
                <span class="instruction">${step.instruction}</span>
                <span class="distance">${(step.distance / 1000).toFixed(2)} km</span>
            </div>
        `)
        .join('');

    results.classList.remove('d-none');
}