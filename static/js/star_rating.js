document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form.form');
    
    // If no form exists, exit silently
    if (!form) {
        console.log('No review form found on this page.');
        return;
    }

    const stars = form.querySelectorAll('.star-rating .fa-star');
    const ratingInput = form.querySelector('#rating');

    if (!stars.length || !ratingInput) {
        console.error('Star rating elements not found within form:', {
            stars: stars.length,
            ratingInput: !!ratingInput
        });
        return;
    }

    // Function to show Bootstrap alert
    function showRatingAlert(message) {
        // Remove any existing alert
        const existingAlert = form.querySelector('.rating-alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        // Create new Bootstrap alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show rating-alert';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        // Insert alert before the star-rating div
        const starRatingDiv = form.querySelector('.star-rating');
        form.prepend(alertDiv, starRatingDiv);
        // form.insertBefore(alertDiv, starRatingDiv);

        // Auto-dismiss after 5 seconds (optional)
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    stars.forEach(star => {
        star.addEventListener('click', function () {
            const rating = this.getAttribute('data-rating');
            ratingInput.value = rating;
            stars.forEach(s => {
                s.classList.toggle('checked', s.getAttribute('data-rating') <= rating);
            });
        });

        star.addEventListener('mouseover', function () {
            const hoverRating = this.getAttribute('data-rating');
            stars.forEach(s => {
                s.classList.toggle('checked', s.getAttribute('data-rating') <= hoverRating);
            });
        });

        star.addEventListener('mouseout', function () {
            const selectedRating = ratingInput.value || 0;
            stars.forEach(s => {
                s.classList.toggle('checked', s.getAttribute('data-rating') <= selectedRating);
            });
        });
    });

    form.addEventListener('submit', function (e) {
        if (ratingInput.value === "0" || ratingInput.value === "") {
            e.preventDefault();
            showRatingAlert('Please select a rating by clicking the stars.');
        }
    });
});