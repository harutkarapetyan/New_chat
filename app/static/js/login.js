document.getElementById('loginBtn').addEventListener('click', async () => {
    const email = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = '';

    if (!email || !password) {
        errorDiv.textContent = 'Please fill out both fields.';
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:8002/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Login failed');
        }

        const data = await response.json();
        console.log('Login successful! Token: ' + data.access_token);

        // Optionally, store the token in localStorage or a cookie
        localStorage.setItem('token', data.access_token);

        // After successful login, redirect to the home page
//        window.location.href = "http://127.0.0.1:8002/home-page";
          window.location.href = "http://127.0.0.1:8002/selection-page";


    } catch (error) {
        errorDiv.textContent = error.message;
    }
});
