<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// Reactive data
const users = ref([])
const loading = ref(true)
const error = ref('')
const successMessage = ref('')
const searchQuery = ref('')
const selectedRole = ref('')
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const userToDelete = ref(null)

// Edit form data
const editForm = ref({
  email: '',
  active: true,
  roles: [],
  name: '',
  dob: '',
  qualification: ''
})

// Available roles
const availableRoles = ['admin', 'student']
const qualificationOptions = ['High School', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD', 'Diploma', 'Certificate', 'Other']

// Computed properties
const filteredUsers = computed(() => {
  let filtered = users.value
  
  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.email.toLowerCase().includes(query) ||
      (user.student_profile?.name && user.student_profile.name.toLowerCase().includes(query))
    )
  }
  
  // Filter by role
  if (selectedRole.value) {
    filtered = filtered.filter(user => 
      user.roles.includes(selectedRole.value)
    )
  }
  
  return filtered
})

const totalUsers = computed(() => users.value.length)
const activeUsers = computed(() => users.value.filter(user => user.active).length)
const adminUsers = computed(() => users.value.filter(user => user.roles.includes('admin')).length)
const studentUsers = computed(() => users.value.filter(user => user.roles.includes('student')).length)

// Fetch all users
const fetchUsers = async () => {
  try {
    loading.value = true
    error.value = ''
    const token = localStorage.getItem('token')
    const response = await axios.get('http://127.0.0.1:5000/api/admin/users', {
      headers: { Authorization: `Bearer ${token}` }
    })
    users.value = response.data.users || []
  } catch (err) {
    console.error('Error fetching users:', err)
    error.value = 'Error loading users: ' + (err.response?.data?.message || err.message)
  } finally {
    loading.value = false
  }
}

// Open edit modal
const openEditModal = (user) => {
  editingUser.value = user
  editForm.value = {
    email: user.email,
    active: user.active,
    roles: [...user.roles],
    name: user.student_profile?.name || '',
    dob: user.student_profile?.dob || '',
    qualification: user.student_profile?.qualification || ''
  }
  showEditModal.value = true
}

// Close edit modal
const closeEditModal = () => {
  showEditModal.value = false
  editingUser.value = null
  editForm.value = {
    email: '',
    active: true,
    roles: [],
    name: '',
    dob: '',
    qualification: ''
  }
}

// Save user changes
const saveUser = async () => {
  try {
    if (!editingUser.value) return
    
    const token = localStorage.getItem('token')
    const updateData = {
      email: editForm.value.email,
      active: editForm.value.active,
      roles: editForm.value.roles
    }
    
    // Add student profile data if user has student role
    if (editForm.value.roles.includes('student')) {
      updateData.name = editForm.value.name
      updateData.dob = editForm.value.dob
      updateData.qualification = editForm.value.qualification
    }
    
    await axios.put(`http://127.0.0.1:5000/api/admin/users/${editingUser.value.id}`, updateData, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    successMessage.value = 'User updated successfully!'
    closeEditModal()
    await fetchUsers() // Refresh the user list
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
  } catch (err) {
    console.error('Error updating user:', err)
    error.value = 'Error updating user: ' + (err.response?.data?.message || err.message)
  }
}

// Open delete modal
const openDeleteModal = (user) => {
  userToDelete.value = user
  showDeleteModal.value = true
}

// Close delete modal
const closeDeleteModal = () => {
  showDeleteModal.value = false
  userToDelete.value = null
}

// Delete user
const deleteUser = async () => {
  try {
    if (!userToDelete.value) return
    
    const token = localStorage.getItem('token')
    await axios.delete(`http://127.0.0.1:5000/api/admin/users/${userToDelete.value.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    successMessage.value = 'User deleted successfully!'
    closeDeleteModal()
    await fetchUsers() // Refresh the user list
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
  } catch (err) {
    console.error('Error deleting user:', err)
    error.value = 'Error deleting user: ' + (err.response?.data?.message || err.message)
  }
}

// Toggle user role
const toggleRole = (role) => {
  const index = editForm.value.roles.indexOf(role)
  if (index === -1) {
    editForm.value.roles.push(role)
  } else {
    editForm.value.roles.splice(index, 1)
  }
}

// Format date
const formatDate = (dateString) => {
  if (!dateString) return 'Not provided'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Get role badge class
const getRoleBadgeClass = (role) => {
  return role === 'admin' ? 'role-badge-admin' : 'role-badge-student'
}

// Clear filters
const clearFilters = () => {
  searchQuery.value = ''
  selectedRole.value = ''
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="admin-users-container">
    <div class="users-header">
      <h1 class="page-title">User Management</h1>
      <p class="page-subtitle">Manage user accounts, roles, and permissions</p>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="fetchUsers" class="retry-btn">Retry</button>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <h3>{{ totalUsers }}</h3>
          <p>Total Users</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <h3>{{ activeUsers }}</h3>
          <p>Active Users</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👑</div>
        <div class="stat-info">
          <h3>{{ adminUsers }}</h3>
          <p>Administrators</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎓</div>
        <div class="stat-info">
          <h3>{{ studentUsers }}</h3>
          <p>Students</p>
        </div>
      </div>
    </div>

    <!-- Filters and Actions -->
    <div class="filters-section">
      <div class="filters">
        <div class="filter-group">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search users by email or name..." 
            class="search-input"
          />
        </div>
        <div class="filter-group">
          <select v-model="selectedRole" class="role-filter">
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="student">Student</option>
          </select>
        </div>
        <button @click="clearFilters" class="clear-filters-btn">
          Clear Filters
        </button>
      </div>
      <div class="actions">
        <button @click="fetchUsers" class="refresh-btn" :disabled="loading">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && users.length === 0" class="loading">
      <div class="spinner"></div>
      <p>Loading users...</p>
    </div>

    <!-- Users Table -->
    <div v-else-if="filteredUsers.length > 0" class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Name</th>
            <th>Roles</th>
            <th>Status</th>
            <th>Qualification</th>
            <th>Date of Birth</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
            <td class="user-id">#{{ user.id }}</td>
            <td class="user-email">{{ user.email }}</td>
            <td class="user-name">{{ user.student_profile?.name || 'N/A' }}</td>
            <td class="user-roles">
              <span 
                v-for="role in user.roles" 
                :key="role" 
                :class="['role-badge', getRoleBadgeClass(role)]"
              >
                {{ role }}
              </span>
            </td>
            <td class="user-status">
              <span :class="['status-badge', user.active ? 'status-active' : 'status-inactive']">
                {{ user.active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="user-qualification">{{ user.student_profile?.qualification || 'N/A' }}</td>
            <td class="user-dob">{{ formatDate(user.student_profile?.dob) }}</td>
            <td class="user-actions">
              <button @click="openEditModal(user)" class="edit-btn">
                Edit
              </button>
              <button @click="openDeleteModal(user)" class="delete-btn">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="empty-state">
      <div class="empty-icon">👥</div>
      <h3>No Users Found</h3>
      <p v-if="searchQuery || selectedRole">
        No users match your current filters. Try adjusting your search criteria.
      </p>
      <p v-else>
        No users are available in the system.
      </p>
      <button @click="clearFilters" class="clear-filters-btn">
        Clear Filters
      </button>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Edit User</h3>
          <button @click="closeEditModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveUser">
            <!-- Email -->
            <div class="form-group">
              <label>Email</label>
              <input v-model="editForm.email" type="email" required class="form-input" />
            </div>

            <!-- Status -->
            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="editForm.active" type="checkbox" />
                <span class="checkmark"></span>
                Active User
              </label>
            </div>

            <!-- Roles -->
            <div class="form-group">
              <label>Roles</label>
              <div class="role-checkboxes">
                <label v-for="role in availableRoles" :key="role" class="checkbox-label">
                  <input 
                    type="checkbox" 
                    :checked="editForm.roles.includes(role)"
                    @change="toggleRole(role)"
                  />
                  <span class="checkmark"></span>
                  {{ role.charAt(0).toUpperCase() + role.slice(1) }}
                </label>
              </div>
            </div>

            <!-- Student Profile Fields (only if student role is selected) -->
            <div v-if="editForm.roles.includes('student')" class="student-profile-section">
              <h4>Student Profile</h4>
              
              <div class="form-group">
                <label>Name</label>
                <input v-model="editForm.name" type="text" class="form-input" />
              </div>

              <div class="form-group">
                <label>Date of Birth</label>
                <input v-model="editForm.dob" type="date" class="form-input" />
              </div>

              <div class="form-group">
                <label>Qualification</label>
                <select v-model="editForm.qualification" class="form-input">
                  <option value="">Select qualification</option>
                  <option v-for="qual in qualificationOptions" :key="qual" :value="qual">
                    {{ qual }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" @click="closeEditModal" class="cancel-btn">
                Cancel
              </button>
              <button type="submit" class="save-btn">
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete User Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Delete User</h3>
          <button @click="closeDeleteModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete the user:</p>
          <div class="user-info">
            <strong>{{ userToDelete?.email }}</strong>
            <span v-if="userToDelete?.student_profile?.name">
              ({{ userToDelete.student_profile.name }})
            </span>
          </div>
          <p class="warning-text">
            This action cannot be undone. All associated data including quiz scores will be permanently deleted.
          </p>
          <div class="form-actions">
            <button @click="closeDeleteModal" class="cancel-btn">
              Cancel
            </button>
            <button @click="deleteUser" class="delete-confirm-btn">
              Delete User
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-users-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.users-header {
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

.success-message {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #059669;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: center;
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

.retry-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  margin-left: 0.5rem;
}

.retry-btn:hover {
  background: #b91c1c;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
}

.stat-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
}

.stat-info h3 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  color: #1f2937;
}

.stat-info p {
  margin: 0;
  color: #64748b;
  font-weight: 500;
}

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-input, .role-filter {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  min-width: 200px;
}

.search-input:focus, .role-filter:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.clear-filters-btn {
  background: #64748b;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.clear-filters-btn:hover {
  background: #475569;
}

.actions {
  display: flex;
  gap: 1rem;
}

.refresh-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #5a67d8;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.users-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.user-row:hover {
  background: #f8fafc;
}

.user-id {
  font-weight: 600;
  color: #64748b;
}

.user-email {
  font-weight: 500;
  color: #1f2937;
}

.user-name {
  color: #374151;
}

.user-roles {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.role-badge-admin {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.role-badge-student {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.user-status {
  text-align: center;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-active {
  background: #f0fdf4;
  color: #059669;
  border: 1px solid #bbf7d0;
}

.status-inactive {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.user-qualification, .user-dob {
  color: #64748b;
  font-size: 0.9rem;
}

.user-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.edit-btn:hover {
  background: #5a67d8;
}

.delete-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.delete-btn:hover {
  background: #dc2626;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #64748b;
  margin-bottom: 1rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #64748b;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

.role-checkboxes {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.student-profile-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.student-profile-section h4 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.cancel-btn {
  background: #64748b;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #475569;
}

.save-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.save-btn:hover {
  background: #5a67d8;
}

.delete-confirm-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.delete-confirm-btn:hover {
  background: #dc2626;
}

.user-info {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
  border: 1px solid #e5e7eb;
}

.warning-text {
  color: #dc2626;
  font-weight: 500;
  margin: 1rem 0;
}

/* Responsive design */
@media (max-width: 768px) {
  .admin-users-container {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .users-table-container {
    overflow-x: auto;
  }
  
  .users-table {
    min-width: 800px;
  }
  
  .user-actions {
    flex-direction: column;
  }
  
  .modal {
    width: 95%;
    margin: 1rem;
  }
}
</style>
