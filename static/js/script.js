// Simple JavaScript for form validation and UX enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Aadhaar number validation
    const aadhaarInputs = document.querySelectorAll('input[name="aadhaar"]');
    aadhaarInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Remove any non-digit characters
            this.value = this.value.replace(/\D/g, '');
        });
    });

    // PIN validation
    const pinInputs = document.querySelectorAll('input[name="pin"]');
    pinInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Remove any non-digit characters
            this.value = this.value.replace(/\D/g, '');
        });
    });

    // Age calculation preview (optional)
    const dobInput = document.getElementById('dob');
    if (dobInput) {
        dobInput.addEventListener('change', function() {
            const dob = new Date(this.value);
            const today = new Date();
            const age = today.getFullYear() - dob.getFullYear() -
                       (today.getMonth() < dob.getMonth() ||
                        (today.getMonth() === dob.getMonth() && today.getDate() < dob.getDate()) ? 1 : 0);

            // You could show age preview here if desired
            console.log('Calculated age:', age);
        });
    }

    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});