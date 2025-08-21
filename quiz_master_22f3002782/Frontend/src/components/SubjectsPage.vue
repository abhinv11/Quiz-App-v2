<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const subjects = ref([])
const loading = ref(true)
const selectedSubject = ref(null)
const chapters = ref([])
const quizzes = ref([])
const loadingChapters = ref(false)
const loadingQuizzes = ref(false)

// Fetch all subjects
const fetchSubjects = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://127.0.0.1:5000/api/subjects', {
      headers: { Authorization: `Bearer ${token}` }
    })
    subjects.value = response.data.subjects
  } catch (error) {
    console.error('Error fetching subjects:', error)
    alert('Error loading subjects: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// Fetch chapters for a subject
const fetchChapters = async (subjectId) => {
  try {
    loadingChapters.value = true
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://127.0.0.1:5000/api/subjects/${subjectId}/chapters`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    chapters.value = response.data.chapters
  } catch (error) {
    console.error('Error fetching chapters:', error)
    alert('Error loading chapters: ' + (error.response?.data?.message || error.message))
  } finally {
    loadingChapters.value = false
  }
}

// Fetch quizzes for a chapter
const fetchQuizzes = async (chapterId) => {
  try {
    loadingQuizzes.value = true
    const token = localStorage.getItem('token')
    const response = await axios.get(`http://127.0.0.1:5000/api/chapters/${chapterId}/quizzes`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    quizzes.value = response.data.quizzes
  } catch (error) {
    console.error('Error fetching quizzes:', error)
    alert('Error loading quizzes: ' + (error.response?.data?.message || error.message))
  } finally {
    loadingQuizzes.value = false
  }
}

// Select a subject
const selectSubject = async (subject) => {
  selectedSubject.value = subject
  chapters.value = []
  quizzes.value = []
  await fetchChapters(subject.id)
}

// Start a quiz
const startQuiz = async (quizId) => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(`http://127.0.0.1:5000/api/quizzes/${quizId}/start`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    // Navigate to quiz taking page
    router.push(`/take-quiz/${quizId}?score_id=${response.data.score_id}`)
  } catch (error) {
    console.error('Error starting quiz:', error)
    alert('Error starting quiz: ' + (error.response?.data?.message || error.message))
  }
}

// Go back to subjects
const goBackToSubjects = () => {
  selectedSubject.value = null
  chapters.value = []
  quizzes.value = []
}

onMounted(() => {
  fetchSubjects()
})
</script>

<template>
  <div class="subjects-container">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading subjects...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="subjects-content">
      <!-- Header -->
      <header class="subjects-header">
        <div class="header-content">
          <h1 v-if="!selectedSubject">Browse Subjects</h1>
          <div v-else class="breadcrumb">
            <button @click="goBackToSubjects" class="breadcrumb-btn">
              ← Subjects
            </button>
            <span class="breadcrumb-separator">/</span>
            <span class="current-subject">{{ selectedSubject.name }}</span>
          </div>
          <p v-if="!selectedSubject">Explore available subjects and take quizzes to test your knowledge</p>
          <p v-else>{{ selectedSubject.description || 'Choose a chapter to see available quizzes' }}</p>
        </div>
      </header>

      <!-- Subjects Grid -->
      <section v-if="!selectedSubject" class="subjects-section">
        <div v-if="subjects.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <h3>No Subjects Available</h3>
          <p>No subjects have been created yet. Please check back later or contact your administrator.</p>
        </div>
        
        <div v-else class="subjects-grid">
          <div 
            v-for="subject in subjects" 
            :key="subject.id"
            class="subject-card"
            @click="selectSubject(subject)"
          >
            <div class="subject-content">
              <div class="subject-icon">📖</div>
              <h3>{{ subject.name }}</h3>
              <p>{{ subject.description || 'Explore this subject to find chapters and quizzes' }}</p>
              <div class="subject-action">
                <span class="action-text">Click to explore →</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Subject Details -->
      <section v-if="selectedSubject" class="subject-details">
        <!-- Chapters Section -->
        <div class="chapters-section">
          <h2>Chapters</h2>
          
          <!-- Loading Chapters -->
          <div v-if="loadingChapters" class="loading-small">
            <div class="loading-spinner-small"></div>
            <span>Loading chapters...</span>
          </div>
          
          <!-- No Chapters -->
          <div v-else-if="chapters.length === 0" class="empty-state-small">
            <p>No chapters available for this subject.</p>
          </div>
          
          <!-- Chapters List -->
          <div v-else class="chapters-grid">
            <div 
              v-for="chapter in chapters" 
              :key="chapter.id"
              class="chapter-card"
              @click="fetchQuizzes(chapter.id)"
            >
              <div class="chapter-content">
                <h4>{{ chapter.name }}</h4>
                <p>{{ chapter.description || 'Click to see available quizzes' }}</p>
                <div class="chapter-action">
                  <span class="action-text">View Quizzes →</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quizzes Section -->
        <div v-if="quizzes.length > 0 || loadingQuizzes" class="quizzes-section">
          <h2>Available Quizzes</h2>
          
          <!-- Loading Quizzes -->
          <div v-if="loadingQuizzes" class="loading-small">
            <div class="loading-spinner-small"></div>
            <span>Loading quizzes...</span>
          </div>
          
          <!-- Quizzes List -->
          <div v-else class="quizzes-list">
            <div 
              v-for="quiz in quizzes" 
              :key="quiz.id"
              class="quiz-card"
            >
              <div class="quiz-content">
                <div class="quiz-info">
                  <h4>{{ quiz.title }}</h4>
                  <p>{{ quiz.description || 'Test your knowledge with this quiz' }}</p>
                  <div class="quiz-meta">
                    <span class="quiz-duration">⏱️ {{ quiz.time_duration }} minutes</span>
                    <span class="quiz-date">📅 {{ new Date(quiz.date_of_quiz).toLocaleDateString() }}</span>
                  </div>
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
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.subjects-container {
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

.subjects-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.subjects-header {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.header-content p {
  color: #64748b;
  font-size: 1.1rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.breadcrumb-btn {
  background: none;
  border: none;
  color: #667eea;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.breadcrumb-btn:hover {
  background: #f1f5f9;
}

.breadcrumb-separator {
  color: #94a3b8;
}

.current-subject {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
}

/* Subjects Grid */
.subjects-section {
  margin-bottom: 2rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #64748b;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.subject-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  cursor: pointer;
}

.subject-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.subject-content {
  padding: 2rem;
}

.subject-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.subject-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.75rem;
}

.subject-card p {
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.subject-action {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.action-text {
  color: #667eea;
  font-weight: 500;
  font-size: 0.9rem;
}

/* Subject Details */
.subject-details {
  display: grid;
  gap: 2rem;
}

.chapters-section,
.quizzes-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.chapters-section h2,
.quizzes-section h2 {
  color: #1e293b;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.loading-small {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #64748b;
}

.loading-spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-state-small {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

/* Chapters Grid */
.chapters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.chapter-card {
  background: #f8fafc;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.chapter-card:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.chapter-content {
  padding: 1.5rem;
}

.chapter-card h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.chapter-card p {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 1rem;
}

.chapter-action {
  border-top: 1px solid rgba(255,255,255,0.2);
  padding-top: 0.75rem;
}

/* Quizzes List */
.quizzes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.quiz-card {
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

.quiz-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
}

.quiz-info {
  flex: 1;
}

.quiz-info h4 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.quiz-info p {
  color: #64748b;
  margin-bottom: 0.75rem;
}

.quiz-meta {
  display: flex;
  gap: 1.5rem;
}

.quiz-duration,
.quiz-date {
  color: #64748b;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.quiz-actions {
  margin-left: 1rem;
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
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
}

.btn-take-quiz {
  font-size: 0.9rem;
  padding: 0.75rem 1.25rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .subjects-container {
    padding: 1rem;
  }
  
  .subjects-grid {
    grid-template-columns: 1fr;
  }
  
  .chapters-grid {
    grid-template-columns: 1fr;
  }
  
  .quiz-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .quiz-actions {
    margin-left: 0;
    align-self: stretch;
  }
  
  .btn-take-quiz {
    width: 100%;
  }
}
</style>
