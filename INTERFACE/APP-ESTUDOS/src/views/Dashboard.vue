<template>
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
            <v-icon class="mr-2" color="primary">mdi-rocket-launch</v-icon>
            Estudaí, sua sala digital
          </v-card-title>
          <v-card-text>
            <p class="text-body-1 mb-3">
              Transforme o jeito de estudar: visualize tarefas, explore conteúdos e acompanhe seu desempenho em tempo real. Mais organização, mais resultados.
            </p>
           
          </v-card-text>
        </v-card>
        
        <!-- Feature Cards -->
        <v-row>
          <v-col cols="12" md="4" v-for="feature in features" :key="feature.id">
            <v-card height="100%" elevation="1" hover>
              <v-card-title class="d-flex align-center">
                <v-avatar :color="feature.color" class="mr-3">
                  <v-icon color="white">{{ feature.icon }}</v-icon>
                </v-avatar>
                {{ feature.title }}
              </v-card-title>
              <v-card-text>
                {{ feature.description }}
              </v-card-text>
              <v-card-actions>
                <v-chip-group>
                  <v-chip
                    v-for="action in feature.actions"
                    :key="action.id"
                    :color="action.color"
                    size="small"
                    @click="action.handler"
                  >
                    <v-icon start>{{ action.icon }}</v-icon>
                    {{ action.label }}
                  </v-chip>
                </v-chip-group>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
        
        <!-- Statistics -->
        <v-row class="mt-6">
          <v-col cols="12">
            <v-card>
              <v-card-title>
                <v-icon class="mr-2">mdi-chart-line</v-icon>
                Estatísticas do Sistema
              </v-card-title>
              <v-card-text>

               
                <v-row>
                  <v-col cols="6" md="3" v-for="stat in statistics" :key="stat.label">
                    <div class="text-center">
             
                      <div class="text-h4 font-weight-bold" :class="stat.color">
                        {{ stat.value }}
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        {{ stat.label }}
                      </div>
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// Composables
const router = useRouter()

// Breadcrumbs
const breadcrumbs = ref([
  {
    title: 'Home',
    disabled: false,
    href: '/'
  },
  {
    title: 'Dashboard',
    disabled: true
  }
])

// Features
const features = ref([
  {
    id: 1,
    title: 'Meus Trabalhos',
    description: 'Aqui você cria, edita e organiza seus trabalhos escolares com praticidade. Visualize conteúdos já feitos, acompanhe seus progressos e mantenha tudo em um só lugar.',
    icon: 'mdi-palette',
    color: 'primary',
    actions: [
      {
        id: 'list-works',
        label: 'Listar',
        icon: 'mdi-format-list-bulleted',
        color: 'primary',
        handler: () => router.push('/trabalhos')
      },
      {
        id: 'create-work',
        label: 'Criar',
        icon: 'mdi-plus-circle',
        color: 'success',
        handler: () => router.push('/trabalhos/novo')
      }
    ]
  },
  {
    id: 2,
    title: 'Vuetify',
    description: 'Framework Material Design com componentes seguindo as diretrizes do Google.',
    icon: 'mdi-material-design',
    color: 'success',
    actions: [
      {
        id: 'list-components',
        label: 'Componentes',
        icon: 'mdi-view-grid',
        color: 'success',
        handler: () => router.push('/vuetify')
      },
      {
        id: 'create-component',
        label: 'Personalizar',
        icon: 'mdi-palette-outline',
        color: 'info',
        handler: () => console.log('Personalizar componente')
      }
    ]
  },
  {
    id: 3,
    title: 'Blank Template',
    description: 'Template em branco para criação rápida de novas páginas no sistema.',
    icon: 'mdi-file-document-outline',
    color: 'warning',
    actions: [
      {
        id: 'list-templates',
        label: 'Ver Templates',
        icon: 'mdi-file-multiple',
        color: 'warning',
        handler: () => router.push('/blank-template')
      },
      {
        id: 'create-template',
        label: 'Novo Template',
        icon: 'mdi-file-plus',
        color: 'orange',
        handler: () => console.log('Criar novo template')
      }
    ]
  }
])

// Statistics
const statistics = ref([
  {
    label: 'Componentes UI',
    value: '500+',
    color: 'text-primary'
  },
  {
    label: 'Páginas Demo',
    value: '4',
    color: 'text-success'
  },
  {
    label: 'Bibliotecas',
    value: '2',
    color: 'text-warning'
  },
  {
    label: 'Templates',
    value: '1',
    color: 'text-info'
  }
])
</script>

<style scoped>
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
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
}
</style>