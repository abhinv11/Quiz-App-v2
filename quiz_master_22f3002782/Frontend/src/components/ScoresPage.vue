<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const scores = ref([])
const loading = ref(true)
const error = ref('')
const sortBy = ref('date')
const sortOrder = ref('desc')

// Computed properties
const sortedScores = computed(() => {
  const sorted = [...scores.value].sort((a, b) => {
    let aVal, bVal
    
    switch (sortBy.value) {
      case 'date':
        aVal = new Date(a.timestamp)
        bVal = new Date(b.timestamp)
        break
      case 'score':
        aVal = a.score_percentage
        bVal = b.score_percentage
        break
      case 'quiz':
        aVal = a.quiz_title
        bVal = b.quiz_title
        break
      case 'subject':
        aVal = a.subject_name
        bVal = b.subject_name
        break
      default:
        aVal = a.timestamp
        bVal = b.timestamp
    }
    
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }
    
    if (sortOrder.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
  
  return sorted
})

const averageScore = computed(() => {
  if (scores.value.length === 0) return 0
  const total = scores.value.reduce((sum, score) => sum + score.score_percentage, 0)
  return Math.round(total / scores.value.length)
})

const totalQuizzesTaken = computed(() => scores.value.length)

const bestScore = computed(() => {
  if (scores.value.length === 0) return 0
  return Math.max(...scores.value.map(s => s.score_percentage))
})

// Fetch user's quiz scores
const fetchScores = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('token')
    const response = await axios.get('http://127.0.0.1:5000/api/users/me/scores', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Transform the data to match our expected format
    scores.value = response.data.scores.map(score => ({
      id: score.id,
      quiz_title: score.quiz_title,
      subject_name: score.subject_name,
      score_percentage: Math.round((score.total_scored / score.total_possible) * 100),
      score_value: score.total_scored,
      total_questions: score.total_possible,
      timestamp: score.time_stamp_of_attempt
    }))
  } catch (error) {
    console.error('Error fetching scores:', error)
    error.value = 'Error loading your quiz scores: ' + (error.response?.data?.message || error.message)
  } finally {
    loading.value = false
  }
}

// View detailed results
const viewResults = (scoreId) => {
  router.push(`/quiz-results/${scoreId}`)
}

// Format date
const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Get score color based on percentage
const getScoreColor = (percentage) => {
  if (percentage >= 90) return 'text-green-600'
  if (percentage >= 70) return 'text-blue-600'
  if (percentage >= 50) return 'text-yellow-600'
  return 'text-red-600'
}

// Get grade based on percentage
const getGrade = (percentage) => {
  if (percentage >= 90) return 'A'
  if (percentage >= 80) return 'B'
  if (percentage >= 70) return 'C'
  if (percentage >= 60) return 'D'
  return 'F'
}

// Change sort
const changeSort = (field) => {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortOrder.value = 'desc'
  }
}

onMounted(() => {
  fetchScores()
})
</script>

<template>
  <div class="scores-container">
    <div class="scores-header">
      <h1 class="page-title">My Quiz Scores</h1>
      <p class="page-subtitle">Track your progress and performance across all quizzes</p>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading your scores...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchScores" class="retry-btn">Try Again</button>
    </div>

    <!-- Scores content -->
    <div v-else-if="scores.length > 0" class="scores-content">
      <!-- Statistics Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <h3>{{ averageScore }}%</h3>
            <p>Average Score</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-info">
            <h3>{{ bestScore }}%</h3>
            <p>Best Score</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-info">
            <h3>{{ totalQuizzesTaken }}</h3>
            <p>Quizzes Taken</p>
          </div>
        </div>
      </div>

      <!-- Sort Controls -->
      <div class="sort-controls">
        <label>Sort by:</label>
        <select v-model="sortBy" @change="sortOrder = 'desc'">
          <option value="date">Date</option>
          <option value="score">Score</option>
          <option value="quiz">Quiz Name</option>
          <option value="subject">Subject</option>
        </select>
        <button @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'" class="sort-order-btn">
          {{ sortOrder === 'asc' ? '↑' : '↓' }}
        </button>
      </div>

      <!-- Scores Table -->
      <div class="scores-table-container">
        <table class="scores-table">
          <thead>
            <tr>
              <th @click="changeSort('quiz')" class="sortable">
                Quiz Name
                <span v-if="sortBy === 'quiz'" class="sort-indicator">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click="changeSort('subject')" class="sortable">
                Subject
                <span v-if="sortBy === 'subject'" class="sort-indicator">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click="changeSort('score')" class="sortable">
                Score
                <span v-if="sortBy === 'score'" class="sort-indicator">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>Grade</th>
              <th @click="changeSort('date')" class="sortable">
                Date
                <span v-if="sortBy === 'date'" class="sort-indicator">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="score in sortedScores" :key="score.id" class="score-row">
              <td class="quiz-title">{{ score.quiz_title }}</td>
              <td class="subject-name">{{ score.subject_name }}</td>
              <td class="score-percentage" :class="getScoreColor(score.score_percentage)">
                {{ score.score_percentage }}%
                <span class="score-fraction">({{ score.score_value }}/{{ score.total_questions }})</span>
              </td>
              <td class="grade" :class="getScoreColor(score.score_percentage)">
                {{ getGrade(score.score_percentage) }}
              </td>
              <td class="date">{{ formatDate(score.timestamp) }}</td>
              <td class="actions">
                <button @click="viewResults(score.id)" class="view-btn">
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <div class="empty-icon">📊</div>
      <h3>No Quiz Scores Yet</h3>
      <p>You haven't taken any quizzes yet. Start taking quizzes to see your scores here!</p>
      <router-link to="/subjects" class="start-quiz-btn">
        Browse Subjects
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.scores-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.scores-header {
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
  text-align: center;
  padding: 3rem;
  color: #ef4444;
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

.sort-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.sort-controls label {
  font-weight: 500;
  color: #374151;
}

.sort-controls select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
}

.sort-order-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.sort-order-btn:hover {
  background: #5a67d8;
}

.scores-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
}

.scores-table {
  width: 100%;
  border-collapse: collapse;
}

.scores-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.scores-table th.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.scores-table th.sortable:hover {
  background: #f1f5f9;
}

.sort-indicator {
  margin-left: 0.5rem;
  color: #667eea;
  font-weight: bold;
}

.scores-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.score-row:hover {
  background: #f8fafc;
}

.quiz-title {
  font-weight: 600;
  color: #1f2937;
}

.subject-name {
  color: #64748b;
  font-size: 0.9rem;
}

.score-percentage {
  font-weight: 700;
  font-size: 1.1rem;
}

.score-fraction {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 400;
  margin-left: 0.5rem;
}

.grade {
  font-weight: 700;
  font-size: 1.2rem;
}

.date {
  color: #64748b;
  font-size: 0.9rem;
}

.view-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s ease;
}

.view-btn:hover {
  background: #5a67d8;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
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
  margin-bottom: 2rem;
}

.start-quiz-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-weight: 600;
  display: inline-block;
  transition: transform 0.3s ease;
}

.start-quiz-btn:hover {
  transform: translateY(-2px);
}

.text-green-600 { color: #059669; }
.text-blue-600 { color: #2563eb; }
.text-yellow-600 { color: #d97706; }
.text-red-600 { color: #dc2626; }

/* Responsive design */
@media (max-width: 768px) {
  .scores-container {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .scores-table-container {
    overflow-x: auto;
  }
  
  .scores-table {
    min-width: 600px;
  }
  
  .sort-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
