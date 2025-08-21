<script>
import axios from 'axios';
export default {
    data() {
        return {
            FormData: {
                email: '',
                password: ''
            },
            token: "",
            loading: false
        }
    },
    methods: {
        async loginUser() {
            this.loading = true;
            try {
                // First, login to get the token
                const loginResponse = await axios.post('http://127.0.0.1:5000/api/login', JSON.stringify(this.FormData), {
                    headers: {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    }
                });

                if (loginResponse.status === 200) {
                    this.token = loginResponse.data.access_token;
                    localStorage.setItem('token', loginResponse.data.access_token);
                    
                    // Get user details to determine role
                    const userResponse = await axios.get('http://127.0.0.1:5000/api/me', {
                        headers: {
                            "Authorization": `Bearer ${this.token}`,
                            "Content-Type": "application/json"
                        }
                    });

                    if (userResponse.status === 200) {
                        const userData = userResponse.data.user;
                        const userRoles = userData.roles;
                        
                        // Store user data in localStorage for future use
                        localStorage.setItem('userData', JSON.stringify(userData));
                        
                        // Role-based redirection
                        if (userRoles.includes('admin')) {
                            // Redirect to admin dashboard
                            this.$router.push('/admin');
                            alert('Welcome Admin! Redirecting to admin dashboard...');
                        } else if (userRoles.includes('student') || userRoles.includes('user')) {
                            // Redirect to student dashboard
                            this.$router.push('/dashboard');
                            alert('Login successful! Redirecting to dashboard...');
                        } else {
                            // Default redirect to student dashboard
                            this.$router.push('/dashboard');
                            alert('Login successful! Redirecting to dashboard...');
                        }
                    }
                } else {
                    alert('Login failed: ' + loginResponse.data.message);
                }
            } catch (error) {
                console.error('Login error:', error);
                if (error.response) {
                    // Server responded with error status
                    alert('Login failed: ' + (error.response.data.message || 'Invalid credentials'));
                } else if (error.request) {
                    // Request was made but no response received
                    alert('Network error: Unable to connect to server');
                } else {
                    // Something else happened
                    alert('An error occurred while logging in: ' + error.message);
                }
            } finally {
                this.loading = false;
            }
        }
    }
}
</script>



<template>
    <div class="login-container">
        <h3 class="text-center mb-4">Welcome Back</h3>
        <form @submit.prevent="loginUser">
        <div class="mb-3">
            <label for="email" class="form-label">Email address</label>
            <input type="email" class="form-control" id="email" placeholder="name@example.com" v-model="FormData.email" required>
        </div>
        <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input type="password" class="form-control" id="password" placeholder="Enter your password" v-model="FormData.password" required>
        </div>
        <div class="mb-3 form-check">
            <input type="checkbox" class="form-check-input" id="remember">
            <label class="form-check-label" for="remember">Remember me</label>
        </div>
        <div class="d-grid">
            <button type="submit" class="btn btn-custom" :disabled="loading">
                <span v-if="loading">Logging in...</span>
                <span v-else>Login</span>
            </button>
        </div>
        </form>
        <div class="text-center mt-3">
            <small>Don't have an account? <router-link to="/register">Register</router-link></small>
        </div>
    </div>
</template>



<style>
body {
      background: linear-gradient(to right, #667eea, #764ba2);
      height: 100vh;
    }
    .login-container {
      max-width: 400px;
      margin: auto;
      margin-top: 100px;
      background-color: white;
      border-radius: 15px;
      padding: 30px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    .form-control:focus {
      box-shadow: none;
      border-color: #667eea;
    }
    .btn-custom {
      background-color: #667eea;
      color: white;
    }
    .btn-custom:hover {
      background-color: #5a67d8;
    }
</style>