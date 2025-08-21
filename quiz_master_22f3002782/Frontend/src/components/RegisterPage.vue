<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// Form data
const formData = ref({
  email: '',
  password: '',
  confirmPassword: '',
  name: '',
  dob: '',
  qualification: ''
})

// Form state
const loading = ref(false)
const errors = ref({})
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Qualification options
const qualificationOptions = [
  'High School',
  'Diploma',
  'Bachelor\'s Degree',
  'Master\'s Degree',
  'PhD',
  'Professional Certification',
  'Other'
]

// Validation functions
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validateForm = () => {
  const newErrors = {}

  // Email validation
  if (!formData.value.email) {
    newErrors.email = 'Email is required'
  } else if (!validateEmail(formData.value.email)) {
    newErrors.email = 'Please enter a valid email address'
  }

  // Password validation
  if (!formData.value.password) {
    newErrors.password = 'Password is required'
  } else if (formData.value.password.length < 6) {
    newErrors.password = 'Password must be at least 6 characters long'
  }

  // Confirm password validation
  if (!formData.value.confirmPassword) {
    newErrors.confirmPassword = 'Please confirm your password'
  } else if (formData.value.password !== formData.value.confirmPassword) {
    newErrors.confirmPassword = 'Passwords do not match'
  }

  // Name validation
  if (!formData.value.name) {
    newErrors.name = 'Full name is required'
  } else if (formData.value.name.length < 2) {
    newErrors.name = 'Name must be at least 2 characters long'
  }

  // Date of birth validation
  if (!formData.value.dob) {
    newErrors.dob = 'Date of birth is required'
  } else {
    const today = new Date()
    const birthDate = new Date(formData.value.dob)
    const age = today.getFullYear() - birthDate.getFullYear()
    
    if (age < 13) {
      newErrors.dob = 'You must be at least 13 years old to register'
    } else if (age > 120) {
      newErrors.dob = 'Please enter a valid date of birth'
    }
  }

  // Qualification validation
  if (!formData.value.qualification) {
    newErrors.qualification = 'Qualification is required'
  }

  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

// Clear error when user starts typing
const clearError = (field) => {
  if (errors.value[field]) {
    delete errors.value[field]
  }
}

// Submit form
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const response = await axios.post('http://127.0.0.1:5000/api/register', {
      email: formData.value.email,
      password: formData.value.password,
      name: formData.value.name,
      dob: formData.value.dob,
      qualification: formData.value.qualification
    })

    // Registration successful
    alert('Registration successful! Please login with your credentials.')
    router.push('/login')
  } catch (error) {
    console.error('Registration error:', error)
    
    if (error.response?.status === 409) {
      errors.value.email = 'An account with this email already exists'
    } else if (error.response?.data?.message) {
      alert('Registration failed: ' + error.response.data.message)
    } else {
      alert('Registration failed. Please try again.')
    }
  } finally {
    loading.value = false
  }
}

// Toggle password visibility
const togglePasswordVisibility = (field) => {
  if (field === 'password') {
    showPassword.value = !showPassword.value
  } else if (field === 'confirmPassword') {
    showConfirmPassword.value = !showConfirmPassword.value
  }
}

// Navigate to login
const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-page-container">
    <div class="register-card">
      <!-- Header -->
      <div class="register-header">
        <h1>Create Account</h1>
        <p>Join us and start your learning journey</p>
      </div>

      <!-- Registration Form -->
      <form @submit.prevent="handleSubmit" class="register-form">
        <!-- Email Field -->
        <div class="form-group">
          <label for="email" class="form-label">
            Email Address <span class="required">*</span>
          </label>
          <div class="input-wrapper">
            <input
              id="email"
              type="email"
              v-model="formData.email"
              @input="clearError('email')"
              :class="['form-input', { 'error': errors.email }]"
              placeholder="Enter your email address"
              autocomplete="email"
            />
            <span class="input-icon">📧</span>
          </div>
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <!-- Name Field -->
        <div class="form-group">
          <label for="name" class="form-label">
            Full Name <span class="required">*</span>
          </label>
          <div class="input-wrapper">
            <input
              id="name"
              type="text"
              v-model="formData.name"
              @input="clearError('name')"
              :class="['form-input', { 'error': errors.name }]"
              placeholder="Enter your full name"
              autocomplete="name"
            />
            <span class="input-icon">👤</span>
          </div>
          <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
        </div>

        <!-- Date of Birth Field -->
        <div class="form-group">
          <label for="dob" class="form-label">
            Date of Birth <span class="required">*</span>
          </label>
          <div class="input-wrapper">
            <input
              id="dob"
              type="date"
              v-model="formData.dob"
              @input="clearError('dob')"
              :class="['form-input', { 'error': errors.dob }]"
              :max="new Date().toISOString().split('T')[0]"
            />
            <span class="input-icon">📅</span>
          </div>
          <span v-if="errors.dob" class="error-message">{{ errors.dob }}</span>
        </div>

        <!-- Qualification Field -->
        <div class="form-group">
          <label for="qualification" class="form-label">
            Qualification <span class="required">*</span>
          </label>
          <div class="input-wrapper">
            <select
              id="qualification"
              v-model="formData.qualification"
              @change="clearError('qualification')"
              :class="['form-input', 'form-select', { 'error': errors.qualification }]"
            >
              <option value="">Select your qualification</option>
              <option v-for="option in qualificationOptions" :key="option" :value="option">
                {{ option }}
              </option>
            </select>
            <span class="input-icon">🎓</span>
          </div>
          <span v-if="errors.qualification" class="error-message">{{ errors.qualification }}</span>
        </div>

        <!-- Password Field -->
        <div class="form-group">
          <label for="password" class="form-label">
            Password <span class="required">*</span>
          </label>
          <div class="input-wrapper">
            <input
              id="password"
              :type="showPassword ? 'text' : 'password'"
              v-model="formData.password"
              @input="clearError('password')"
              :class="['form-input', { 'error': errors.password }]"
              placeholder="Create a strong password"
              autocomplete="new-password"
            />
            <span class="input-icon">🔒</span>
            <button
              type="button"
              class="password-toggle"
              @click="togglePasswordVisibility('password')"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          <div class="password-hint">
            Password should be at least 6 characters long
          </div>
        </div>

        <!-- Confirm Password Field -->
        <div class="form-group">
          <label for="confirmPassword" class="form-label">
            Confirm Password <span class="required">*</span>
          </label>
          <div class="input-wrapper">
            <input
              id="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              v-model="formData.confirmPassword"
              @input="clearError('confirmPassword')"
              :class="['form-input', { 'error': errors.confirmPassword }]"
              placeholder="Confirm your password"
              autocomplete="new-password"
            />
            <span class="input-icon">🔒</span>
            <button
              type="button"
              class="password-toggle"
              @click="togglePasswordVisibility('confirmPassword')"
            >
              {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="loading"
          class="submit-btn"
        >
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>

      <!-- Login Link -->
      <div class="login-link">
        <p>Already have an account?</p>
        <button @click="goToLogin" class="link-btn">Sign In</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.register-card {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.register-header p {
  color: #64748b;
  font-size: 1rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.required {
  color: #ef4444;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  padding-left: 3rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #fafafa;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1rem;
  padding-right: 3rem;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  opacity: 0.6;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.password-toggle:hover {
  opacity: 1;
}

.error-message {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.password-hint {
  color: #64748b;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.login-link {
  text-align: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.login-link p {
  color: #64748b;
  margin-bottom: 0.5rem;
}

.link-btn {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.link-btn:hover {
  color: #764ba2;
}

/* Responsive Design */
@media (max-width: 640px) {
  .register-page-container {
    padding: 1rem;
  }
  
  .register-card {
    padding: 2rem;
  }
  
  .register-header h1 {
    font-size: 1.5rem;
  }
  
  .form-input {
    padding: 0.75rem 0.875rem;
    padding-left: 2.75rem;
  }
}
</style>