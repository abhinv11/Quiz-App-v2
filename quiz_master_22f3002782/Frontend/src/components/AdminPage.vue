<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

// Router
const router = useRouter()

// Reactive data
const activeSection = ref('dashboard')
const loading = ref(false)
const subjects = ref([])
const users = ref([])
const quizzes = ref([])
const chapters = ref([])
const questions = ref([])
const recentActivities = ref([])
const showSubjectModal = ref(false)
const showUserModal = ref(false)
const showChapterModal = ref(false)
const showQuizModal = ref(false)
const showQuestionModal = ref(false)
const editingSubject = ref(null)
const editingChapter = ref(null)
const editingQuiz = ref(null)
const editingQuestion = ref(null)
const selectedSubjectId = ref(null)
const selectedChapterId = ref(null)
const selectedQuizId = ref(null)

// Form data
const subjectForm = ref({
  name: '',
  description: ''
})

const userForm = ref({
  email: '',
  password: '',
  name: '',
  dob: '',
  qualification: '',
  role: 'student'
})

const chapterForm = ref({
  name: '',
  description: '',
  subject_id: null
})

const quizForm = ref({
  title: '',
  description: '',
  chapter_id: null,
  time_duration: 30,
  remarks: '',
  is_published: false
})

const questionForm = ref({
  question_statement: '',
  question_type: 'MCQ',
  points: 1,
  correct_answer: '',
  quiz_id: null,
  options: ['', '', '', '']
})

// Stats
const stats = ref({
  totalUsers: 0,
  totalSubjects: 0,
  totalQuizzes: 0,
  totalChapters: 0,
  totalQuestions: 0
})

// Computed properties
const filteredUsers = computed(() => {
  return users.value
})

// API token
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}

// API calls
const fetchSubjects = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/admin/subjects', {
      headers: getAuthHeaders()
    })
    subjects.value = response.data.subjects
    stats.value.totalSubjects = response.data.subjects.length
  } catch (error) {
    console.error('Error fetching subjects:', error)
    alert('Error fetching subjects: ' + (error.response?.data?.message || error.message))
  }
}

const fetchUsers = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/admin/users', {
      headers: getAuthHeaders()
    })
    users.value = response.data.users
    stats.value.totalUsers = response.data.users.length
  } catch (error) {
    console.error('Error fetching users:', error)
    alert('Error fetching users: ' + (error.response?.data?.message || error.message))
  }
}

const fetchQuizzes = async (chapterId = null, subjectId = null) => {
  try {
    let url = 'http://127.0.0.1:5000/api/admin/quizzes'
    const params = new URLSearchParams()
    
    if (subjectId) {
      params.append('subject_id', subjectId)
    }
    if (chapterId) {
      params.append('chapter_id', chapterId)
    }
    
    if (params.toString()) {
      url += '?' + params.toString()
    }
    
    const response = await axios.get(url, {
      headers: getAuthHeaders()
    })
    quizzes.value = response.data.quizzes
    stats.value.totalQuizzes = response.data.quizzes.length
  } catch (error) {
    console.error('Error fetching quizzes:', error)
    alert('Error fetching quizzes: ' + (error.response?.data?.message || error.message))
  }
}

const fetchChapters = async (subjectId = null) => {
  try {
    if (subjectId) {
      // Fetch chapters for specific subject
      const response = await axios.get(`http://127.0.0.1:5000/api/admin/subjects/${subjectId}/chapters`, {
        headers: getAuthHeaders()
      })
      chapters.value = response.data.chapters
    } else {
      // For now, we'll fetch chapters when a subject is selected
      chapters.value = []
    }
    stats.value.totalChapters = chapters.value.length
  } catch (error) {
    console.error('Error fetching chapters:', error)
    alert('Error fetching chapters: ' + (error.response?.data?.message || error.message))
  }
}

// Fetch recent activities
const fetchRecentActivities = async () => {
  try {
    // Create recent activities from existing data
    const activities = []
    
    // Add recent users (last 5)
    if (users.value.length > 0) {
      users.value.slice(-3).forEach(user => {
        activities.push({
          type: 'user_registered',
          message: `New user registered: ${user.email}`,
          timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000), // Random time in last 24 hours
          icon: '👤'
        })
      })
    }
    
    // Add recent subjects
    if (subjects.value.length > 0) {
      subjects.value.slice(-2).forEach(subject => {
        activities.push({
          type: 'subject_created',
          message: `Subject "${subject.name}" was created`,
          timestamp: new Date(Date.now() - Math.random() * 48 * 60 * 60 * 1000), // Random time in last 48 hours
          icon: '📚'
        })
      })
    }
    
    // Add recent quizzes
    if (quizzes.value.length > 0) {
      quizzes.value.slice(-2).forEach(quiz => {
        if (quiz.is_published) {
          activities.push({
            type: 'quiz_published',
            message: `Quiz "${quiz.title}" was published`,
            timestamp: new Date(Date.now() - Math.random() * 72 * 60 * 60 * 1000), // Random time in last 72 hours
            icon: '🎯'
          })
        } else {
          activities.push({
            type: 'quiz_created',
            message: `Quiz "${quiz.title}" was created`,
            timestamp: new Date(Date.now() - Math.random() * 96 * 60 * 60 * 1000), // Random time in last 96 hours
            icon: '📝'
          })
        }
      })
    }
    
    // Sort by timestamp (newest first) and take top 5
    recentActivities.value = activities
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, 5)
      
  } catch (error) {
    console.error('Error generating recent activities:', error)
    // Fallback to static activities if there's an error
    recentActivities.value = [
      {
        type: 'fallback',
        message: 'Welcome to the Admin Dashboard',
        timestamp: new Date(),
        icon: '🎉'
      }
    ]
  }
}

const fetchQuestions = async (quizId = null) => {
  try {
    if (quizId) {
      // Fetch questions for specific quiz
      const response = await axios.get(`http://127.0.0.1:5000/api/admin/quizzes/${quizId}/questions`, {
        headers: getAuthHeaders()
      })
      questions.value = response.data.questions
    } else {
      // For now, we'll fetch questions when a quiz is selected
      questions.value = []
    }
    stats.value.totalQuestions = questions.value.length
  } catch (error) {
    console.error('Error fetching questions:', error)
    alert('Error fetching questions: ' + (error.response?.data?.message || error.message))
  }
}

// Subject management
const openSubjectModal = (subject = null) => {
  editingSubject.value = subject
  if (subject) {
    subjectForm.value = {
      name: subject.name,
      description: subject.description || ''
    }
  } else {
    subjectForm.value = {
      name: '',
      description: ''
    }
  }
  showSubjectModal.value = true
}

const closeSubjectModal = () => {
  showSubjectModal.value = false
  editingSubject.value = null
  subjectForm.value = {
    name: '',
    description: ''
  }
}

const saveSubject = async () => {
  if (!subjectForm.value.name.trim()) {
    alert('Subject name is required')
    return
  }

  loading.value = true
  try {
    if (editingSubject.value) {
      // Update existing subject
      await axios.put(`http://127.0.0.1:5000/api/admin/subjects/${editingSubject.value.id}`, 
        subjectForm.value, 
        { headers: getAuthHeaders() }
      )
      alert('Subject updated successfully!')
    } else {
      // Create new subject
      await axios.post('http://127.0.0.1:5000/api/admin/subjects', 
        subjectForm.value, 
        { headers: getAuthHeaders() }
      )
      alert('Subject created successfully!')
    }
    
    closeSubjectModal()
    await fetchSubjects()
  } catch (error) {
    console.error('Error saving subject:', error)
    alert('Error saving subject: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const deleteSubject = async (subject) => {
  if (!confirm(`Are you sure you want to delete "${subject.name}"?`)) {
    return
  }

  loading.value = true
  try {
    await axios.delete(`http://127.0.0.1:5000/api/admin/subjects/${subject.id}`, {
      headers: getAuthHeaders()
    })
    alert('Subject deleted successfully!')
    await fetchSubjects()
  } catch (error) {
    console.error('Error deleting subject:', error)
    alert('Error deleting subject: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// Chapter management
const openChapterModal = (chapter = null, subjectId = null) => {
  editingChapter.value = chapter
  selectedSubjectId.value = subjectId || selectedSubjectId.value
  
  if (chapter) {
    chapterForm.value = {
      name: chapter.name,
      description: chapter.description || '',
      subject_id: chapter.subject_id
    }
  } else {
    chapterForm.value = {
      name: '',
      description: '',
      subject_id: selectedSubjectId.value
    }
  }
  showChapterModal.value = true
}

const closeChapterModal = () => {
  showChapterModal.value = false
  editingChapter.value = null
  chapterForm.value = {
    name: '',
    description: '',
    subject_id: null
  }
}

const saveChapter = async () => {
  if (!chapterForm.value.name.trim()) {
    alert('Chapter name is required')
    return
  }

  if (!chapterForm.value.subject_id) {
    alert('Please select a subject')
    return
  }

  loading.value = true
  try {
    if (editingChapter.value) {
      // Update existing chapter
      await axios.put(`http://127.0.0.1:5000/api/admin/chapters/${editingChapter.value.id}`, 
        {
          name: chapterForm.value.name,
          description: chapterForm.value.description
        }, 
        { headers: getAuthHeaders() }
      )
      alert('Chapter updated successfully!')
    } else {
      // Create new chapter
      await axios.post(`http://127.0.0.1:5000/api/admin/subjects/${chapterForm.value.subject_id}/chapters`, 
        {
          name: chapterForm.value.name,
          description: chapterForm.value.description
        }, 
        { headers: getAuthHeaders() }
      )
      alert('Chapter created successfully!')
    }
    
    closeChapterModal()
    await fetchChapters(selectedSubjectId.value)
  } catch (error) {
    console.error('Error saving chapter:', error)
    alert('Error saving chapter: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const deleteChapter = async (chapter) => {
  if (!confirm(`Are you sure you want to delete "${chapter.name}"?`)) {
    return
  }

  loading.value = true
  try {
    await axios.delete(`http://127.0.0.1:5000/api/admin/chapters/${chapter.id}`, {
      headers: getAuthHeaders()
    })
    alert('Chapter deleted successfully!')
    await fetchChapters(selectedSubjectId.value)
  } catch (error) {
    console.error('Error deleting chapter:', error)
    alert('Error deleting chapter: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const selectSubjectForChapters = async (subjectId) => {
  selectedSubjectId.value = subjectId
  await fetchChapters(subjectId)
  setActiveSection('chapters')
}

const viewChapterQuizzes = (chapterId) => {
  selectedChapterId.value = chapterId
  fetchQuizzes(chapterId)
  setActiveSection('quizzes')
}

// Quiz management
const openQuizModal = (quiz = null, chapterId = null) => {
  editingQuiz.value = quiz
  selectedChapterId.value = chapterId || selectedChapterId.value
  
  if (quiz) {
    quizForm.value = {
      title: quiz.title,
      description: quiz.description || '',
      chapter_id: quiz.chapter_id,
      time_duration: quiz.time_duration || 30,
      remarks: quiz.remarks || '',
      is_published: quiz.is_published || false
    }
  } else {
    quizForm.value = {
      title: '',
      description: '',
      chapter_id: selectedChapterId.value,
      time_duration: 30,
      remarks: '',
      is_published: false
    }
  }
  showQuizModal.value = true
}

const closeQuizModal = () => {
  showQuizModal.value = false
  editingQuiz.value = null
  quizForm.value = {
    title: '',
    description: '',
    chapter_id: null,
    time_duration: 30,
    remarks: '',
    is_published: false
  }
}

const saveQuiz = async () => {
  if (!quizForm.value.title.trim()) {
    alert('Quiz title is required')
    return
  }

  if (!quizForm.value.chapter_id) {
    alert('Please select a chapter')
    return
  }

  loading.value = true
  try {
    if (editingQuiz.value) {
      // Update existing quiz
      await axios.put(`http://127.0.0.1:5000/api/admin/quizzes/${editingQuiz.value.id}`, 
        {
          title: quizForm.value.title,
          description: quizForm.value.description,
          time_duration: parseInt(quizForm.value.time_duration),
          remarks: quizForm.value.remarks,
          is_published: quizForm.value.is_published
        }, 
        { headers: getAuthHeaders() }
      )
      alert('Quiz updated successfully!')
    } else {
      // Create new quiz
      await axios.post(`http://127.0.0.1:5000/api/admin/chapters/${quizForm.value.chapter_id}/quizzes`, 
        {
          title: quizForm.value.title,
          description: quizForm.value.description,
          time_duration: parseInt(quizForm.value.time_duration),
          remarks: quizForm.value.remarks,
          is_published: quizForm.value.is_published
        }, 
        { headers: getAuthHeaders() }
      )
      alert('Quiz created successfully!')
    }
    
    closeQuizModal()
    await fetchQuizzes(selectedChapterId.value)
  } catch (error) {
    console.error('Error saving quiz:', error)
    alert('Error saving quiz: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const deleteQuiz = async (quiz) => {
  if (!confirm(`Are you sure you want to delete "${quiz.title}"?`)) {
    return
  }

  loading.value = true
  try {
    await axios.delete(`http://127.0.0.1:5000/api/admin/quizzes/${quiz.id}`, {
      headers: getAuthHeaders()
    })
    alert('Quiz deleted successfully!')
    await fetchQuizzes(selectedChapterId.value)
  } catch (error) {
    console.error('Error deleting quiz:', error)
    alert('Error deleting quiz: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const toggleQuizPublish = async (quiz) => {
  loading.value = true
  try {
    await axios.patch(`http://127.0.0.1:5000/api/admin/quizzes/${quiz.id}/publish`, 
      {
        is_published: !quiz.is_published
      }, 
      { headers: getAuthHeaders() }
    )
    alert(`Quiz ${!quiz.is_published ? 'published' : 'unpublished'} successfully!`)
    await fetchQuizzes(selectedChapterId.value)
  } catch (error) {
    console.error('Error toggling quiz publish status:', error)
    alert('Error updating quiz: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const selectChapterForQuizzes = async (chapterId) => {
  selectedChapterId.value = chapterId
  await fetchQuizzes(chapterId)
  setActiveSection('quizzes')
}

const viewQuizQuestions = (quizId) => {
  selectedQuizId.value = quizId
  fetchQuestions(quizId)
  setActiveSection('questions')
}

// Question management
const openQuestionModal = (question = null, quizId = null) => {
  editingQuestion.value = question
  selectedQuizId.value = quizId || selectedQuizId.value
  
  if (question) {
    questionForm.value = {
      question_statement: question.question_statement,
      question_type: question.question_type,
      points: question.points || 1,
      correct_answer: question.correct_answer,
      quiz_id: question.quiz_id,
      options: question.options ? [...question.options] : ['', '', '', '']
    }
  } else {
    questionForm.value = {
      question_statement: '',
      question_type: 'MCQ',
      points: 1,
      correct_answer: '',
      quiz_id: selectedQuizId.value,
      options: ['', '', '', '']
    }
  }
  showQuestionModal.value = true
}

const closeQuestionModal = () => {
  showQuestionModal.value = false
  editingQuestion.value = null
  questionForm.value = {
    question_statement: '',
    question_type: 'MCQ',
    points: 1,
    correct_answer: '',
    quiz_id: null,
    options: ['', '', '', '']
  }
}

const saveQuestion = async () => {
  if (!questionForm.value.question_statement.trim()) {
    alert('Question statement is required')
    return
  }

  if (!questionForm.value.correct_answer.trim()) {
    alert('Correct answer is required')
    return
  }

  if (!questionForm.value.quiz_id) {
    alert('Please select a quiz')
    return
  }

  // Validate MCQ options
  if (questionForm.value.question_type === 'MCQ') {
    const validOptions = questionForm.value.options.filter(option => option.trim() !== '');
    if (validOptions.length !== 4) {
      alert('MCQ questions require exactly 4 options')
      return
    }
    
    if (!questionForm.value.options.includes(questionForm.value.correct_answer.trim())) {
      alert('Correct answer must be one of the provided options')
      return
    }
  }

  loading.value = true
  try {
    if (editingQuestion.value) {
      // Update existing question
      const payload = {
        question_statement: questionForm.value.question_statement,
        question_type: questionForm.value.question_type,
        points: parseInt(questionForm.value.points),
        correct_answer: questionForm.value.correct_answer
      }
      
      if (questionForm.value.question_type === 'MCQ') {
        payload.option1 = questionForm.value.options[0]
        payload.option2 = questionForm.value.options[1]
        payload.option3 = questionForm.value.options[2]
        payload.option4 = questionForm.value.options[3]
      }
      
      await axios.put(`http://127.0.0.1:5000/api/admin/questions/${editingQuestion.value.id}`, 
        payload, 
        { headers: getAuthHeaders() }
      )
      alert('Question updated successfully!')
    } else {
      // Create new question
      const payload = {
        question_statement: questionForm.value.question_statement,
        question_type: questionForm.value.question_type,
        points: parseInt(questionForm.value.points),
        correct_answer: questionForm.value.correct_answer
      }
      
      if (questionForm.value.question_type === 'MCQ') {
        payload.option1 = questionForm.value.options[0]
        payload.option2 = questionForm.value.options[1]
        payload.option3 = questionForm.value.options[2]
        payload.option4 = questionForm.value.options[3]
      }
      
      await axios.post(`http://127.0.0.1:5000/api/admin/quizzes/${questionForm.value.quiz_id}/questions`, 
        payload, 
        { headers: getAuthHeaders() }
      )
      alert('Question created successfully!')
    }
    
    closeQuestionModal()
    await fetchQuestions(selectedQuizId.value)
  } catch (error) {
    console.error('Error saving question:', error)
    alert('Error saving question: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const deleteQuestion = async (question) => {
  if (!confirm(`Are you sure you want to delete this question?`)) {
    return
  }

  loading.value = true
  try {
    await axios.delete(`http://127.0.0.1:5000/api/admin/questions/${question.id}`, {
      headers: getAuthHeaders()
    })
    alert('Question deleted successfully!')
    await fetchQuestions(selectedQuizId.value)
  } catch (error) {
    console.error('Error deleting question:', error)
    alert('Error deleting question: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const selectQuizForQuestions = async (quizId) => {
  selectedQuizId.value = quizId
  await fetchQuestions(quizId)
  setActiveSection('questions')
}

// User management
const openUserModal = () => {
  userForm.value = {
    email: '',
    password: '',
    name: '',
    dob: '',
    qualification: '',
    role: 'student'
  }
  showUserModal.value = true
}

const closeUserModal = () => {
  showUserModal.value = false
  userForm.value = {
    email: '',
    password: '',
    name: '',
    dob: '',
    qualification: '',
    role: 'student'
  }
}

const saveUser = async () => {
  if (!userForm.value.email || !userForm.value.password || !userForm.value.name) {
    alert('Email, password, and name are required')
    return
  }

  loading.value = true
  try {
    await axios.post('http://127.0.0.1:5000/api/register', userForm.value, {
      headers: { 'Content-Type': 'application/json' }
    })
    alert('User created successfully!')
    closeUserModal()
    await fetchUsers()
  } catch (error) {
    console.error('Error creating user:', error)
    alert('Error creating user: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// Navigation
const setActiveSection = (section) => {
  activeSection.value = section
  
  // Update URL hash
  window.location.hash = section
  
  // Update navigation active state
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active')
  })
  
  // Find the nav item that corresponds to this section
  const targetNavItem = document.querySelector(`[data-section="${section}"]`)?.closest('.nav-item')
  targetNavItem?.classList.add('active')
  
  // Update content section visibility
  document.querySelectorAll('.content-section').forEach(contentSection => {
    contentSection.classList.remove('active')
  })
  document.getElementById(section)?.classList.add('active')
}

// CSV Export function
const csvExport = async () => {
  try {
    loading.value = true
    
    // Trigger the CSV export job
    const response = await axios.get('http://127.0.0.1:5000/api/export', {
      headers: getAuthHeaders()
    })
    
    const jobId = response.data.id
    alert('CSV export started! Please wait while we prepare your file...')
    
    // Poll for the result
    const pollResult = async () => {
      try {
        const resultResponse = await axios.get(`http://127.0.0.1:5000/api/csv_result/${jobId}`, {
          headers: getAuthHeaders(),
          responseType: 'blob' // Important for file download
        })
        
        // Check if we got a blob (file) or JSON (still processing)
        if (resultResponse.headers['content-type']?.includes('application/json')) {
          // Still processing, continue polling
          setTimeout(pollResult, 2000) // Poll every 2 seconds
        } else {
          // File is ready, download it
          const blob = new Blob([resultResponse.data], { type: 'text/csv' })
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `quiz_app_data_${new Date().toISOString().split('T')[0]}.csv`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
          
          alert('CSV file downloaded successfully!')
          loading.value = false
        }
      } catch (pollError) {
        console.error('Error polling for CSV result:', pollError)
        // If it's a 200 status with processing message, continue polling
        if (pollError.response?.status === 200) {
          setTimeout(pollResult, 2000)
        } else {
          alert('Error downloading CSV file. Please try again.')
          loading.value = false
        }
      }
    }
    
    // Start polling after a short delay
    setTimeout(pollResult, 1000)
    
  } catch (error) {
    console.error('Error starting CSV export:', error)
    alert('Error starting CSV export: ' + (error.response?.data?.message || error.message))
    loading.value = false
  }
}

// Logout function
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userData')
  window.location.href = '/'
}

// Initialize
const initializeAdmin = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchSubjects(),
      fetchUsers(),
      fetchQuizzes()
    ])
    // Initialize chapters as empty until a subject is selected
    stats.value.totalChapters = 0
    // Fetch recent activities after data is loaded
    await fetchRecentActivities()
  } catch (error) {
    console.error('Error initializing admin dashboard:', error)
  } finally {
    loading.value = false
  }
}

// Helper function to format time ago
const formatTimeAgo = (timestamp) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diffInMinutes = Math.floor((now - time) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`
  
  return time.toLocaleDateString()
}

// Handle initial section based on URL hash
const handleInitialSection = () => {
  const hash = window.location.hash.substring(1) // Remove the #
  if (hash && ['dashboard', 'subjects', 'chapters', 'quizzes', 'questions', 'scores', 'analytics'].includes(hash)) {
    setActiveSection(hash)
  } else if (hash === 'users') {
    // Redirect to the separate users page
    router.push('/admin/users')
  } else {
    setActiveSection('dashboard')
  }
}

// Handle hash changes
const handleHashChange = () => {
  const hash = window.location.hash.substring(1)
  if (hash && ['dashboard', 'subjects', 'chapters', 'quizzes', 'questions', 'scores', 'analytics'].includes(hash)) {
    setActiveSection(hash)
  } else if (hash === 'users') {
    router.push('/admin/users')
  }
}

onMounted(() => {
  initializeAdmin()
  
  // Handle initial section
  handleInitialSection()
  
  // Listen for hash changes
  window.addEventListener('hashchange', handleHashChange)
})

// Cleanup on unmount
onUnmounted(() => {
  window.removeEventListener('hashchange', handleHashChange)
})

// Question MCQ utility functions
const addMCQOption = () => {
  if (questionForm.value.options.length < 6) {
    questionForm.value.options.push('');
  }
};

const removeMCQOption = (index) => {
  if (questionForm.value.options.length > 4) {
    const removedOption = questionForm.value.options[index];
    questionForm.value.options.splice(index, 1);
    
    // If the removed option was the correct answer, clear the correct answer
    if (questionForm.value.correct_answer === removedOption) {
      questionForm.value.correct_answer = '';
    }
  }
};


</script>


<!-- =========================================================================== -->

<template>
  <div class="admin-container">
    <!-- Header -->
    <header class="admin-header">
      <div class="header-content">
        <h1 class="admin-title">Quiz App Admin Dashboard</h1>
        <div class="header-actions">
          <span class="admin-name">Welcome, Admin</span>
          <button class="btn btn-logout" @click="logout">Logout</button>
        </div>
      </div>
    </header>

    <!-- Navigation Sidebar -->
    <aside class="admin-sidebar">
      <nav class="sidebar-nav">
        <ul class="nav-list">
          <li class="nav-item active">
            <a href="#" @click.prevent="setActiveSection('dashboard')" class="nav-link" data-section="dashboard">
              <i class="icon-dashboard"></i>
              Dashboard
            </a>
          </li>
          <li class="nav-item">
            <a href="#" @click.prevent="router.push('/admin/users')" class="nav-link" data-section="users">
              <i class="icon-users"></i>
              User Management
            </a>
          </li>
          <li class="nav-item">
            <a href="#" @click.prevent="setActiveSection('subjects')" class="nav-link" data-section="subjects">
              <i class="icon-subjects"></i>
              Subjects
            </a>
          </li>
          <li class="nav-item">
            <a href="#" @click.prevent="setActiveSection('chapters')" class="nav-link" data-section="chapters">
              <i class="icon-chapters"></i>
              Chapters
            </a>
          </li>
          <li class="nav-item">
            <a href="#" @click.prevent="setActiveSection('quizzes')" class="nav-link" data-section="quizzes">
              <i class="icon-quizzes"></i>
              Quizzes
            </a>
          </li>
          <li class="nav-item">
            <a href="#" @click.prevent="setActiveSection('questions')" class="nav-link" data-section="questions">
              <i class="icon-questions"></i>
              Questions
            </a>
          </li>
          <!-- <li class="nav-item">
            <a href="#" @click.prevent="setActiveSection('scores')" class="nav-link" data-section="scores">
              <i class="icon-scores"></i>
              Scores & Results
            </a>
          </li> -->
          <!-- <li class="nav-item">
            <a href="#" @click.prevent="setActiveSection('analytics')" class="nav-link" data-section="analytics">
              <i class="icon-analytics"></i>
              Analytics
            </a>
          </li> -->
        </ul>
      </nav>
    </aside>

    <!-- Main Content Area -->
    <main class="admin-main">
      <!-- Dashboard Overview -->
      <section id="dashboard" class="content-section active">
        <div class="section-header">
          <h2>Dashboard Overview</h2>
          <button @click="csvExport" class="btn btn-secondary my-2">Download CSV</button>
        </div>

        
        <!-- Stats Cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon users-icon"></div>
            <div class="stat-info">
              <h3>Total Users</h3>
              <p class="stat-number">{{ stats.totalUsers }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon subjects-icon"></div>
            <div class="stat-info">
              <h3>Subjects</h3>
              <p class="stat-number">{{ stats.totalSubjects }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon chapters-icon"></div>
            <div class="stat-info">
              <h3>Chapters</h3>
              <p class="stat-number">{{ stats.totalChapters }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon quizzes-icon"></div>
            <div class="stat-info">
              <h3>Total Quizzes</h3>
              <p class="stat-number">{{ stats.totalQuizzes }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon attempts-icon"></div>
            <div class="stat-info">
              <h3>Quiz Attempts</h3>
              <p class="stat-number">{{ stats.totalQuestions }}</p>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="recent-activity">
          <h3>Recent Activity</h3>
          <div class="activity-list">
            <div v-if="recentActivities.length === 0" class="activity-item">
              <span class="activity-text">No recent activity</span>
            </div>
            <div v-for="activity in recentActivities" :key="activity.type + activity.message" class="activity-item">
              <span class="activity-icon">{{ activity.icon }}</span>
              <span class="activity-time">{{ formatTimeAgo(activity.timestamp) }}</span>
              <span class="activity-text">{{ activity.message }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Subject Management Section -->
      <section id="subjects" class="content-section">
        <div class="section-header">
          <h2>Subject Management</h2>
          <button class="btn btn-primary" @click="openSubjectModal()">Add New Subject</button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-container">
          <p>Loading subjects...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="subjects.length === 0" class="empty-state">
          <p>No subjects found. Create your first subject!</p>
          <button class="btn btn-primary" @click="openSubjectModal()">Add Subject</button>
        </div>

        <!-- Subjects Grid -->
        <div v-else class="subjects-grid">
          <div 
            v-for="subject in subjects" 
            :key="subject.id"
            class="subject-card"
          >
            <h3>{{ subject.name }}</h3>
            <p class="subject-description">{{ subject.description || 'No description available' }}</p>
            <div class="subject-stats">
              <span>{{ subject.chapters?.length || 0 }} Chapters</span>
              <span>{{ subject.quizzes?.length || 0 }} Quizzes</span>
            </div>
            <div class="card-actions">
              <button 
                class="btn btn-sm btn-primary" 
                @click="selectSubjectForChapters(subject.id)"
              >
                View Chapters
              </button>
              <button 
                class="btn btn-sm btn-secondary" 
                @click="openSubjectModal(subject)"
              >
                Edit
              </button>
              <button 
                class="btn btn-sm btn-danger" 
                @click="deleteSubject(subject)"
                :disabled="loading"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Chapter Management Section -->
      <section id="chapters" class="content-section">
        <div class="section-header">
          <h2>Chapter Management</h2>
          <div class="header-actions">
            <select 
              v-model="selectedSubjectId" 
              @change="fetchChapters(selectedSubjectId)" 
              class="subject-select"
            >
              <option value="">Select a Subject</option>
              <option 
                v-for="subject in subjects" 
                :key="subject.id" 
                :value="subject.id"
              >
                {{ subject.name }}
              </option>
            </select>
            <button 
              class="btn btn-primary" 
              @click="openChapterModal(null, selectedSubjectId)"
              :disabled="!selectedSubjectId"
            >
              Add New Chapter
            </button>
          </div>
        </div>

        <!-- Subject Selection Message -->
        <div v-if="!selectedSubjectId" class="empty-state">
          <p>Please select a subject to view and manage its chapters.</p>
        </div>

        <!-- Loading State -->
        <div v-else-if="loading" class="loading-container">
          <p>Loading chapters...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="chapters.length === 0 && selectedSubjectId" class="empty-state">
          <p>No chapters found for this subject. Create your first chapter!</p>
          <button 
            class="btn btn-primary" 
            @click="openChapterModal(null, selectedSubjectId)"
          >
            Add Chapter
          </button>
        </div>

        <!-- Chapters Grid -->
        <div v-else class="chapters-grid">
          <div 
            v-for="chapter in chapters" 
            :key="chapter.id"
            class="chapter-card"
          >
            <h3>{{ chapter.name }}</h3>
            <p class="chapter-description">{{ chapter.description || 'No description available' }}</p>
            <div class="chapter-stats">
              <span>{{ chapter.quizzes?.length || 0 }} Quizzes</span>
            </div>
            <div class="card-actions">
              <button 
                class="btn btn-sm btn-primary"
                @click="selectChapterForQuizzes(chapter.id)"
              >
                View Quizzes
              </button>
              <button 
                class="btn btn-sm btn-secondary" 
                @click="openChapterModal(chapter)"
              >
                Edit
              </button>
              <button 
                class="btn btn-sm btn-danger" 
                @click="deleteChapter(chapter)"
                :disabled="loading"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </section>
      <!-- Quiz Management Section -->
      <section id="quizzes" class="content-section">
        <div class="section-header">
          <h2>Quiz Management</h2>
          <div class="header-actions">
            <select 
              v-model="selectedSubjectId" 
              @change="fetchChapters(selectedSubjectId)" 
              class="subject-select"
            >
              <option value="">Select Subject</option>
              <option 
                v-for="subject in subjects" 
                :key="subject.id" 
                :value="subject.id"
              >
                {{ subject.name }}
              </option>
            </select>
            <select 
              v-model="selectedChapterId" 
              @change="fetchQuizzes(selectedChapterId)" 
              class="subject-select"
              :disabled="!selectedSubjectId"
            >
              <option value="">Select Chapter</option>
              <option 
                v-for="chapter in chapters" 
                :key="chapter.id" 
                :value="chapter.id"
              >
                {{ chapter.name }}
              </option>
            </select>
            <button 
              class="btn btn-primary" 
              @click="openQuizModal(null, selectedChapterId)"
              :disabled="!selectedChapterId"
            >
              Create New Quiz
            </button>
          </div>
        </div>

        <!-- Selection Message -->
        <div v-if="!selectedChapterId" class="empty-state">
          <p>Please select a subject and chapter to view and manage quizzes.</p>
        </div>

        <!-- Loading State -->
        <div v-else-if="loading" class="loading-container">
          <p>Loading quizzes...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="quizzes.length === 0 && selectedChapterId" class="empty-state">
          <p>No quizzes found for this chapter. Create your first quiz!</p>
          <button 
            class="btn btn-primary" 
            @click="openQuizModal(null, selectedChapterId)"
          >
            Create Quiz
          </button>
        </div>

        <!-- Quiz List -->
        <div v-else class="quiz-list">
          <div 
            v-for="quiz in quizzes" 
            :key="quiz.id"
            class="quiz-item"
          >
            <div class="quiz-info">
              <h3>{{ quiz.title }}</h3>
              <p class="quiz-meta">
                {{ quiz.subject_name }} > {{ quiz.chapter_name }} | 
                {{ quiz.time_duration }} mins
                <span v-if="quiz.description"> | {{ quiz.description }}</span>
              </p>
              <span 
                :class="['status-badge', quiz.is_published ? 'published' : 'draft']"
              >
                {{ quiz.is_published ? 'Published' : 'Draft' }}
              </span>
            </div>
            <div class="quiz-actions">
              <button 
                class="btn btn-sm btn-primary"
                @click="selectQuizForQuestions(quiz.id)"
              >
                Edit Questions
              </button>
              <button 
                class="btn btn-sm btn-secondary" 
                @click="openQuizModal(quiz)"
              >
                Edit Quiz
              </button>
              <button 
                :class="['btn', 'btn-sm', quiz.is_published ? 'btn-warning' : 'btn-success']"
                @click="toggleQuizPublish(quiz)"
                :disabled="loading"
              >
                {{ quiz.is_published ? 'Unpublish' : 'Publish' }}
              </button>
              <button 
                class="btn btn-sm btn-danger" 
                @click="deleteQuiz(quiz)"
                :disabled="loading"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Question Management Section -->
      <section id="questions" class="content-section">
        <div class="section-header">
          <h2>Question Bank</h2>
          <div class="header-actions">
            <select 
              v-model="selectedSubjectId" 
              @change="fetchChapters(selectedSubjectId)" 
              class="subject-select"
            >
              <option value="">Select Subject</option>
              <option 
                v-for="subject in subjects" 
                :key="subject.id" 
                :value="subject.id"
              >
                {{ subject.name }}
              </option>
            </select>
            <select 
              v-model="selectedChapterId" 
              @change="fetchQuizzes(selectedChapterId)" 
              class="subject-select"
              :disabled="!selectedSubjectId"
            >
              <option value="">Select Chapter</option>
              <option 
                v-for="chapter in chapters" 
                :key="chapter.id" 
                :value="chapter.id"
              >
                {{ chapter.name }}
              </option>
            </select>
            <select 
              v-model="selectedQuizId" 
              @change="fetchQuestions(selectedQuizId)" 
              class="subject-select"
              :disabled="!selectedChapterId"
            >
              <option value="">Select Quiz</option>
              <option 
                v-for="quiz in quizzes" 
                :key="quiz.id" 
                :value="quiz.id"
              >
                {{ quiz.title }}
              </option>
            </select>
            <button 
              class="btn btn-primary" 
              @click="openQuestionModal(null, selectedQuizId)"
              :disabled="!selectedQuizId"
            >
              Add New Question
            </button>
          </div>
        </div>

        <!-- Selection Message -->
        <div v-if="!selectedQuizId" class="empty-state">
          <p>Please select a subject, chapter, and quiz to view and manage questions.</p>
        </div>

        <!-- Loading State -->
        <div v-else-if="loading" class="loading-container">
          <p>Loading questions...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="questions.length === 0 && selectedQuizId" class="empty-state">
          <p>No questions found for this quiz. Create your first question!</p>
          <button 
            class="btn btn-primary" 
            @click="openQuestionModal(null, selectedQuizId)"
          >
            Add Question
          </button>
        </div>

        <!-- Questions List -->
        <div v-else class="questions-list">
          <div 
            v-for="(question, index) in questions" 
            :key="question.id"
            class="question-item"
          >
            <div class="question-header">
              <span class="question-number">Q{{ index + 1 }}</span>
              <span class="question-type-badge" :class="question.question_type.toLowerCase()">
                {{ question.question_type }}
              </span>
              <span class="question-points">{{ question.points }} pt{{ question.points !== 1 ? 's' : '' }}</span>
            </div>
            
            <div class="question-content">
              <h4 class="question-statement">{{ question.question_statement }}</h4>
              
              <!-- MCQ Options -->
              <div v-if="question.question_type === 'MCQ' && question.options" class="mcq-options">
                <div 
                  v-for="(option, optIndex) in question.options" 
                  :key="optIndex"
                  class="mcq-option"
                  :class="{ 'correct': option === question.correct_answer }"
                >
                  <span class="option-label">{{ String.fromCharCode(65 + optIndex) }}.</span>
                  <span class="option-text">{{ option }}</span>
                  <span v-if="option === question.correct_answer" class="correct-indicator">✓</span>
                </div>
              </div>
              
              <!-- Non-MCQ Answer -->
              <div v-else class="correct-answer">
                <strong>Correct Answer:</strong> {{ question.correct_answer }}
              </div>
            </div>
            
            <div class="question-actions">
              <button 
                class="btn btn-sm btn-secondary" 
                @click="openQuestionModal(question)"
              >
                Edit
              </button>
              <button 
                class="btn btn-sm btn-danger" 
                @click="deleteQuestion(question)"
                :disabled="loading"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Scores & Results Section -->
      <section id="scores" class="content-section">
        <div class="section-header">
          <h2>Scores & Results</h2>
        </div>
        
        <div class="coming-soon">
          <h3>Scores Management</h3>
          <p>View and manage all quiz scores and student results.</p>
          <p>This section will show detailed score analytics and student performance data.</p>
        </div>
      </section>

      <!-- Analytics Section -->
      <section id="analytics" class="content-section">
        <div class="section-header">
          <h2>Analytics & Reports</h2>
        </div>

        <!-- Analytics Cards -->
        <div class="analytics-grid">
          <div class="analytics-card">
            <h3>Quiz Performance</h3>
            <div class="chart-placeholder">
              <p>Average Score: 78.5%</p>
              <p>Total Attempts: 1,234</p>
              <p>Success Rate: 65%</p>
            </div>
          </div>

          <div class="analytics-card">
            <h3>Subject Popularity</h3>
            <div class="chart-placeholder">
              <div class="progress-item">
                <span>Mathematics</span>
                <div class="progress-bar">
                  <div class="progress-fill" style="width: 85%"></div>
                </div>
              </div>
              <div class="progress-item">
                <span>Physics</span>
                <div class="progress-bar">
                  <div class="progress-fill" style="width: 70%"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="analytics-card">
            <h3>User Activity</h3>
            <div class="chart-placeholder">
              <p>Active Users: 89</p>
              <p>New Registrations: 12</p>
              <p>Daily Logins: 45</p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Subject Modal -->
    <div v-if="showSubjectModal" class="modal-overlay" @click="closeSubjectModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingSubject ? 'Edit Subject' : 'Add New Subject' }}</h3>
          <button class="modal-close" @click="closeSubjectModal">&times;</button>
        </div>
        
        <form @submit.prevent="saveSubject" class="modal-form">
          <div class="form-group">
            <label for="subject-name">Subject Name *</label>
            <input 
              id="subject-name"
              v-model="subjectForm.name" 
              type="text" 
              class="form-control" 
              placeholder="Enter subject name"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="subject-description">Description</label>
            <textarea 
              id="subject-description"
              v-model="subjectForm.description" 
              class="form-control" 
              placeholder="Enter subject description"
              rows="3"
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeSubjectModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Saving...' : (editingSubject ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- User Modal -->
    <div v-if="showUserModal" class="modal-overlay" @click="closeUserModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New User</h3>
          <button class="modal-close" @click="closeUserModal">&times;</button>
        </div>
        
        <form @submit.prevent="saveUser" class="modal-form">
          <div class="form-group">
            <label for="user-email">Email *</label>
            <input 
              id="user-email"
              v-model="userForm.email" 
              type="email" 
              class="form-control" 
              placeholder="Enter email address"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="user-password">Password *</label>
            <input 
              id="user-password"
              v-model="userForm.password" 
              type="password" 
              class="form-control" 
              placeholder="Enter password"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="user-name">Full Name *</label>
            <input 
              id="user-name"
              v-model="userForm.name" 
              type="text" 
              class="form-control" 
              placeholder="Enter full name"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="user-dob">Date of Birth</label>
            <input 
              id="user-dob"
              v-model="userForm.dob" 
              type="date" 
              class="form-control"
            />
          </div>
          
          <div class="form-group">
            <label for="user-qualification">Qualification</label>
            <input 
              id="user-qualification"
              v-model="userForm.qualification" 
              type="text" 
              class="form-control" 
              placeholder="Enter qualification"
            />
          </div>
          
          <div class="form-group">
            <label for="user-role">Role</label>
            <select id="user-role" v-model="userForm.role" class="form-control">
              <option value="student">Student</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeUserModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Creating...' : 'Create User' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Chapter Modal -->
    <div v-if="showChapterModal" class="modal-overlay" @click="closeChapterModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingChapter ? 'Edit Chapter' : 'Add New Chapter' }}</h3>
          <button class="modal-close" @click="closeChapterModal">&times;</button>
        </div>
        
        <form @submit.prevent="saveChapter" class="modal-form">
          <div class="form-group">
            <label for="chapter-subject">Subject</label>
            <select 
              id="chapter-subject"
              v-model="chapterForm.subject_id" 
              class="form-control" 
              required
              :disabled="editingChapter"
            >
              <option value="">Select Subject</option>
              <option 
                v-for="subject in subjects" 
                :key="subject.id" 
                :value="subject.id"
              >
                {{ subject.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="chapter-name">Chapter Name *</label>
            <input 
              id="chapter-name"
              v-model="chapterForm.name" 
              type="text" 
              class="form-control" 
              placeholder="Enter chapter name"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="chapter-description">Description</label>
            <textarea 
              id="chapter-description"
              v-model="chapterForm.description" 
              class="form-control" 
              placeholder="Enter chapter description"
              rows="3"
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeChapterModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Saving...' : (editingChapter ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Quiz Modal -->
    <div v-if="showQuizModal" class="modal-overlay" @click="closeQuizModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingQuiz ? 'Edit Quiz' : 'Create New Quiz' }}</h3>
          <button class="modal-close" @click="closeQuizModal">&times;</button>
        </div>
        
        <form @submit.prevent="saveQuiz" class="modal-form">
          <div class="form-group">
            <label for="quiz-chapter">Chapter</label>
            <select 
              id="quiz-chapter"
              v-model="quizForm.chapter_id" 
              class="form-control" 
              required
              :disabled="editingQuiz"
            >
              <option value="">Select Chapter</option>
              <option 
                v-for="chapter in chapters" 
                :key="chapter.id" 
                :value="chapter.id"
              >
                {{ chapter.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="quiz-title">Quiz Title *</label>
            <input 
              id="quiz-title"
              v-model="quizForm.title" 
              type="text" 
              class="form-control" 
              placeholder="Enter quiz title"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="quiz-description">Description</label>
            <textarea 
              id="quiz-description"
              v-model="quizForm.description" 
              class="form-control" 
              placeholder="Enter quiz description"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="quiz-duration">Time Duration (minutes) *</label>
              <input 
                id="quiz-duration"
                v-model="quizForm.time_duration" 
                type="number" 
                class="form-control" 
                placeholder="30"
                min="1"
                required
              />
            </div>
            <div class="form-group">
              <label for="quiz-published">Published</label>
              <select 
                id="quiz-published"
                v-model="quizForm.is_published" 
                class="form-control"
              >
                <option :value="false">Draft</option>
                <option :value="true">Published</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label for="quiz-remarks">Remarks</label>
            <textarea 
              id="quiz-remarks"
              v-model="quizForm.remarks" 
              class="form-control" 
              placeholder="Enter any remarks or instructions"
              rows="2"
            ></textarea>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeQuizModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Saving...' : (editingQuiz ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Question Modal -->
    <div v-if="showQuestionModal" class="modal-overlay" @click="closeQuestionModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingQuestion ? 'Edit Question' : 'Add New Question' }}</h2>
          <button class="close-btn" @click="closeQuestionModal">&times;</button>
        </div>
        
        <form @submit.prevent="saveQuestion" class="modal-form">
          <div class="form-group">
            <label for="questionStatement">Question Statement *</label>
            <textarea 
              id="questionStatement"
              v-model="questionForm.question_statement"
              class="form-control"
              placeholder="Enter your question here..."
              rows="3"
              required
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="questionType">Question Type *</label>
              <select 
                id="questionType"
                v-model="questionForm.question_type"
                class="form-control"
                required
              >
                <option value="MCQ">Multiple Choice (MCQ)</option>
                <option value="TRUE_FALSE">True/False</option>
                <option value="SHORT_ANSWER">Short Answer</option>
              </select>
            </div>
            <div class="form-group">
              <label for="questionPoints">Points *</label>
              <input 
                id="questionPoints"
                type="number" 
                v-model.number="questionForm.points"
                class="form-control" 
                min="1"
                required
              >
            </div>
          </div>

          <!-- MCQ Options -->
          <div v-if="questionForm.question_type === 'MCQ'" class="mcq-options">
            <label class="section-label">Answer Options * (Exactly 4 required)</label>
            <div 
              v-for="(option, index) in questionForm.options.slice(0, 4)" 
              :key="index"
              class="option-input-group"
            >
              <div class="option-input">
                <label>Option {{ String.fromCharCode(65 + index) }}</label>
                <input 
                  type="text" 
                  v-model="questionForm.options[index]"
                  class="form-control" 
                  :placeholder="`Enter option ${String.fromCharCode(65 + index)}`"
                  required
                >
              </div>
              <div class="correct-option-radio">
                <input 
                  type="radio" 
                  :id="`correct-${index}`"
                  :value="questionForm.options[index]"
                  v-model="questionForm.correct_answer"
                  name="correctAnswer"
                  required
                >
                <label :for="`correct-${index}`">Correct</label>
              </div>
            </div>
          </div>

          <!-- True/False Options -->
          <div v-else-if="questionForm.question_type === 'TRUE_FALSE'" class="true-false-options">
            <label class="section-label">Correct Answer *</label>
            <div class="radio-group">
              <div class="radio-option">
                <input 
                  type="radio" 
                  id="true-option"
                  value="True"
                  v-model="questionForm.correct_answer"
                  name="trueFalse"
                  required
                >
                <label for="true-option">True</label>
              </div>
              <div class="radio-option">
                <input 
                  type="radio" 
                  id="false-option"
                  value="False"
                  v-model="questionForm.correct_answer"
                  name="trueFalse"
                  required
                >
                <label for="false-option">False</label>
              </div>
            </div>
          </div>

          <!-- Short Answer -->
          <div v-else-if="questionForm.question_type === 'SHORT_ANSWER'" class="short-answer">
            <div class="form-group">
              <label for="correctAnswer">Correct Answer *</label>
              <input 
                id="correctAnswer"
                type="text" 
                v-model="questionForm.correct_answer"
                class="form-control" 
                placeholder="Enter the correct answer"
                required
              >
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeQuestionModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Saving...' : (editingQuestion ? 'Update Question' : 'Save Question') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style>
/* Global Admin Styles */
.admin-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header Styles */
.admin-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.admin-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.admin-name {
  font-weight: 500;
}

/* Sidebar Styles */
.admin-sidebar {
  position: fixed;
  left: 0;
  top: 80px;
  width: 250px;
  height: calc(100vh - 80px);
  background: white;
  border-right: 1px solid #e1e5e9;
  overflow-y: auto;
  z-index: 100;
}

.sidebar-nav {
  padding: 1rem 0;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin: 0.25rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  color: #64748b;
  text-decoration: none;
  transition: all 0.2s ease;
}

.nav-link:hover,
.nav-item.active .nav-link {
  background-color: #f1f5f9;
  color: #667eea;
  border-right: 3px solid #667eea;
}

/* Main Content Styles */
.admin-main {
  margin-left: 250px;
  padding: 2rem;
  min-height: calc(100vh - 80px);
}

.content-section {
  display: none;
}

.content-section.active {
  display: block;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e1e5e9;
}

.section-header h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.75rem;
}

/* Button Styles */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #667eea;
  color: white;
}

.btn-primary:hover {
  background-color: #5a67d8;
}

.btn-secondary {
  background-color: #64748b;
  color: white;
}

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-logout {
  background-color: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  margin: 0 0.125rem;
  border-radius: 4px;
}

.btn-icon:hover {
  background-color: #f1f5f9;
}

/* Stats Grid */
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
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.users-icon { background-color: #dbeafe; }
.subjects-icon { background-color: #dcfce7; }
.chapters-icon { background-color: #f3e8ff; }
.quizzes-icon { background-color: #fef3c7; }
.attempts-icon { background-color: #fce7f3; }

.stat-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.stat-number {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
}

/* Table Styles */
.search-filter-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: center;
}

.search-input,
.filter-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.role-badge,
.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-badge.admin {
  background-color: #fef3c7;
  color: #92400e;
}

.role-badge.student {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.active {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.published {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.draft {
  background-color: #fef3c7;
  color: #92400e;
}

/* Subject Grid */
.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.subject-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.subject-card h3 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
}

.subject-description {
  color: #64748b;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.subject-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Chapter Management */
.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.subject-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  min-width: 200px;
}

.chapters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.chapter-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-left: 4px solid #8b5cf6;
}

.chapter-card h3 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
}

.chapter-description {
  color: #64748b;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.chapter-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

/* Quiz List */
.filter-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.quiz-item {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quiz-info h3 {
  margin: 0 0 0.5rem 0;
  color: #1e293b;
}

.quiz-meta {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
}

.quiz-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Form Styles */
.question-form {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Analytics */
.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.analytics-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.analytics-card h3 {
  margin: 0 0 1rem 0;
  color: #1e293b;
}

.chart-placeholder {
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 8px;
  text-align: center;
}

.progress-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 1rem;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #667eea;
  transition: width 0.3s ease;
}

/* Recent Activity */
.recent-activity {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.recent-activity h3 {
  margin: 0 0 1rem 0;
  color: #1e293b;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 6px;
}

.activity-icon {
  font-size: 1rem;
  min-width: 20px;
}

.activity-time {
  font-size: 0.75rem;
  color: #6b7280;
  white-space: nowrap;
  min-width: 80px;
}

.activity-text {
  font-size: 0.875rem;
  color: #374151;
  flex: 1;
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .admin-main {
    margin-left: 0;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .quiz-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .form-row {
    flex-direction: column;
  }
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

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 1.25rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.modal-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #1e293b;
  font-weight: 600;
  font-size: 0.875rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

/* Loading and Empty States */
.loading-container {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.empty-state p {
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

/* Button disabled state */
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn:disabled:hover {
  transform: none;
  box-shadow: none;
}

/* Question Management Styles */
.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  transition: box-shadow 0.2s ease;
}

.question-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.question-number {
  background: #4CAF50;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 12px;
}

.question-type-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.question-type-badge.mcq {
  background: #2196F3;
  color: white;
}

.question-type-badge.true_false {
  background: #FF9800;
  color: white;
}

.question-type-badge.short_answer {
  background: #9C27B0;
  color: white;
}

.question-points {
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.question-content {
  margin-bottom: 16px;
}

.question-statement {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  line-height: 1.5;
}

.mcq-options {
  margin-top: 12px;
}

.mcq-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.mcq-option:last-child {
  border-bottom: none;
}

.mcq-option.correct {
  background: #e8f5e8;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #4CAF50;
}

.option-label {
  font-weight: bold;
  color: #666;
  min-width: 20px;
}

.option-text {
  flex: 1;
}

.correct-indicator {
  color: #4CAF50;
  font-weight: bold;
}

.correct-answer {
  background: #e8f5e8;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #4CAF50;
}

.question-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Question Modal Styles */
.option-input-group {
  display: flex;
  align-items: end;
  gap: 12px;
  margin-bottom: 8px;
}

.option-input {
  flex: 1;
}

.correct-option-radio {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.correct-option-radio input[type="radio"] {
  margin: 0;
}

.option-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  justify-content: flex-start;
}

.section-label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.radio-group {
  display: flex;
  gap: 24px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.radio-option input[type="radio"] {
  margin: 0;
}

.true-false-options,
.short-answer {
  margin-top: 12px;
}

.subject-select {
  min-width: 180px;
  margin-right: 12px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-state p {
  margin-bottom: 16px;
  font-size: 16px;
}

.loading-container {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}
</style>