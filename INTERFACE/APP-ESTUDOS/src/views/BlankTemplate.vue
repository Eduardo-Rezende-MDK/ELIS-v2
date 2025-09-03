<template>
  <v-app>
    <!-- Header / App Bar -->
    <v-app-bar
      :elevation="2"
      color="primary"
      dark
      app
    >
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-toolbar-title>
        <v-icon class="mr-2">mdi-file-document-outline</v-icon>
        {{ pageTitle }}
      </v-toolbar-title>
      
      <v-spacer></v-spacer>
      
      <!-- Theme Toggle -->
      <v-btn
        icon
        @click="toggleTheme"
        :title="isDark ? 'Modo Claro' : 'Modo Escuro'"
      >
        <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>
    </v-app-bar>
    
    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      app
      temporary
    >
      <v-list>
        <v-list-item
          prepend-avatar="https://randomuser.me/api/portraits/men/85.jpg"
          title="Usuário"
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
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>
    
    <!-- Main Content Area -->
    <v-main>
      <v-container fluid class="pa-4">
        <!-- Breadcrumbs -->
        <v-breadcrumbs
          :items="breadcrumbs"
          class="pa-0 mb-4"
        >
          <template v-slot:prepend>
            <v-icon size="small">mdi-home</v-icon>
          </template>
        </v-breadcrumbs>
        
        <!-- Page Content -->
        <v-row>
          <v-col cols="12">
            <!-- Welcome Card -->
            <v-card class="mb-6" elevation="2">
              <v-card-title class="d-flex align-center">
                <v-icon class="mr-2" color="primary">mdi-file-document</v-icon>
                Modelo de Página em Branco
              </v-card-title>
              <v-card-text>
                <p class="text-body-1 mb-3">
                  Este é um template básico para criação de novas páginas no projeto ELIS v2.
                  Você pode usar este arquivo como ponto de partida para desenvolver novas funcionalidades.
                </p>
                
                <v-alert
                  type="info"
                  variant="tonal"
                  class="mb-4"
                >
                  <v-alert-title>Como usar este template:</v-alert-title>
                  <ul class="mt-2">
                    <li>Copie este arquivo e renomeie para sua nova página</li>
                    <li>Modifique o conteúdo da seção Main Content</li>
                    <li>Ajuste o título da página na propriedade pageTitle</li>
                    <li>Adicione suas funcionalidades específicas</li>
                  </ul>
                </v-alert>
                
                <v-chip-group>
                  <v-chip color="primary" size="small">
                    <v-icon start>mdi-vuejs</v-icon>
                    Vue 3
                  </v-chip>
                  <v-chip color="success" size="small">
                    <v-icon start>mdi-material-design</v-icon>
                    Vuetify
                  </v-chip>
                  <v-chip color="info" size="small">
                    <v-icon start>mdi-language-typescript</v-icon>
                    TypeScript
                  </v-chip>
                </v-chip-group>
              </v-card-text>
            </v-card>
            
            <!-- Content Area - Customize this section -->
            <v-card elevation="1">
              <v-card-title>
                <v-icon class="mr-2">mdi-pencil</v-icon>
                Área de Conteúdo Personalizável
              </v-card-title>
              <v-card-text>
                <p class="text-body-2 text-medium-emphasis mb-4">
                  Substitua este conteúdo pelo que você deseja exibir em sua página.
                </p>
                
                <!-- Example content - replace with your own -->
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      label="Campo de exemplo"
                      variant="outlined"
                      prepend-inner-icon="mdi-text"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-select
                      label="Seleção de exemplo"
                      :items="['Opção 1', 'Opção 2', 'Opção 3']"
                      variant="outlined"
                      prepend-inner-icon="mdi-format-list-bulleted"
                    ></v-select>
                  </v-col>
                </v-row>
                
                <v-btn
                  color="primary"
                  prepend-icon="mdi-check"
                  @click="showNotification('Ação executada!', 'success')"
                >
                  Botão de Exemplo
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
    
    <!-- Footer -->
    <v-footer
      app
      color="grey-lighten-4"
      class="text-center pa-4"
    >
      <span class="text-body-2">
        {{ currentYear }} ELIS v2 - Template Base
      </span>
    </v-footer>
    
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
import { ref, computed, onMounted } from 'vue'
import { useTheme } from 'vuetify'

// Composables
const theme = useTheme()

// Reactive data
const drawer = ref(false)
const pageTitle = ref('Blank Template')
const snackbar = ref({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000
})

// Computed
const isDark = computed(() => theme.global.current.value.dark)
const currentYear = computed(() => new Date().getFullYear())

// Navigation items
const navigationItems = ref([
  {
    title: 'Layout Base',
    icon: 'mdi-view-dashboard',
    to: '/layout-base'
  },
  {
    title: 'PrimeVue Demo',
    icon: 'mdi-palette',
    to: '/primevue'
  },
  {
    title: 'Vuetify Demo',
    icon: 'mdi-material-design',
    to: '/vuetify'
  },
  {
    title: 'Blank Template',
    icon: 'mdi-file-document-outline',
    to: '/blank-template'
  }
])

// Breadcrumbs
const breadcrumbs = ref([
  {
    title: 'Home',
    disabled: false,
    href: '/layout-base'
  },
  {
    title: 'Blank Template',
    disabled: true
  }
])

// Methods
const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
  showNotification(
    `Tema alterado para ${isDark.value ? 'escuro' : 'claro'}`,
    'info'
  )
}

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
  showNotification('Template carregado com sucesso!', 'success')
})
</script>

<style scoped>
/* Custom styles for the template */
.v-app-bar {
  backdrop-filter: blur(10px);
}

.v-navigation-drawer {
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.v-footer {
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

/* Smooth transitions */
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .v-container {
    padding: 16px 8px;
  }
}

/* Animation for cards */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.v-card {
  animation: fadeInUp 0.6s ease-out;
}
</style>