document.addEventListener('DOMContentLoaded', function() {
    // Add point button handler
    document.getElementById('addPointBtn').addEventListener('click', function () {
        const form = document.getElementById('pointForm');
        const formData = new FormData(form);

        fetch('/api/routes/{{ route.id }}/points', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                street: formData.get('street'),
                post_code: formData.get('postal_code'),
                city: formData.get('city'),
                state: formData.get('state'),
                country: formData.get('country'),
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove empty row if exists
            const noPointsRow = document.getElementById('no-points-row');
            if (noPointsRow) {
                noPointsRow.remove();
            }

            // Add new point to the table
            const tbody = document.getElementById('pointsTable');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${data.sequence_number}</td>
                <td>${data.address_text}</td>
                <td>${data.latitude}</td>
                <td>${data.longitude}</td>
                <td>
                    <button type="button" class="btn delete-point" data-point-id="${data.id}">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);

            // Dynamically update the map with new point
            const map = {{ map_html|safe }}; // Assume you are passing the map to the page
            const marker = L.marker([data.latitude, data.longitude]).addTo(map);
            marker.bindPopup(data.address_text);

            // Clear form inputs
            form.reset();
        })
        .catch(error => console.log('Error:', error));
    });

    // Handle delete point
    document.getElementById('pointsTable').addEventListener('click', function () {
        if (event.target.classList.contains('delete-point')) {
            const pointId = event.target.dataset.pointId;
            fetch(`/api/points/${pointId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    event.target.closest('tr').remove();
                }
            })
            .catch(error => console.error('Error', error));
        }
    });
});
