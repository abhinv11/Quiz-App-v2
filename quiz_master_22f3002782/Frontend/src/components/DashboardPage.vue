<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// Reactive data
const userStats = ref({
  totalQuizzes: 0,
  completedQuizzes: 0,
  averageScore: 0,
  totalSubjects: 0
})

const recentScores = ref([])
const availableSubjects = ref([])
const recentQuizzes = ref([])
const loading = ref(true)
const userData = ref(null)

// Get user data from localStorage
const getUserData = () => {
  const storedUserData = localStorage.getItem('userData')
  if (storedUserData) {
    userData.value = JSON.parse(storedUserData)
  }
}

// Computed properties
const welcomeMessage = computed(() => {
  if (userData.value?.student_profile?.name) {
    return `Welcome back, ${userData.value.student_profile.name}!`
  }
  return 'Welcome to your Dashboard!'
})

const completionPercentage = computed(() => {
  if (userStats.value.totalQuizzes === 0) return 0
  return Math.round((userStats.value.completedQuizzes / userStats.value.totalQuizzes) * 100)
})

// API calls
const fetchUserStats = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://127.0.0.1:5000/api/users/me/scores', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const scores = response.data.scores
    userStats.value.completedQuizzes = scores.length
    
    if (scores.length > 0) {
      const totalScore = scores.reduce((sum, score) => sum + ((score.total_scored / score.total_possible) * 100), 0)
      userStats.value.averageScore = Math.round(totalScore / scores.length)
    }
    
    recentScores.value = scores.slice(0, 5).map(score => ({
      ...score,
      score: Math.round((score.total_scored / score.total_possible) * 100)
    }))
  } catch (error) {
    console.error('Error fetching user stats:', error)
  }
}

const fetchSubjects = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://127.0.0.1:5000/api/subjects', {
      headers: { Authorization: `Bearer ${token}` }
    })
    availableSubjects.value = response.data.subjects.slice(0, 6) // Show 6 subjects
    userStats.value.totalSubjects = response.data.subjects.length
  } catch (error) {
    console.error('Error fetching subjects:', error)
  }
}

const fetchQuizzes = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://127.0.0.1:5000/api/quizzes', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    userStats.value.totalQuizzes = response.data.quizzes.length
    recentQuizzes.value = response.data.quizzes
      .filter(quiz => quiz.is_published) // Only show published quizzes
      .slice(0, 6) // Show 6 recent quizzes
  } catch (error) {
    console.error('Error fetching quizzes:', error)
  }
}

// Quiz functionality
const startQuiz = async (quizId) => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(`http://127.0.0.1:5000/api/quizzes/${quizId}/start`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Navigate to quiz taking page with quiz data
    window.location.href = `/take-quiz/${quizId}?score_id=${response.data.score_id}`
  } catch (error) {
    console.error('Error starting quiz:', error)
    alert('Error starting quiz: ' + (error.response?.data?.message || error.message))
  }
}

// Initialize dashboard
const initDashboard = async () => {
  loading.value = true
  getUserData()
  
  await Promise.all([
    fetchUserStats(),
    fetchSubjects(),
    fetchQuizzes()
  ])
  
  loading.value = false
}

onMounted(() => {
  initDashboard()
})
</script>

<template>
  <div class="dashboard-container">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading your dashboard...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="dashboard-content">
      <!-- Welcome Header -->
      <header class="dashboard-header">
        <div class="welcome-section">
          <h1 class="welcome-title">{{ welcomeMessage }}</h1>
          <p class="welcome-subtitle">Track your progress and continue learning</p>
        </div>
        <div class="date-section">
          <p class="current-date">{{ new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          }) }}</p>
        </div>
      </header>

      <!-- Stats Cards -->
      <section class="stats-section">
        <div class="stats-grid">
          <div class="stat-card total-quizzes">
            <div class="stat-icon">📚</div>
            <div class="stat-info">
              <h3>{{ userStats.totalQuizzes }}</h3>
              <p>Total Quizzes</p>
            </div>
          </div>
          
          <div class="stat-card completed-quizzes">
            <div class="stat-icon">✅</div>
            <div class="stat-info">
              <h3>{{ userStats.completedQuizzes }}</h3>
              <p>Completed</p>
            </div>
          </div>
          
          <div class="stat-card average-score">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <h3>{{ userStats.averageScore }}%</h3>
              <p>Average Score</p>
            </div>
          </div>
          
          <div class="stat-card total-subjects">
            <div class="stat-icon">📖</div>
            <div class="stat-info">
              <h3>{{ userStats.totalSubjects }}</h3>
              <p>Subjects Available</p>
            </div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="progress-section">
          <h3>Overall Progress</h3>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: completionPercentage + '%' }"
            ></div>
          </div>
          <p class="progress-text">{{ completionPercentage }}% Complete</p>
        </div>
      </section>

      <!-- Main Content Grid -->
      <div class="main-grid">
        <!-- Recent Scores -->
        <section class="recent-scores-section">
          <h2>Recent Quiz Results</h2>
          <div v-if="recentScores.length === 0" class="empty-state">
            <p>No quiz results yet. Start taking quizzes to see your progress!</p>
            <router-link to="/subjects" class="btn btn-primary">Browse Subjects</router-link>
          </div>
          <div v-else class="scores-list">
            <div 
              v-for="score in recentScores" 
              :key="score.id" 
              class="score-item"
            >
              <div class="score-info">
                <h4>{{ score.quiz_title || 'Quiz' }}</h4>
                <p class="score-subject">{{ score.subject_name }}</p>
              </div>
              <div class="score-result" :class="{ 'high-score': score.score >= 80, 'medium-score': score.score >= 60 }">
                {{ score.score }}%
              </div>
            </div>
          </div>
        </section>

        <!-- Available Subjects -->
        <section class="subjects-section">
          <h2>Available Subjects</h2>
          <div class="subjects-grid">
            <div 
              v-for="subject in availableSubjects" 
              :key="subject.id"
              class="subject-card"
              @click="$router.push(`/subjects/${subject.id}/chapters`)"
            >
              <div class="subject-icon">📚</div>
              <h3>{{ subject.name }}</h3>
              <p>{{ subject.description || 'Explore this subject' }}</p>
            </div>
          </div>
          <div class="view-all-section">
            <router-link to="/subjects" class="btn btn-secondary">View All Subjects</router-link>
          </div>
        </section>

        <!-- Available Quizzes -->
        <section class="quizzes-section">
          <h2>Available Quizzes</h2>
          <div v-if="recentQuizzes.length === 0" class="empty-state">
            <p>No quizzes available at the moment. Check back later!</p>
            <router-link to="/subjects" class="btn btn-primary">Browse Subjects</router-link>
          </div>
          <div v-else class="quizzes-list">
            <div 
              v-for="quiz in recentQuizzes" 
              :key="quiz.id" 
              class="quiz-card"
            >
              <div class="quiz-info">
                <h4>{{ quiz.title }}</h4>
                <p class="quiz-subject">{{ quiz.subject_name }} • {{ quiz.chapter_name }}</p>
                <div class="quiz-meta">
                  <span class="quiz-duration">⏱️ {{ quiz.time_duration }} min</span>
                  <span class="quiz-questions">📝 Questions available</span>
                </div>
                <p class="quiz-description">{{ quiz.description || 'Take this quiz to test your knowledge' }}</p>
              </div>
              <div class="quiz-actions">
                <button 
                  class="btn btn-primary btn-take-quiz"
                  @click="startQuiz(quiz.id)"
                >
                  Take Quiz
                </button>
              </div>
            </div>
          </div>
          <div class="view-all-section">
            <router-link to="/subjects" class="btn btn-secondary">Browse More Quizzes</router-link>
          </div>
        </section>

        <!-- Quick Actions -->
        <section class="quick-actions-section">
          <h2>Quick Actions</h2>
          <div class="actions-grid">
            <router-link to="/subjects" class="action-card">
              <div class="action-icon">🔍</div>
              <h3>Browse Subjects</h3>
              <p>Explore available subjects and topics</p>
            </router-link>
            
            <router-link to="/scores" class="action-card">
              <div class="action-icon">📊</div>
              <h3>View All Scores</h3>
              <p>See detailed performance analytics</p>
            </router-link>
            
            <router-link to="/profile" class="action-card">
              <div class="action-icon">👤</div>
              <h3>Update Profile</h3>
              <p>Manage your account settings</p>
            </router-link>
          </div>
        </section>

        <!-- Study Tips -->
        <section class="tips-section">
          <h2>Study Tips</h2>
          <div class="tips-container">
            <div class="tip-item">
              <span class="tip-icon">💡</span>
              <p>Take quizzes regularly to reinforce your learning</p>
            </div>
            <div class="tip-item">
              <span class="tip-icon">🎯</span>
              <p>Focus on subjects where your scores are below 70%</p>
            </div>
            <div class="tip-item">
              <span class="tip-icon">📝</span>
              <p>Review incorrect answers to understand concepts better</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.welcome-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.welcome-subtitle {
  color: #64748b;
  font-size: 1.1rem;
}

.current-date {
  color: #667eea;
  font-weight: 600;
  font-size: 1rem;
}

/* Stats Section */
.stats-section {
  margin-bottom: 3rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.stat-info p {
  color: #64748b;
  font-size: 0.9rem;
}

.total-quizzes { border-left: 4px solid #3b82f6; }
.completed-quizzes { border-left: 4px solid #10b981; }
.average-score { border-left: 4px solid #f59e0b; }
.total-subjects { border-left: 4px solid #8b5cf6; }

/* Progress Section */
.progress-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.progress-section h3 {
  color: #1e293b;
  margin-bottom: 1rem;
}

.progress-bar {
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.8s ease;
}

.progress-text {
  color: #64748b;
  font-size: 0.9rem;
  text-align: center;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

/* Sections */
.recent-scores-section,
.subjects-section,
.quizzes-section,
.quick-actions-section,
.tips-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.recent-scores-section h2,
.subjects-section h2,
.quizzes-section h2,
.quick-actions-section h2,
.tips-section h2 {
  color: #1e293b;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

/* Recent Scores */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.scores-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  transition: background 0.3s ease;
}

.score-item:hover {
  background: #f1f5f9;
}

.score-info h4 {
  color: #1e293b;
  margin-bottom: 0.25rem;
  font-size: 1rem;
}

.score-subject {
  color: #64748b;
  font-size: 0.85rem;
}

.score-result {
  font-weight: 700;
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  background: #ef4444;
  color: white;
}

.score-result.medium-score {
  background: #f59e0b;
}

.score-result.high-score {
  background: #10b981;
}

/* Subjects Grid */
.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.subject-card {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.subject-card:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.subject-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.subject-card h3 {
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.subject-card p {
  font-size: 0.8rem;
  opacity: 0.8;
}

.view-all-section {
  text-align: center;
}

/* Available Quizzes */
.quizzes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

.quiz-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  transition: all 0.3s ease;
}

.quiz-card:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.quiz-info {
  flex: 1;
}

.quiz-info h4 {
  color: #1e293b;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.quiz-subject {
  color: #667eea;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.quiz-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.quiz-duration,
.quiz-questions {
  color: #64748b;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.quiz-description {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.quiz-actions {
  margin-left: 1rem;
}

.btn-take-quiz {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.btn-take-quiz:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
}

/* Quick Actions */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.action-card {
  display: block;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
}

.action-card:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.action-card h3 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.action-card p {
  font-size: 0.85rem;
  opacity: 0.8;
}

/* Study Tips */
.tips-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.tip-icon {
  font-size: 1.2rem;
  margin-top: 0.1rem;
}

.tip-item p {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Buttons */
.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .main-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
}
</style>
