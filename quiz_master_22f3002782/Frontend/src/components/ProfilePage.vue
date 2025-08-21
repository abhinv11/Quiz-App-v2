<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// Reactive data
const userData = ref(null)
const editMode = ref(false)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const successMessage = ref('')

// Form data for editing
const editForm = ref({
  name: '',
  email: '',
  phone: '',
  qualification: '',
  institution: '',
  yearOfStudy: ''
})

// Computed properties
const isStudent = computed(() => userData.value?.role === 'student')
const profileInitials = computed(() => {
  if (userData.value?.student_profile?.name) {
    return userData.value.student_profile.name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }
  return userData.value?.email?.[0]?.toUpperCase() || 'U'
})

// Fetch user profile data
const fetchUserData = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('token')
    const response = await axios.get('http://127.0.0.1:5000/api/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
    userData.value = response.data.user
    
    // Initialize edit form with current data
    if (userData.value.student_profile) {
      editForm.value = {
        name: userData.value.student_profile.name || '',
        email: userData.value.email || '',
        phone: userData.value.student_profile.phone || '',
        qualification: userData.value.student_profile.qualification || '',
        institution: userData.value.student_profile.institution || '',
        yearOfStudy: userData.value.student_profile.year_of_study || ''
      }
    }
  } catch (error) {
    console.error('Error fetching profile:', error)
    error.value = 'Error loading profile: ' + (error.response?.data?.message || error.message)
  } finally {
    loading.value = false
  }
}

// Save profile changes
const saveProfile = async () => {
  try {
    saving.value = true
    error.value = ''
    successMessage.value = ''
    
    const token = localStorage.getItem('token')
    const response = await axios.put('http://127.0.0.1:5000/api/users/me/profile', {
      name: editForm.value.name,
      phone: editForm.value.phone,
      qualification: editForm.value.qualification,
      institution: editForm.value.institution,
      year_of_study: editForm.value.yearOfStudy
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Update local data
    userData.value = response.data.user
    editMode.value = false
    successMessage.value = 'Profile updated successfully!'
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
  } catch (error) {
    console.error('Error saving profile:', error)
    error.value = 'Error saving profile: ' + (error.response?.data?.message || error.message)
  } finally {
    saving.value = false
  }
}

// Cancel editing
const cancelEdit = () => {
  editMode.value = false
  error.value = ''
  
  // Reset form to original values
  if (userData.value?.student_profile) {
    editForm.value = {
      name: userData.value.student_profile.name || '',
      email: userData.value.email || '',
      phone: userData.value.student_profile.phone || '',
      qualification: userData.value.student_profile.qualification || '',
      institution: userData.value.student_profile.institution || '',
      yearOfStudy: userData.value.student_profile.year_of_study || ''
    }
  }
}

// Format join date
const formatJoinDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  fetchUserData()
})
</script>

<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1 class="page-title">My Profile</h1>
      <p class="page-subtitle">Manage your account information and preferences</p>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading your profile...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error && !userData" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchUserData" class="retry-btn">Try Again</button>
    </div>

    <!-- Profile content -->
    <div v-else-if="userData" class="profile-content">
      <!-- Success message -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <!-- Error message -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div class="profile-card">
        <!-- Profile Header -->
        <div class="profile-card-header">
          <div class="profile-avatar">
            {{ profileInitials }}
          </div>
          <div class="profile-basic-info">
            <h2>{{ userData.student_profile?.name || userData.email }}</h2>
            <p class="profile-role">{{ userData.role || 'User' }}</p>
            <p class="profile-email">{{ userData.email }}</p>
          </div>
          <div class="profile-actions">
            <button 
              v-if="!editMode" 
              @click="editMode = true" 
              class="edit-btn"
            >
              Edit Profile
            </button>
            <div v-else class="edit-actions">
              <button @click="saveProfile" :disabled="saving" class="save-btn">
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
              <button @click="cancelEdit" :disabled="saving" class="cancel-btn">
                Cancel
              </button>
            </div>
          </div>
        </div>

        <!-- Profile Details -->
        <div class="profile-details">
          <div class="details-grid">
            <!-- Name -->
            <div class="detail-item">
              <label class="detail-label">Full Name</label>
              <div v-if="!editMode" class="detail-value">
                {{ userData.student_profile?.name || 'Not provided' }}
              </div>
              <input 
                v-else 
                v-model="editForm.name" 
                type="text" 
                class="detail-input"
                placeholder="Enter your full name"
              />
            </div>

            <!-- Email -->
            <div class="detail-item">
              <label class="detail-label">Email Address</label>
              <div class="detail-value">
                {{ userData.email }}
                <span class="detail-note">(Cannot be changed)</span>
              </div>
            </div>

            <!-- Phone -->
            <div class="detail-item">
              <label class="detail-label">Phone Number</label>
              <div v-if="!editMode" class="detail-value">
                {{ userData.student_profile?.phone || 'Not provided' }}
              </div>
              <input 
                v-else 
                v-model="editForm.phone" 
                type="tel" 
                class="detail-input"
                placeholder="Enter your phone number"
              />
            </div>

            <!-- Qualification -->
            <div class="detail-item">
              <label class="detail-label">Qualification</label>
              <div v-if="!editMode" class="detail-value">
                {{ userData.student_profile?.qualification || 'Not provided' }}
              </div>
              <select v-else v-model="editForm.qualification" class="detail-input">
                <option value="">Select qualification</option>
                <option value="High School">High School</option>
                <option value="Bachelor's Degree">Bachelor's Degree</option>
                <option value="Master's Degree">Master's Degree</option>
                <option value="PhD">PhD</option>
                <option value="Diploma">Diploma</option>
                <option value="Certificate">Certificate</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <!-- Institution -->
            <div class="detail-item">
              <label class="detail-label">Institution</label>
              <div v-if="!editMode" class="detail-value">
                {{ userData.student_profile?.institution || 'Not provided' }}
              </div>
              <input 
                v-else 
                v-model="editForm.institution" 
                type="text" 
                class="detail-input"
                placeholder="Enter your institution name"
              />
            </div>

            <!-- Year of Study -->
            <div class="detail-item">
              <label class="detail-label">Year of Study</label>
              <div v-if="!editMode" class="detail-value">
                {{ userData.student_profile?.year_of_study || 'Not provided' }}
              </div>
              <select v-else v-model="editForm.yearOfStudy" class="detail-input">
                <option value="">Select year</option>
                <option value="1st Year">1st Year</option>
                <option value="2nd Year">2nd Year</option>
                <option value="3rd Year">3rd Year</option>
                <option value="4th Year">4th Year</option>
                <option value="Graduate">Graduate</option>
                <option value="Postgraduate">Postgraduate</option>
              </select>
            </div>

            <!-- User ID -->
            <div class="detail-item">
              <label class="detail-label">User ID</label>
              <div class="detail-value">
                #{{ userData.id }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Info Card -->
      <div class="info-card">
        <h3>Account Information</h3>
        <div class="info-grid">
          <div class="info-item">
            <div class="info-icon">🎯</div>
            <div class="info-content">
              <h4>Quiz Performance</h4>
              <p>View your scores and progress in the Scores section</p>
            </div>
          </div>
          <div class="info-item">
            <div class="info-icon">🔒</div>
            <div class="info-content">
              <h4>Account Security</h4>
              <p>Your account is secured with JWT token authentication</p>
            </div>
          </div>
          <div class="info-item">
            <div class="info-icon">📚</div>
            <div class="info-content">
              <h4>Learning Progress</h4>
              <p>Take quizzes across different subjects to improve your knowledge</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: #64748b;
  font-size: 1.1rem;
  margin: 0;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
}

.success-message {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #059669;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
}

.retry-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
}

.retry-btn:hover {
  background: #5a67d8;
}

.profile-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
  margin-bottom: 2rem;
  overflow: hidden;
}

.profile-card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: bold;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.profile-basic-info {
  flex-grow: 1;
}

.profile-basic-info h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 700;
}

.profile-role {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  opacity: 0.9;
  text-transform: capitalize;
}

.profile-email {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}

.profile-actions {
  display: flex;
  gap: 1rem;
}

.edit-btn, .save-btn, .cancel-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.edit-btn:hover, .save-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.cancel-btn {
  background: transparent;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
}

.profile-details {
  padding: 2rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-label {
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  color: #1f2937;
  font-size: 1.1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.detail-note {
  font-size: 0.8rem;
  color: #64748b;
  font-style: italic;
  margin-left: 0.5rem;
}

.detail-input {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.detail-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.info-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
  padding: 2rem;
}

.info-card h3 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.3rem;
  font-weight: 700;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.info-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  flex-shrink: 0;
}

.info-content h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.info-content p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.4;
}

/* Responsive design */
@media (max-width: 768px) {
  .profile-container {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .profile-card-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .edit-actions {
    flex-direction: column;
    width: 100%;
  }
}
</style>
