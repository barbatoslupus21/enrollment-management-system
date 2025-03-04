// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('dropdownMenu');
    const accountSection = document.querySelector('.account-section');
    
    if (!accountSection.contains(event.target) && 
        !dropdown.contains(event.target)) {
        dropdown.classList.remove('active');
    }
});

function toggleDropdown() {
    const dropdown = document.getElementById('dropdownMenu');
    const sidebar = document.querySelector('.sidebar');
    const isMinimized = sidebar.classList.contains('minimized');
    
    dropdown.classList.toggle('active');
    
    // Position dropdown correctly based on sidebar state
    if (isMinimized) {
        dropdown.style.left = '50px';
    } else {
        dropdown.style.left = '10px';
    }
}

// Form Validation
(() => {
    'use strict'
  
    const forms = document.querySelectorAll('.needs-validation')
  
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
  
        form.classList.add('was-validated')
      }, false)
    })
  })()

// Login Password toggle

function togglePassword(id, eyeId) {
    const passwordInput = document.getElementById(id);
    const eyeIcon = document.getElementById(eyeId);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeIcon.innerHTML = `
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
            <circle cx="12" cy="12" r="3"></circle>
        `;
    } else {
        passwordInput.type = 'password';
        eyeIcon.innerHTML = `
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
            <line x1="1" y1="1" x2="23" y2="23"></line>
        `;
    }
  }