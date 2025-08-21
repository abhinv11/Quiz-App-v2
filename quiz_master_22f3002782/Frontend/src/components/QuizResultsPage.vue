<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

// Get route params
const route = useRoute()
const router = useRouter()

// Reactive data
const loading = ref(true)
const result = ref(null)
const quiz = ref(null)
const userAnswers = ref([])
const showDetailedResults = ref(false)

// Get score ID from URL
const scoreId = route.params.scoreId

// Computed properties
const scorePercentage = computed(() => {
  if (!result.value) return 0
  return Math.round((result.value.total_scored / result.value.total_possible) * 100)
})

const scoreGrade = computed(() => {
  const percentage = scorePercentage.value
  if (percentage >= 90) return 'A+'
  if (percentage >= 80) return 'A'
  if (percentage >= 70) return 'B'
  if (percentage >= 60) return 'C'
  if (percentage >= 50) return 'D'
  return 'F'
})

const scoreColor = computed(() => {
  const percentage = scorePercentage.value
  if (percentage >= 80) return '#10b981' // Green
  if (percentage >= 60) return '#f59e0b' // Yellow
  return '#ef4444' // Red
})

const completionTimeFormatted = computed(() => {
  if (!result.value) return '0:00'
  const minutes = Math.floor(result.value.completion_time / 60)
  const seconds = result.value.completion_time % 60
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

const correctAnswers = computed(() => {
  return userAnswers.value.filter(answer => answer.is_correct).length
})

const incorrectAnswers = computed(() => {
  return userAnswers.value.filter(answer => !answer.is_correct).length
})

// Functions
const fetchQuizResult = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://127.0.0.1:5000/api/scores/${scoreId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    result.value = response.data.score
    userAnswers.value = response.data.score.user_answers || []
    
    // Create quiz object from score data
    quiz.value = {
      id: response.data.score.quiz_id,
      title: response.data.score.quiz_title,
      subject_name: response.data.score.subject_name || 'Subject',
      chapter_name: response.data.score.chapter_name || 'Chapter'
    }
    
    console.log('Quiz result loaded:', result.value)
    console.log('User answers:', userAnswers.value)
  } catch (error) {
    console.error('Error fetching quiz result:', error)
    alert('Error loading quiz result: ' + (error.response?.data?.message || error.message))
    router.push('/dashboard')
  }
}

const retakeQuiz = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(`http://127.0.0.1:5000/api/quizzes/${quiz.value.id}/start`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Navigate to quiz taking page with new score ID
    router.push(`/take-quiz/${quiz.value.id}?score_id=${response.data.score_id}`)
  } catch (error) {
    console.error('Error starting quiz:', error)
    alert('Error starting quiz: ' + (error.response?.data?.message || error.message))
  }
}

const goToDashboard = () => {
  router.push('/dashboard')
}

const viewAllScores = () => {
  router.push('/scores')
}

// Initialize
onMounted(async () => {
  if (!scoreId) {
    alert('Invalid score ID')
    router.push('/dashboard')
    return
  }
  
  loading.value = true
  await fetchQuizResult()
  loading.value = false
})
</script>

<template>
  <div class="quiz-results-container">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading your results...</p>
    </div>

    <!-- Results Display -->
    <div v-else-if="result && quiz" class="results-content">
      <!-- Results Header -->
      <header class="results-header">
        <div class="quiz-info">
          <h1>{{ quiz.title }}</h1>
          <p class="quiz-subject">{{ quiz.subject_name }} • {{ quiz.chapter_name }}</p>
          <p class="completion-time">Completed in {{ completionTimeFormatted }}</p>
        </div>
        
        <!-- Score Display -->
        <div class="score-display" :style="{ borderColor: scoreColor }">
          <div class="score-circle" :style="{ backgroundColor: scoreColor }">
            <span class="score-percentage">{{ scorePercentage }}%</span>
            <span class="score-grade">{{ scoreGrade }}</span>
          </div>
          <div class="score-details">
            <p>{{ result.total_scored }} / {{ result.total_possible }} points</p>
            <p>{{ correctAnswers }} correct • {{ incorrectAnswers }} incorrect</p>
          </div>
        </div>
      </header>

      <!-- Performance Summary -->
      <section class="performance-summary">
        <h2>Performance Summary</h2>
        <div class="summary-grid">
          <div class="summary-card correct">
            <div class="summary-icon">✅</div>
            <div class="summary-info">
              <h3>{{ correctAnswers }}</h3>
              <p>Correct Answers</p>
            </div>
          </div>
          
          <div class="summary-card incorrect">
            <div class="summary-icon">❌</div>
            <div class="summary-info">
              <h3>{{ incorrectAnswers }}</h3>
              <p>Incorrect Answers</p>
            </div>
          </div>
          
          <div class="summary-card score">
            <div class="summary-icon">🎯</div>
            <div class="summary-info">
              <h3>{{ scorePercentage }}%</h3>
              <p>Final Score</p>
            </div>
          </div>
          
          <div class="summary-card time">
            <div class="summary-icon">⏱️</div>
            <div class="summary-info">
              <h3>{{ completionTimeFormatted }}</h3>
              <p>Time Taken</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Motivational Message -->
      <section class="motivation-section">
        <div class="motivation-card" :class="{ 'excellent': scorePercentage >= 80, 'good': scorePercentage >= 60, 'needs-improvement': scorePercentage < 60 }">
          <div v-if="scorePercentage >= 90" class="motivation-content">
            <h3>🌟 Outstanding Performance!</h3>
            <p>Excellent work! You've demonstrated exceptional understanding of the material. Keep up the amazing effort!</p>
          </div>
          <div v-else-if="scorePercentage >= 80" class="motivation-content">
            <h3>🎉 Great Job!</h3>
            <p>Well done! You have a solid grasp of the concepts. With a little more practice, you'll be perfect!</p>
          </div>
          <div v-else-if="scorePercentage >= 60" class="motivation-content">
            <h3>👍 Good Effort!</h3>
            <p>You're on the right track! Review the areas you missed and try again to improve your understanding.</p>
          </div>
          <div v-else class="motivation-content">
            <h3>💪 Keep Learning!</h3>
            <p>Don't worry! Learning is a process. Review the material, practice more, and you'll see improvement.</p>
          </div>
        </div>
      </section>

      <!-- Detailed Results Toggle -->
      <section class="detailed-results-section">
        <div class="section-header">
          <h2>Question Review</h2>
          <button 
            @click="showDetailedResults = !showDetailedResults"
            class="btn btn-secondary"
          >
            {{ showDetailedResults ? 'Hide Details' : 'Show Details' }}
          </button>
        </div>

        <!-- Detailed Results -->
        <div v-if="showDetailedResults" class="detailed-results">
          <div 
            v-for="(answer, index) in userAnswers" 
            :key="answer.question_id"
            class="question-review"
            :class="{ 'correct': answer.is_correct, 'incorrect': !answer.is_correct }"
          >
            <div class="question-header">
              <span class="question-number">Question {{ index + 1 }}</span>
              <span class="question-status" :class="{ 'correct': answer.is_correct, 'incorrect': !answer.is_correct }">
                {{ answer.is_correct ? '✅ Correct' : '❌ Incorrect' }}
              </span>
              <span class="question-points">{{ answer.points_earned }} / {{ answer.question.points }} pts</span>
            </div>
            
            <div class="question-content">
              <h4>{{ answer.question.question_statement }}</h4>
              
              <div class="answer-comparison">
                <div class="user-answer">
                  <strong>Your Answer:</strong>
                  <span :class="{ 'correct-answer': answer.is_correct, 'incorrect-answer': !answer.is_correct }">
                    {{ answer.user_answer || 'No answer provided' }}
                  </span>
                </div>
                
                <div v-if="!answer.is_correct" class="correct-answer-display">
                  <strong>Correct Answer:</strong>
                  <span class="correct-answer">{{ answer.question.correct_answer }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Action Buttons -->
      <section class="action-section">
        <div class="action-buttons">
          <button @click="retakeQuiz" class="btn btn-primary">
            🔄 Retake Quiz
          </button>
          
          <button @click="viewAllScores" class="btn btn-secondary">
            📊 View All Scores
          </button>
          
          <button @click="goToDashboard" class="btn btn-secondary">
            🏠 Back to Dashboard
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.quiz-results-container {
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

.results-content {
  max-width: 900px;
  margin: 0 auto;
}

/* Results Header */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.quiz-info h1 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
  font-size: 1.8rem;
}

.quiz-subject {
  color: #667eea;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.completion-time {
  color: #64748b;
  font-size: 0.9rem;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border: 3px solid;
  border-radius: 12px;
  padding: 1.5rem;
  background: #f8fafc;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
}

.score-percentage {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.score-grade {
  font-size: 1.2rem;
  font-weight: 600;
  opacity: 0.9;
}

.score-details {
  text-align: center;
}

.score-details p {
  margin: 0.25rem 0;
  color: #64748b;
  font-weight: 500;
}

/* Performance Summary */
.performance-summary {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.performance-summary h2 {
  color: #1e293b;
  margin-bottom: 1.5rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.summary-card.correct {
  background: #ecfdf5;
  border-left-color: #10b981;
}

.summary-card.incorrect {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.summary-card.score {
  background: #eff6ff;
  border-left-color: #3b82f6;
}

.summary-card.time {
  background: #f3e8ff;
  border-left-color: #8b5cf6;
}

.summary-icon {
  font-size: 2rem;
}

.summary-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  color: #1e293b;
}

.summary-info p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

/* Motivation Section */
.motivation-section {
  margin-bottom: 2rem;
}

.motivation-card {
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  border-left: 4px solid;
}

.motivation-card.excellent {
  background: #ecfdf5;
  border-left-color: #10b981;
}

.motivation-card.good {
  background: #fffbeb;
  border-left-color: #f59e0b;
}

.motivation-card.needs-improvement {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.motivation-content h3 {
  margin: 0 0 1rem 0;
  color: #1e293b;
  font-size: 1.3rem;
}

.motivation-content p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
}

/* Detailed Results */
.detailed-results-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  color: #1e293b;
  margin: 0;
}

.detailed-results {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.question-review {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.question-review.correct {
  border-color: #10b981;
  background: #f0fdf4;
}

.question-review.incorrect {
  border-color: #ef4444;
  background: #fef2f2;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.question-number {
  font-weight: 600;
  color: #1e293b;
}

.question-status.correct {
  color: #059669;
  font-weight: 600;
}

.question-status.incorrect {
  color: #dc2626;
  font-weight: 600;
}

.question-points {
  background: #f1f5f9;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #64748b;
}

.question-content h4 {
  color: #1e293b;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.answer-comparison {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-answer,
.correct-answer-display {
  padding: 0.75rem;
  border-radius: 6px;
  background: #f8fafc;
}

.user-answer strong,
.correct-answer-display strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
}

.correct-answer {
  color: #059669;
  font-weight: 600;
}

.incorrect-answer {
  color: #dc2626;
  font-weight: 600;
}

/* Action Section */
.action-section {
  text-align: center;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
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
  background: #f1f5f9;
  color: #64748b;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #e2e8f0;
  color: #475569;
}

/* Responsive Design */
@media (max-width: 768px) {
  .quiz-results-container {
    padding: 1rem;
  }
  
  .results-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .score-display {
    flex-direction: column;
    text-align: center;
  }
  
  .summary-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .question-header {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
}
</style>
