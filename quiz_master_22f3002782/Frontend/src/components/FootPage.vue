<script setup>
// Footer component logic
</script>

<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <!-- Logo and Description -->
        <div class="footer-section">
          <h3 class="footer-logo">QuizApp</h3>
          <p class="footer-description">
            Enhance your learning experience with our comprehensive quiz platform. 
            Perfect for students looking to test and improve their knowledge.
          </p>
        </div>

        <!-- Quick Links -->
        <div class="footer-section">
          <h4 class="footer-title">Quick Links</h4>
          <ul class="footer-links">
            <li><router-link to="/">Home</router-link></li>
            <li><router-link to="/subjects">Subjects</router-link></li>
            <li><router-link to="/dashboard">Dashboard</router-link></li>
            <li><router-link to="/profile">Profile</router-link></li>
          </ul>
        </div>

        <!-- Support -->
        <div class="footer-section">
          <h4 class="footer-title">Support</h4>
          <ul class="footer-links">
            <li><a href="#help">Help Center</a></li>
            <li><a href="#contact">Contact Us</a></li>
            <li><a href="#faq">FAQ</a></li>
            <li><a href="#terms">Terms of Service</a></li>
          </ul>
        </div>

        <!-- Connect -->
        <div class="footer-section">
          <h4 class="footer-title">Connect</h4>
          <div class="social-links">
            <a href="#" class="social-link">📧</a>
            <a href="#" class="social-link">🐦</a>
            <a href="#" class="social-link">📘</a>
            <a href="#" class="social-link">📷</a>
          </div>
        </div>
      </div>

      <!-- Copyright -->
      <div class="footer-bottom">
        <p>&copy; 2025 QuizApp. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: #1e293b;
  color: white;
  margin-top: auto;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem 1rem 2rem;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3.footer-logo {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

.footer-section h4.footer-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #f1f5f9;
}

.footer-description {
  color: #cbd5e1;
  line-height: 1.6;
  font-size: 0.9rem;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 0.5rem;
}

.footer-links a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.footer-links a:hover {
  color: #667eea;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  display: inline-block;
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.social-link:hover {
  transform: translateY(-2px);
}

.footer-bottom {
  border-top: 1px solid #334155;
  padding-top: 1rem;
  text-align: center;
}

.footer-bottom p {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .footer-container {
    padding: 2rem 1rem 1rem 1rem;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>