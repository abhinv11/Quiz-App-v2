<script setup>
// Home page component logic will go here
</script>

<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            Master Your Knowledge with
            <span class="gradient-text">QuizApp</span>
          </h1>
          <p class="hero-description">
            Test your skills, track your progress, and achieve academic excellence with our comprehensive quiz platform. 
            Perfect for students looking to enhance their learning experience.
          </p>
          <div class="hero-buttons">
            <router-link to="/register" class="btn btn-primary btn-large">
              Get Started Free
            </router-link>
            <router-link to="/login" class="btn btn-secondary btn-large">
              Sign In
            </router-link>
          </div>
          <div class="hero-stats">
            <div class="stat-item">
              <span class="stat-number">1000+</span>
              <span class="stat-label">Students</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">50+</span>
              <span class="stat-label">Subjects</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">500+</span>
              <span class="stat-label">Quizzes</span>
            </div>
          </div>
        </div>
        <div class="hero-image">
          <div class="floating-card card-1">
            <div class="quiz-preview">
              <h4>Mathematics Quiz</h4>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 75%"></div>
              </div>
              <span class="score">Score: 75%</span>
            </div>
          </div>
          <div class="floating-card card-2">
            <div class="quiz-preview">
              <h4>Physics Quiz</h4>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 90%"></div>
              </div>
              <span class="score">Score: 90%</span>
            </div>
          </div>
          <div class="floating-card card-3">
            <div class="quiz-preview">
              <h4>Chemistry Quiz</h4>
              <div class="progress-bar">
                <div class="progress-fill" style="width: 85%"></div>
              </div>
              <span class="score">Score: 85%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="container">
        <div class="section-header">
          <h2>Why Choose QuizApp?</h2>
          <p>Discover the features that make learning engaging and effective</p>
        </div>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">📚</div>
            <h3>Multiple Subjects</h3>
            <p>Access quizzes across various subjects including Mathematics, Physics, Chemistry, and more.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⏱️</div>
            <h3>Timed Quizzes</h3>
            <p>Challenge yourself with time-bound quizzes that simulate real exam conditions.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Performance Analytics</h3>
            <p>Track your progress with detailed analytics and performance insights.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>Instant Results</h3>
            <p>Get immediate feedback on your answers with detailed explanations.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🏆</div>
            <h3>Achievement System</h3>
            <p>Earn achievements and track your learning milestones.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📱</div>
            <h3>Mobile Friendly</h3>
            <p>Access your quizzes anywhere, anytime on any device.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="how-it-works-section">
      <div class="container">
        <div class="section-header">
          <h2>How It Works</h2>
          <p>Get started in just a few simple steps</p>
        </div>
        <div class="steps-container">
          <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>Create Account</h3>
              <p>Sign up for free and create your student profile</p>
            </div>
          </div>
          <div class="step-arrow">→</div>
          <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>Choose Subject</h3>
              <p>Browse and select from our wide range of subjects</p>
            </div>
          </div>
          <div class="step-arrow">→</div>
          <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>Take Quiz</h3>
              <p>Start taking quizzes and test your knowledge</p>
            </div>
          </div>
          <div class="step-arrow">→</div>
          <div class="step-item">
            <div class="step-number">4</div>
            <div class="step-content">
              <h3>Track Progress</h3>
              <p>Monitor your performance and improve continuously</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Popular Subjects Section -->
    <section class="subjects-section">
      <div class="container">
        <div class="section-header">
          <h2>Popular Subjects</h2>
          <p>Explore our most popular quiz categories</p>
        </div>
        <div class="subjects-grid">
          <div class="subject-card">
            <div class="subject-icon">🔢</div>
            <h3>Mathematics</h3>
            <p>Algebra, Geometry, Calculus, Statistics</p>
            <div class="subject-stats">
              <span>120+ Quizzes</span>
              <span>15 Chapters</span>
            </div>
          </div>
          <div class="subject-card">
            <div class="subject-icon">⚛️</div>
            <h3>Physics</h3>
            <p>Mechanics, Thermodynamics, Electromagnetism</p>
            <div class="subject-stats">
              <span>85+ Quizzes</span>
              <span>12 Chapters</span>
            </div>
          </div>
          <div class="subject-card">
            <div class="subject-icon">🧪</div>
            <h3>Chemistry</h3>
            <p>Organic, Inorganic, Physical Chemistry</p>
            <div class="subject-stats">
              <span>95+ Quizzes</span>
              <span>10 Chapters</span>
            </div>
          </div>
          <div class="subject-card">
            <div class="subject-icon">🌍</div>
            <h3>Geography</h3>
            <p>Physical, Human, Economic Geography</p>
            <div class="subject-stats">
              <span>60+ Quizzes</span>
              <span>8 Chapters</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="container">
        <div class="section-header">
          <h2>What Students Say</h2>
          <p>Hear from our successful learners</p>
        </div>
        <div class="testimonials-grid">
          <div class="testimonial-card">
            <div class="testimonial-content">
              <p>"QuizApp helped me improve my math scores significantly. The analytics feature is amazing!"</p>
            </div>
            <div class="testimonial-author">
              <div class="author-avatar">👨‍🎓</div>
              <div class="author-info">
                <h4>Alex Johnson</h4>
                <span>Computer Science Student</span>
              </div>
            </div>
          </div>
          <div class="testimonial-card">
            <div class="testimonial-content">
              <p>"The timed quizzes really helped me prepare for my physics exams. Highly recommended!"</p>
            </div>
            <div class="testimonial-author">
              <div class="author-avatar">👩‍🎓</div>
              <div class="author-info">
                <h4>Sarah Wilson</h4>
                <span>Physics Major</span>
              </div>
            </div>
          </div>
          <div class="testimonial-card">
            <div class="testimonial-content">
              <p>"Great platform with comprehensive coverage of subjects. Made studying fun and interactive."</p>
            </div>
            <div class="testimonial-author">
              <div class="author-avatar">👨‍🎓</div>
              <div class="author-info">
                <h4>Mike Chen</h4>
                <span>Chemistry Student</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2>Ready to Start Learning?</h2>
          <p>Join thousands of students already using QuizApp to enhance their learning experience</p>
          <div class="cta-buttons">
            <router-link to="/register" class="btn btn-primary btn-large">
              Start Learning Now
            </router-link>
            <router-link to="/subjects" class="btn btn-outline btn-large">
              Browse Subjects
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Global Styles */
.home-container {
  width: 100%;
  overflow-x: hidden;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-header h2 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 1rem;
}

.section-header p {
  font-size: 1.1rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto;
}

/* Button Styles */
.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  cursor: pointer;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.1rem;
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
  border-color: #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: white;
  border-color: white;
}

.btn-outline:hover {
  background: white;
  color: #667eea;
  transform: translateY(-2px);
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4rem 0;
  min-height: 90vh;
  display: flex;
  align-items: center;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 1.5rem;
}

.gradient-text {
  background: linear-gradient(45deg, #ffd700, #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 3rem;
}

.hero-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #ffd700;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* Hero Image/Animation */
.hero-image {
  position: relative;
  height: 400px;
}

.floating-card {
  position: absolute;
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  animation: float 6s ease-in-out infinite;
}

.card-1 {
  top: 20px;
  left: 20px;
  animation-delay: 0s;
}

.card-2 {
  top: 120px;
  right: 20px;
  animation-delay: 2s;
}

.card-3 {
  bottom: 20px;
  left: 60px;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.quiz-preview h4 {
  color: #1e293b;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.score {
  color: #667eea;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Features Section */
.features-section {
  padding: 5rem 0;
  background: #f8fafc;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  color: #1e293b;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.feature-card p {
  color: #64748b;
  line-height: 1.6;
}

/* How It Works Section */
.how-it-works-section {
  padding: 5rem 0;
  background: white;
}

.steps-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1000px;
  margin: 0 auto;
}

.step-item {
  text-align: center;
  flex: 1;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 auto 1rem auto;
}

.step-content h3 {
  color: #1e293b;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.step-content p {
  color: #64748b;
  font-size: 0.9rem;
}

.step-arrow {
  font-size: 2rem;
  color: #667eea;
  margin: 0 1rem;
}

/* Subjects Section */
.subjects-section {
  padding: 5rem 0;
  background: #f8fafc;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.subject-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: transform 0.3s ease;
}

.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.subject-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.subject-card h3 {
  color: #1e293b;
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
}

.subject-card p {
  color: #64748b;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.subject-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.subject-stats span {
  font-size: 0.8rem;
  color: #667eea;
  font-weight: 600;
}

/* Testimonials Section */
.testimonials-section {
  padding: 5rem 0;
  background: white;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.testimonial-card {
  background: #f8fafc;
  padding: 2rem;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.testimonial-content p {
  color: #1e293b;
  font-style: italic;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  line-height: 1.6;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.author-avatar {
  font-size: 2.5rem;
}

.author-info h4 {
  color: #1e293b;
  margin-bottom: 0.25rem;
  font-size: 1rem;
}

.author-info span {
  color: #64748b;
  font-size: 0.875rem;
}

/* CTA Section */
.cta-section {
  padding: 5rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.cta-content h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.cta-content p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 2rem;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-stats {
    justify-content: center;
  }
  
  .steps-container {
    flex-direction: column;
    gap: 2rem;
  }
  
  .step-arrow {
    transform: rotate(90deg);
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .section-header h2 {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 1rem;
  }
  
  .hero-section {
    padding: 2rem 0;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .features-grid,
  .subjects-grid,
  .testimonials-grid {
    grid-template-columns: 1fr;
  }
}
</style>
