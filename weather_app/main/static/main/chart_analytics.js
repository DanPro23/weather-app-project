document.addEventListener("DOMContentLoaded", function () {
    const cityName = document.getElementById('tempChart')?.dataset?.city;

    if (!cityName || cityName.trim() === '') {
        console.log('No city name provided for chart');
        return;
    }

    fetch(`/weather-chart/${encodeURIComponent(cityName)}/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Chart data error:', data.error);
                // Show an error message in place of the graph
                const canvas = document.getElementById('tempChart');
                const parent = canvas.parentNode;
                parent.innerHTML = `<p style="color: red;">Error loading chart: ${data.error}</p>`;
                return;
            }

            // Checking if there is a date for the schedule
            if (!data.labels || data.labels.length === 0) {
                const canvas = document.getElementById('tempChart');
                const parent = canvas.parentNode;
                parent.innerHTML = '<p style="color: orange;">No data available for chart</p>';
                return;
            }

            const ctx = document.getElementById('tempChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Max Temp (°C)',
                            data: data.max_temp,
                            borderColor: 'rgba(255, 99, 132, 1)',
                            backgroundColor: 'rgba(255, 99, 132, 0.1)',
                            fill: false,
                            tension: 0.1
                        },
                        {
                            label: 'Min Temp (°C)',
                            data: data.min_temp,
                            borderColor: 'rgba(54, 162, 235, 1)',
                            backgroundColor: 'rgba(54, 162, 235, 0.1)',
                            fill: false,
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Temperature (°C)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: `Temperature Chart for ${cityName}`
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error("Chart fetch failed:", error);
            const canvas = document.getElementById('tempChart');
            const parent = canvas.parentNode;
            parent.innerHTML = '<p style="color: red;">Failed to load chart data</p>';
        });
});