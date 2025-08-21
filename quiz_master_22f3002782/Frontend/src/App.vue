<script setup>
import NavPage from './components/NavPage.vue'
import FootPage from './components/FootPage.vue'
</script>

<template>
  <div id="app">
    <NavPage />  
    <main class="main-content">
      <RouterView />
    </main>
    <FootPage />
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}
</style>
