document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById('reliefChart').getContext('2d');

    // Sample Data for Relief Funds Over Time
    const chartData = {
        labels: ["January", "February", "March", "April", "May", "June"],
        datasets: [{
            label: 'Relief Funds Received ($)',
            data: [200, 300, 400, 500, 600, 700],
            backgroundColor: 'rgba(0, 123, 255, 0.5)',
            borderColor: '#007BFF',
            borderWidth: 2
        }]
    };

    // Chart.js Configuration
    const chartConfig = {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount ($)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Months'
                    }
                }
            }
        }
    };

    // Render Chart
    new Chart(ctx, chartConfig);
});
