document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form.form');
    const stars = form ? form.querySelectorAll('.star-rating .fa-star') : [];
    const ratingInput = form ? form.querySelector('#rating') : null;

    if (!form || !stars.length || !ratingInput) {
        console.error('Star rating elements not found', { form: !!form, stars: stars.length, ratingInput: !!ratingInput });
        return;
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
            alert('Please select a rating by clicking the stars.'); 
        }
    });
});
