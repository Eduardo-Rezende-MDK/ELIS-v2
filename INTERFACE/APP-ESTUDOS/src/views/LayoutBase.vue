<template>
  <v-app class="w-100">
    <!-- Header Component -->
    <AppHeader 
      @toggle-drawer="drawer = !drawer"
    />
    
    <!-- Navigation Drawer Component -->
    <AppDrawer 
      v-model="drawer"
      @show-notification="showNotification"
    />
    
    <!-- Main Content Area -->
    <v-main>
      <RouterView />
    </v-main>
    
    <!-- Footer Component -->
    <AppFooter v-if="$route.path !== '/trabalhos/novo'" />
    
    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
    >
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import AppDrawer from '../components/AppDrawer.vue'
import AppFooter from '../components/AppFooter.vue'

// Reactive data
const drawer = ref(false)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000
})

// Methods
const showNotification = (text: string, color: string = 'success') => {
  snackbar.value = {
    show: true,
    text,
    color,
    timeout: 3000
  }
}

// Lifecycle
onMounted(() => {
  showNotification('Layout Base carregado com sucesso!', 'success')
})
</script>

<style scoped>
/* Minimal custom styles - using Vuetify utilities where possible */

/* Custom scrollbar for webkit browsers */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}
</style>