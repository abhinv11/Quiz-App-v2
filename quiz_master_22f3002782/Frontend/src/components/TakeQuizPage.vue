<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

// Get route params
const route = useRoute()
const router = useRouter()

// Reactive data
const loading = ref(true)
const quiz = ref(null)
const questions = ref([])
const userAnswers = ref({})
const currentQuestionIndex = ref(0)
const timeRemaining = ref(0)
const quizStarted = ref(false)
const submitting = ref(false)
const timer = ref(null)

// Get quiz and score IDs from URL
const quizId = route.params.quizId
const scoreId = route.query.score_id

// Computed properties
const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value] || null
})

const totalQuestions = computed(() => questions.value.length)

const answeredQuestions = computed(() => {
  return Object.keys(userAnswers.value).length
})

const progressPercentage = computed(() => {
  if (totalQuestions.value === 0) return 0
  return Math.round((answeredQuestions.value / totalQuestions.value) * 100)
})

const timeRemainingFormatted = computed(() => {
  const minutes = Math.floor(timeRemaining.value / 60)
  const seconds = timeRemaining.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const canSubmit = computed(() => {
  return answeredQuestions.value === totalQuestions.value
})

// Functions
const fetchQuizData = async () => {
  try {
    const token = localStorage.getItem('token')
    
    // Get quiz session data using the score_id
    const response = await axios.get(`http://127.0.0.1:5000/api/quiz-sessions/${scoreId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const sessionData = response.data
    quiz.value = {
      id: sessionData.quiz_id,
      title: sessionData.quiz_title,
      time_duration: sessionData.time_duration,
      subject_name: sessionData.subject_name,
      chapter_name: sessionData.chapter_name
    }
    questions.value = sessionData.questions || []
    timeRemaining.value = quiz.value.time_duration * 60 // Convert minutes to seconds
    quizStarted.value = true
    
    console.log('Quiz loaded:', quiz.value)
    console.log('Questions loaded:', questions.value.length)
    
    startTimer()
  } catch (error) {
    console.error('Error fetching quiz:', error)
    alert('Error loading quiz: ' + (error.response?.data?.message || error.message))
    router.push('/dashboard')
  }
}

const startTimer = () => {
  timer.value = setInterval(() => {
    if (timeRemaining.value > 0) {
      timeRemaining.value--
    } else {
      // Time's up, auto-submit
      submitQuiz(true)
    }
  }, 1000)
}

const stopTimer = () => {
  if (timer.value) {
    clearInterval(timer.value)
    timer.value = null
  }
}

const selectAnswer = (questionId, answer) => {
  userAnswers.value[questionId] = answer
}

const goToQuestion = (index) => {
  if (index >= 0 && index < totalQuestions.value) {
    currentQuestionIndex.value = index
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < totalQuestions.value - 1) {
    currentQuestionIndex.value++
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

const submitQuiz = async (autoSubmit = false) => {
  if (!canSubmit.value && !autoSubmit) {
    alert('Please answer all questions before submitting.')
    return
  }

  if (!autoSubmit && !confirm('Are you sure you want to submit your quiz? This action cannot be undone.')) {
    return
  }

  submitting.value = true
  stopTimer()

  try {
    const token = localStorage.getItem('token')
    const completionTime = (quiz.value.time_duration * 60) - timeRemaining.value

    // Prepare answers in the format expected by backend
    const answers = questions.value.map(question => ({
      question_id: question.id,
      user_answer: userAnswers.value[question.id] || ''
    }))

    const response = await axios.post(`http://127.0.0.1:5000/api/quizzes/${quizId}/submit`, {
      answers: answers,
      score_id: scoreId,
      completion_time: completionTime
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })

    // Navigate to results page
    router.push(`/quiz-results/${scoreId}`)
  } catch (error) {
    console.error('Error submitting quiz:', error)
    alert('Error submitting quiz: ' + (error.response?.data?.message || error.message))
    submitting.value = false
  }
}

// Initialize quiz
onMounted(async () => {
  if (!scoreId) {
    alert('Invalid quiz session. Please start the quiz again.')
    router.push('/dashboard')
    return
  }
  
  loading.value = true
  await fetchQuizData()
  loading.value = false
})

// Cleanup timer
onBeforeUnmount(() => {
  stopTimer()
})

// Prevent page refresh/navigation during quiz
window.addEventListener('beforeunload', (e) => {
  if (quizStarted.value && !submitting.value) {
    e.preventDefault()
    e.returnValue = 'You have an active quiz. Are you sure you want to leave?'
  }
})
</script>

<template>
  <div class="quiz-take-container">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading quiz...</p>
    </div>

    <!-- Quiz Interface -->
    <div v-else-if="quiz" class="quiz-interface">
      <!-- Quiz Header -->
      <header class="quiz-header">
        <div class="quiz-info">
          <h1>{{ quiz.title }}</h1>
          <p class="quiz-subject">{{ quiz.subject_name }} • {{ quiz.chapter_name }}</p>
        </div>
        <div class="quiz-timer" :class="{ 'timer-warning': timeRemaining < 300 }">
          <span class="timer-icon">⏰</span>
          <span class="timer-text">{{ timeRemainingFormatted }}</span>
        </div>
      </header>

      <!-- Progress Bar -->
      <div class="progress-section">
        <div class="progress-info">
          <span>Question {{ currentQuestionIndex + 1 }} of {{ totalQuestions }}</span>
          <span>{{ answeredQuestions }} / {{ totalQuestions }} answered</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: progressPercentage + '%' }"
          ></div>
        </div>
      </div>

      <!-- Question Navigation -->
      <div class="question-navigation">
        <div class="question-numbers">
          <button
            v-for="(question, index) in questions"
            :key="question.id"
            @click="goToQuestion(index)"
            :class="[
              'question-number-btn',
              { 'current': index === currentQuestionIndex },
              { 'answered': userAnswers[question.id] }
            ]"
          >
            {{ index + 1 }}
          </button>
        </div>
      </div>

      <!-- Current Question -->
      <div v-if="currentQuestion" class="question-section">
        <div class="question-content">
          <div class="question-header">
            <span class="question-type-badge">{{ currentQuestion.question_type }}</span>
            <span class="question-points">{{ currentQuestion.points }} point{{ currentQuestion.points !== 1 ? 's' : '' }}</span>
          </div>
          
          <h2 class="question-statement">{{ currentQuestion.question_statement }}</h2>
          
          <!-- MCQ Options -->
          <div v-if="currentQuestion.question_type === 'multiple_choice'" class="mcq-options">
            <div 
              v-for="(option, index) in currentQuestion.options"
              :key="index"
              class="mcq-option"
              @click="selectAnswer(currentQuestion.id, option)"
            >
              <input 
                type="radio" 
                :name="`question-${currentQuestion.id}`"
                :value="option"
                :checked="userAnswers[currentQuestion.id] === option"
                readonly
              >
              <label>
                <span class="option-letter">{{ String.fromCharCode(65 + index) }}.</span>
                <span class="option-text">{{ option }}</span>
              </label>
            </div>
          </div>

          <!-- True/False Options -->
          <div v-else-if="currentQuestion.question_type === 'true_false'" class="true-false-options">
            <div class="tf-option" @click="selectAnswer(currentQuestion.id, 'True')">
              <input 
                type="radio" 
                :name="`question-${currentQuestion.id}`"
                value="True"
                :checked="userAnswers[currentQuestion.id] === 'True'"
                readonly
              >
              <label>True</label>
            </div>
            <div class="tf-option" @click="selectAnswer(currentQuestion.id, 'False')">
              <input 
                type="radio" 
                :name="`question-${currentQuestion.id}`"
                value="False"
                :checked="userAnswers[currentQuestion.id] === 'False'"
                readonly
              >
              <label>False</label>
            </div>
          </div>

          <!-- Short Answer -->
          <div v-else-if="currentQuestion.question_type === 'short_answer'" class="short-answer">
            <textarea
              v-model="userAnswers[currentQuestion.id]"
              placeholder="Enter your answer here..."
              class="answer-textarea"
              rows="4"
            ></textarea>
          </div>

          <!-- Fill in the Blank -->
          <div v-else-if="currentQuestion.question_type === 'fill_blank'" class="fill-blank">
            <input
              type="text"
              v-model="userAnswers[currentQuestion.id]"
              placeholder="Fill in the blank..."
              class="answer-input"
            />
          </div>
        </div>
      </div>

      <!-- Navigation Controls -->
      <div class="quiz-controls">
        <div class="navigation-controls">
          <button 
            @click="previousQuestion" 
            :disabled="currentQuestionIndex === 0"
            class="btn btn-secondary"
          >
            ← Previous
          </button>
          
          <button 
            @click="nextQuestion" 
            :disabled="currentQuestionIndex === totalQuestions - 1"
            class="btn btn-secondary"
          >
            Next →
          </button>
        </div>

        <div class="submit-controls">
          <div class="completion-status">
            <span v-if="!canSubmit" class="incomplete-warning">
              ⚠️ {{ totalQuestions - answeredQuestions }} question{{ totalQuestions - answeredQuestions !== 1 ? 's' : '' }} remaining
            </span>
            <span v-else class="complete-status">
              ✅ All questions answered
            </span>
          </div>
          
          <button 
            @click="submitQuiz()" 
            :disabled="submitting"
            :class="['btn', 'btn-submit', { 'btn-ready': canSubmit }]"
          >
            {{ submitting ? 'Submitting...' : 'Submit Quiz' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.quiz-take-container {
  min-height: 100vh;
  background: #f8fafc;
  padding: 1rem;
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

.quiz-interface {
  max-width: 900px;
  margin: 0 auto;
}

/* Quiz Header */
.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem;
}

.quiz-info h1 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
  font-size: 1.8rem;
}

.quiz-subject {
  color: #667eea;
  font-weight: 500;
}

.quiz-timer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f1f5f9;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
}

.timer-warning {
  background: #fef3c7;
  color: #92400e;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Progress Section */
.progress-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: #64748b;
  font-weight: 500;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  transition: width 0.3s ease;
}

/* Question Navigation */
.question-navigation {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem;
}

.question-numbers {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.question-number-btn {
  width: 40px;
  height: 40px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.question-number-btn:hover {
  border-color: #667eea;
  background: #f1f5f9;
}

.question-number-btn.current {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.question-number-btn.answered {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.question-number-btn.answered.current {
  background: #059669;
  border-color: #059669;
}

/* Question Section */
.question-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.question-type-badge {
  background: #667eea;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.question-points {
  background: #f1f5f9;
  color: #64748b;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
}

.question-statement {
  color: #1e293b;
  font-size: 1.3rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

/* MCQ Options */
.mcq-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.mcq-option {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mcq-option:hover {
  border-color: #667eea;
  background: #f8fafc;
}

.mcq-option:has(input:checked) {
  border-color: #667eea;
  background: #f1f5f9;
}

.mcq-option input[type="radio"] {
  margin-right: 1rem;
  transform: scale(1.2);
}

.mcq-option label {
  display: flex;
  align-items: center;
  cursor: pointer;
  width: 100%;
}

.option-letter {
  font-weight: 600;
  color: #667eea;
  margin-right: 1rem;
  min-width: 25px;
}

.option-text {
  flex: 1;
}

/* True/False Options */
.true-false-options {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.tf-option {
  display: flex;
  align-items: center;
  padding: 1.5rem 2rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
  justify-content: center;
}

.tf-option:hover {
  border-color: #667eea;
  background: #f8fafc;
}

.tf-option:has(input:checked) {
  border-color: #667eea;
  background: #f1f5f9;
}

.tf-option input[type="radio"] {
  margin-right: 0.5rem;
  transform: scale(1.2);
}

.tf-option label {
  font-weight: 600;
  cursor: pointer;
}

/* Short Answer */
.short-answer {
  width: 100%;
}

.answer-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.answer-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Fill in the Blank */
.fill-blank {
  width: 100%;
}

.answer-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.5;
  transition: border-color 0.3s ease;
}

.answer-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Quiz Controls */
.quiz-controls {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navigation-controls {
  display: flex;
  gap: 1rem;
}

.submit-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.completion-status {
  font-weight: 500;
}

.incomplete-warning {
  color: #f59e0b;
}

.complete-status {
  color: #10b981;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  color: #64748b;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-submit {
  background: #64748b;
  color: white;
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

.btn-submit.btn-ready {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
  .quiz-take-container {
    padding: 0.5rem;
  }
  
  .quiz-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .quiz-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .navigation-controls {
    justify-content: space-between;
    width: 100%;
  }
  
  .submit-controls {
    flex-direction: column;
    text-align: center;
  }
  
  .true-false-options {
    flex-direction: column;
    gap: 1rem;
  }
  
  .question-numbers {
    justify-content: center;
  }
}
</style>
