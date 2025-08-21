<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive authentication state
const isLoggedIn = ref(false)
const userRole = ref('student')
const userData = ref(null)

// Check authentication status
const checkAuthStatus = () => {
  const token = localStorage.getItem('token')
  const storedUserData = localStorage.getItem('userData')
  
  if (token && storedUserData) {
    isLoggedIn.value = true
    userData.value = JSON.parse(storedUserData)
    
    // Determine user role
    if (userData.value.roles && userData.value.roles.includes('admin')) {
      userRole.value = 'admin'
    } else {
      userRole.value = 'student'
    }
  } else {
    isLoggedIn.value = false
    userData.value = null
    userRole.value = 'student'
  }
}

// Logout function
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userData')
  isLoggedIn.value = false
  userData.value = null
  userRole.value = 'student'
  router.push('/')
}

// Navigation items based on authentication and role
const navigationItems = computed(() => {
  if (!isLoggedIn.value) {
    return [
      { name: 'Home', path: '/' },
      { name: 'Subjects', path: '/subjects' },
      { name: 'Login', path: '/login' },
      { name: 'Register', path: '/register' }
    ]
  }
  
  const baseItems = [
    { name: 'Dashboard', path: userRole.value === 'admin' ? '/admin' : '/dashboard' },
    { name: 'Subjects', path: '/subjects' },
    { name: 'Profile', path: '/profile' },
    { name: 'Scores', path: '/scores' }
  ]
  
  if (userRole.value === 'admin') {
    baseItems.push({ name: 'Admin Panel', path: '/admin' })
    baseItems.push({ name: 'Analytics', path: '/admin/analytics' })
  }
  
  return baseItems
})

// Check auth status on component mount
onMounted(() => {
  checkAuthStatus()
  
  // Listen for storage changes (useful for multiple tabs)
  window.addEventListener('storage', checkAuthStatus)
})
</script>

<template>
  <nav class="navbar">
    <div class="nav-container">
      <!-- Logo -->
      <router-link to="/" class="nav-logo">
        <span class="logo-text">QuizApp</span>
      </router-link>

      <!-- Navigation Links -->
      <div class="nav-links">
        <router-link 
          v-for="item in navigationItems" 
          :key="item.name"
          :to="item.path" 
          class="nav-link"
          :class="{ 'nav-link-auth': item.name === 'Login' || item.name === 'Register' }"
        >
          {{ item.name }}
        </router-link>
        
        <!-- User info and logout if logged in -->
        <div v-if="isLoggedIn" class="user-section">
          <span class="user-greeting">
            Welcome, {{ userData?.student_profile?.name || userData?.email || 'User' }}!
          </span>
          <button class="nav-link logout-btn" @click="logout">
            Logout
          </button>
        </div>
      </div>

      <!-- Mobile menu toggle (for future mobile implementation) -->
      <div class="mobile-menu-toggle">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid #e5e7eb;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.nav-logo {
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-greeting {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.nav-link {
  text-decoration: none;
  color: #64748b;
  font-weight: 500;
  transition: color 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 1rem;
}

.nav-link:hover {
  color: #667eea;
}

.nav-link.router-link-active {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.nav-link-auth {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
}

.nav-link-auth:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  color: white !important;
}

.logout-btn {
  background: #ef4444;
  color: white !important;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
}

.logout-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.mobile-menu-toggle {
  display: none;
  flex-direction: column;
  cursor: pointer;
  gap: 4px;
}

.mobile-menu-toggle span {
  width: 25px;
  height: 3px;
  background: #64748b;
  transition: 0.3s;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
  }
  
  .nav-links {
    display: none; /* Will implement mobile menu later */
  }
  
  .mobile-menu-toggle {
    display: flex;
  }
}
</style>