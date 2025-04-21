document.addEventListener('DOMContentLoaded', function() {
    // Initialize Swiper
    new Swiper('.swiper-container', {
        loop: true,
        autoplay: {
            delay: 5000,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
    });

    // Initialize charts
    document.querySelectorAll('.chart').forEach(canvas => {
        const ctx = canvas.getContext('2d');
        const type = canvas.dataset.type;
        const labels = JSON.parse(canvas.dataset.labels);
        const data = JSON.parse(canvas.dataset.data);

        new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: canvas.parentElement.querySelector('h3')?.textContent || ''
                    }
                }
            }
        });
    });
});
