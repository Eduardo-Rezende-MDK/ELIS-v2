<template>
  <!-- Navigation Drawer -->
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:model-value', $event)"
    app
    temporary
    location="right"
    class="border-s"
  >
    <v-list>
      <v-list-item
        prepend-avatar="https://randomuser.me/api/portraits/men/85.jpg"
        title="João Silva"
        subtitle="Desenvolvedor"
      ></v-list-item>
    </v-list>
    
    <v-divider></v-divider>
    
    <v-list density="compact" nav>
      <v-list-item
        v-for="item in navigationItems"
        :key="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        :subtitle="item.subtitle"
      ></v-list-item>
    </v-list>
    
    <template v-slot:append>
      <div class="pa-2">
        <v-btn
          block
          color="error"
          variant="outlined"
          prepend-icon="mdi-logout"
          @click="logout"
        >
          Sair
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Props
defineProps<{
  modelValue: boolean
}>()

// Emits
const emit = defineEmits<{
  'update:model-value': [value: boolean]
  'show-notification': [text: string, color?: string]
}>()

// Navigation items
const navigationItems = ref([
  {
    title: 'Dashboard',
    subtitle: 'Visão geral',
    icon: 'mdi-view-dashboard',
    to: '/'
  },
  {
    title: 'PrimeVue Demo',
    subtitle: 'Componentes PrimeVue',
    icon: 'mdi-palette',
    to: '/primevue'
  },
  {
    title: 'Vuetify Demo',
    subtitle: 'Material Design',
    icon: 'mdi-material-design',
    to: '/vuetify'
  },
  {
    title: 'Blank Template',
    subtitle: 'Template modelo',
    icon: 'mdi-file-document-outline',
    to: '/blank-template'
  }
])

// Methods
const logout = () => {
  emit('show-notification', 'Logout realizado com sucesso!', 'success')
  // Aqui você implementaria a lógica de logout
}
</script>