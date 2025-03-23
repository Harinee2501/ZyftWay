// scripts.js
document.getElementById('rideRequestForm').addEventListener('submit', function (e) {
    e.preventDefault();

    let pickupLocation = document.getElementById('pickup').value;
    let dropOffLocation = document.getElementById('dropoff').value;

    // Send the data to backend (using Fetch API)
    fetch('/api/request_ride', {
        method: 'POST',
        body: JSON.stringify({
            pickup: pickupLocation,
            dropoff: dropOffLocation
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert("Ride Requested: " + data.message);
    })
    .catch(error => console.error("Error:", error));
});
