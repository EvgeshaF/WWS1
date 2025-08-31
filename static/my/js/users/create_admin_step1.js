
        document.addEventListener('DOMContentLoaded', () => {
            const form = document.getElementById('admin-step1-form');
            const submitBtn = document.getElementById('submit-btn');

            form.addEventListener('submit', (e) => {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-person-check spinner-border spinner-border-sm me-1"></i>Wird validiert...';
            });
        });
