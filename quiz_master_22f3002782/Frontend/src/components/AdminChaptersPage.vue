<script setup>
import { ref, onMounted } from 'vue'

// Reactive data
const loading = ref(true)

onMounted(() => {
  loading.value = false
})
</script>

<template>
  <div class="admin-chapters-container">
    <div class="chapters-header">
      <h1 class="page-title">Chapter Management</h1>
      <p class="page-subtitle">Manage chapters across all subjects</p>
    </div>

    <div class="coming-soon">
      <h3>Coming Soon</h3>
      <p>Chapter management interface will be implemented here.</p>
      <p>For now, you can manage chapters through the main Admin Dashboard.</p>
    </div>
  </div>
</template>

<style scoped>
.admin-chapters-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.chapters-header {
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

.coming-soon {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
}

.coming-soon h3 {
  color: #374151;
  margin-bottom: 1rem;
}

.coming-soon p {
  color: #64748b;
  margin-bottom: 0.5rem;
}
</style>
