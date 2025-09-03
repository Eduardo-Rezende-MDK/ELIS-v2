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

    <!-- Page Header -->
    <v-row class="mb-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-format-list-bulleted</v-icon>
              Lista de Trabalhos
            </div>
            <v-btn
              color="success"
              prepend-icon="mdi-plus"
              @click="$router.push('/trabalhos/novo')"
            >
              Novo Trabalho
            </v-btn>
          </v-card-title>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row class="mb-4">
      <v-col cols="12" md="4">
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Pesquisar trabalhos"
          variant="outlined"
          density="compact"
          clearable
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="statusFilter"
          :items="statusOptions"
          label="Status"
          variant="outlined"
          density="compact"
          clearable
        ></v-select>
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="materiaFilter"
          :items="materiaOptions"
          label="Matéria"
          variant="outlined"
          density="compact"
          clearable
        ></v-select>
      </v-col>
    </v-row>

    <!-- Data Table -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-data-table
            :headers="headers"
            :items="filteredTrabalhos"
            :search="search"
            :loading="loading"
            class="elevation-1"
          >
            <template v-slot:item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
              >
                {{ item.status }}
              </v-chip>
            </template>
            
            <template v-slot:item.dataEntrega="{ item }">
              {{ formatDate(item.dataEntrega) }}
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn-group variant="text" size="small">
                <v-btn
                  icon="mdi-eye"
                  color="info"
                  @click="visualizar(item)"
                  :title="'Visualizar ' + item.titulo"
                ></v-btn>
                <v-btn
                  icon="mdi-pencil"
                  color="warning"
                  @click="editar(item)"
                  :title="'Editar ' + item.titulo"
                ></v-btn>
                <v-btn
                  icon="mdi-delete"
                  color="error"
                  @click="excluir(item)"
                  :title="'Excluir ' + item.titulo"
                ></v-btn>
              </v-btn-group>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Confirmar Exclusão</v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir o trabalho "{{ itemToDelete?.titulo }}"?
          Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="deleteDialog = false">
            Cancelar
          </v-btn>
          <v-btn color="error" variant="text" @click="confirmDelete">
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// Composables
const router = useRouter()

// Reactive data
const loading = ref(false)
const search = ref('')
const statusFilter = ref(null)
const materiaFilter = ref(null)
const deleteDialog = ref(false)
const itemToDelete = ref(null)

// Breadcrumbs
const breadcrumbs = ref([
  {
    title: 'Home',
    disabled: false,
    href: '/'
  },
  {
    title: 'Trabalhos',
    disabled: true
  }
])

// Table headers
const headers = ref([
  { title: 'Título', key: 'titulo', sortable: true },
  { title: 'Matéria', key: 'materia', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Data Entrega', key: 'dataEntrega', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center' }
])

// Filter options
const statusOptions = ref([
  'Rascunho',
  'Em Andamento',
  'Concluído',
  'Entregue'
])

const materiaOptions = ref([
  'Matemática',
  'Português',
  'História',
  'Geografia',
  'Ciências',
  'Inglês',
  'Educação Física',
  'Artes'
])

// Sample data
const trabalhos = ref([
  {
    id: 1,
    titulo: 'Redação sobre Meio Ambiente',
    materia: 'Português',
    status: 'Em Andamento',
    dataEntrega: '2024-02-15',
    descricao: 'Redação dissertativa sobre preservação ambiental'
  },
  {
    id: 2,
    titulo: 'Exercícios de Álgebra',
    materia: 'Matemática',
    status: 'Concluído',
    dataEntrega: '2024-02-10',
    descricao: 'Lista de exercícios sobre equações do 2º grau'
  },
  {
    id: 3,
    titulo: 'Pesquisa sobre Segunda Guerra',
    materia: 'História',
    status: 'Rascunho',
    dataEntrega: '2024-02-20',
    descricao: 'Pesquisa sobre as causas da Segunda Guerra Mundial'
  }
])

// Computed
const filteredTrabalhos = computed(() => {
  let filtered = trabalhos.value
  
  if (statusFilter.value) {
    filtered = filtered.filter(item => item.status === statusFilter.value)
  }
  
  if (materiaFilter.value) {
    filtered = filtered.filter(item => item.materia === materiaFilter.value)
  }
  
  return filtered
})

// Methods
const getStatusColor = (status: string) => {
  const colors = {
    'Rascunho': 'grey',
    'Em Andamento': 'warning',
    'Concluído': 'success',
    'Entregue': 'primary'
  }
  return colors[status] || 'grey'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('pt-BR')
}

const visualizar = (item: any) => {
  router.push(`/trabalhos/${item.id}`)
}

const editar = (item: any) => {
  router.push(`/trabalhos/${item.id}/editar`)
}

const excluir = (item: any) => {
  itemToDelete.value = item
  deleteDialog.value = true
}

const confirmDelete = () => {
  if (itemToDelete.value) {
    const index = trabalhos.value.findIndex(t => t.id === itemToDelete.value.id)
    if (index > -1) {
      trabalhos.value.splice(index, 1)
    }
  }
  deleteDialog.value = false
  itemToDelete.value = null
}

// Lifecycle
onMounted(() => {
  loading.value = true
  // Simulate API call
  setTimeout(() => {
    loading.value = false
  }, 1000)
})
</script>

<style scoped>
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
}
</style>