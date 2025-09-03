<template>
  <div class="primevue-demo">
    <div class="demo-header">
      <h1>🎨 PrimeVue Demo</h1>
      <p>Demonstração dos componentes PrimeVue com tema Aura</p>
    </div>
    
    <!-- Seções de componentes -->
    <div class="demo-sections">
      <!-- Botões -->
      <Card class="demo-card">
        <template #title>
          <i class="pi pi-palette"></i>
          Botões PrimeVue
        </template>
        <template #content>
          <div class="flex flex-wrap gap-2 mb-4">
            <Button label="Primary" />
            <Button label="Secondary" severity="secondary" />
            <Button label="Success" severity="success" />
            <Button label="Info" severity="info" />
            <Button label="Warning" severity="warning" />
            <Button label="Danger" severity="danger" />
          </div>
          
          <div class="flex flex-wrap gap-2">
            <Button label="Outlined" outlined />
            <Button label="Text" text />
            <Button label="Raised" raised />
            <Button label="Rounded" rounded />
          </div>
        </template>
      </Card>
      
      <!-- Formulários -->
      <Card class="demo-card">
        <template #title>
          <i class="pi pi-file-edit"></i>
          Formulários
        </template>
        <template #content>
          <div class="flex flex-column gap-3">
            <div class="field">
              <label for="input-text">Input Text</label>
              <InputText id="input-text" v-model="inputValue" placeholder="Digite algo..." class="w-full" />
              <small>Valor: {{ inputValue }}</small>
            </div>
            
            <div class="field">
              <label for="dropdown">Dropdown</label>
              <Dropdown 
                id="dropdown"
                v-model="selectedOption" 
                :options="options" 
                optionLabel="name" 
                placeholder="Selecione uma opção"
                class="w-full"
              />
            </div>
            
            <div class="field">
              <label for="calendar">Calendar</label>
              <Calendar 
                id="calendar"
                v-model="dateValue" 
                placeholder="Selecione uma data"
                class="w-full"
                showIcon
              />
            </div>
            
            <div class="field">
              <label for="textarea">Textarea</label>
              <Textarea 
                id="textarea"
                v-model="textareaValue" 
                placeholder="Digite sua mensagem..."
                rows="3"
                class="w-full"
              />
            </div>
            
            <div class="field-checkbox">
              <Checkbox v-model="checkboxValue" inputId="checkbox" binary />
              <label for="checkbox">Aceito os termos e condições</label>
            </div>
            
            <Button 
              label="Enviar Formulário" 
              icon="pi pi-send" 
              @click="submitForm"
              :disabled="!canSubmit"
            />
          </div>
        </template>
      </Card>
      
      <!-- Dados -->
      <Card class="demo-card">
        <template #title>
          <i class="pi pi-table"></i>
          Tabela de Dados
        </template>
        <template #content>
          <DataTable :value="products" tableStyle="min-width: 50rem" paginator :rows="5">
            <Column field="name" header="Nome" sortable></Column>
            <Column field="category" header="Categoria" sortable></Column>
            <Column field="price" header="Preço" sortable>
              <template #body="slotProps">
                {{ formatCurrency(slotProps.data.price) }}
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="slotProps">
                <Tag 
                  :value="slotProps.data.status" 
                  :severity="getStatusSeverity(slotProps.data.status)"
                />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <!-- Feedback -->
      <Card class="demo-card">
        <template #title>
          <i class="pi pi-bell"></i>
          Componentes de Feedback
        </template>
        <template #content>
          <div class="flex flex-wrap gap-2 mb-4">
            <Button label="Toast Success" severity="success" @click="showToast('success')" />
            <Button label="Toast Info" severity="info" @click="showToast('info')" />
            <Button label="Toast Warning" severity="warning" @click="showToast('warn')" />
            <Button label="Toast Error" severity="danger" @click="showToast('error')" />
          </div>
          
          <div class="mb-4">
            <label>Progress: {{ progressValue }}%</label>
            <ProgressBar :value="progressValue" class="mb-2" />
            <Slider v-model="progressValue" class="w-full" />
          </div>
          
          <div class="flex flex-wrap gap-2">
            <Button label="Mostrar Dialog" @click="showDialog" />
            <Button label="Confirmar Ação" severity="warning" @click="showConfirm" />
          </div>
        </template>
      </Card>
      
      <!-- Layout -->
      <Card class="demo-card">
        <template #title>
          <i class="pi pi-th-large"></i>
          Componentes de Layout
        </template>
        <template #content>
          <div class="grid">
            <div class="col-12 md:col-4">
              <Panel header="Panel 1" toggleable>
                <p>Conteúdo do painel 1 com toggle funcional.</p>
              </Panel>
            </div>
            <div class="col-12 md:col-4">
              <Panel header="Panel 2" toggleable>
                <p>Conteúdo do painel 2 com informações importantes.</p>
              </Panel>
            </div>
            <div class="col-12 md:col-4">
              <Panel header="Panel 3" toggleable>
                <p>Conteúdo do painel 3 com dados adicionais.</p>
              </Panel>
            </div>
          </div>
          
          <Divider />
          
          <div class="flex flex-wrap gap-2">
            <Chip label="Vue.js" icon="pi pi-check" />
            <Chip label="PrimeVue" icon="pi pi-star" removable />
            <Chip label="TypeScript" icon="pi pi-code" />
            <Chip label="Vite" icon="pi pi-bolt" removable />
          </div>
        </template>
      </Card>
    </div>
    
    <!-- Toast -->
    <Toast />
    
    <!-- Dialog -->
    <Dialog 
      v-model:visible="dialogVisible" 
      modal 
      header="Informações do Formulário"
      :style="{ width: '450px' }"
    >
      <div class="flex flex-column gap-3">
        <div><strong>Input:</strong> {{ inputValue || 'Vazio' }}</div>
        <div><strong>Opção:</strong> {{ selectedOption?.name || 'Nenhuma' }}</div>
        <div><strong>Data:</strong> {{ dateValue ? formatDate(dateValue) : 'Não selecionada' }}</div>
        <div><strong>Mensagem:</strong> {{ textareaValue || 'Vazia' }}</div>
        <div><strong>Checkbox:</strong> {{ checkboxValue ? 'Marcado' : 'Desmarcado' }}</div>
      </div>
      <template #footer>
        <Button label="Fechar" @click="dialogVisible = false" />
      </template>
    </Dialog>
    
    <!-- Confirm Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

// Componentes PrimeVue
import Button from 'primevue/button'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import ProgressBar from 'primevue/progressbar'
import Slider from 'primevue/slider'
import Dialog from 'primevue/dialog'
import ConfirmDialog from 'primevue/confirmdialog'
import Panel from 'primevue/panel'
import Divider from 'primevue/divider'
import Chip from 'primevue/chip'

// Composables
const toast = useToast()
const confirm = useConfirm()

// Dados reativos
const inputValue = ref('')
const selectedOption = ref()
const dateValue = ref()
const textareaValue = ref('')
const checkboxValue = ref(false)
const progressValue = ref(60)
const dialogVisible = ref(false)

// Opções do dropdown
const options = ref([
  { name: 'Vue.js', code: 'vue' },
  { name: 'React', code: 'react' },
  { name: 'Angular', code: 'angular' },
  { name: 'Svelte', code: 'svelte' }
])

// Dados da tabela
const products = ref([
  { name: 'Produto A', category: 'Categoria 1', price: 100, status: 'Ativo' },
  { name: 'Produto B', category: 'Categoria 2', price: 200, status: 'Inativo' },
  { name: 'Produto C', category: 'Categoria 1', price: 150, status: 'Ativo' },
  { name: 'Produto D', category: 'Categoria 3', price: 300, status: 'Pendente' },
  { name: 'Produto E', category: 'Categoria 2', price: 250, status: 'Ativo' },
  { name: 'Produto F', category: 'Categoria 1', price: 180, status: 'Inativo' }
])

// Computed
const canSubmit = computed(() => {
  return inputValue.value && selectedOption.value && checkboxValue.value
})

// Métodos
const submitForm = () => {
  if (canSubmit.value) {
    showToast('success', 'Formulário enviado com sucesso!')
    showDialog()
  } else {
    showToast('error', 'Preencha todos os campos obrigatórios')
  }
}

const showToast = (severity: string, detail?: string) => {
  const messages = {
    success: detail || 'Operação realizada com sucesso!',
    info: detail || 'Informação importante.',
    warn: detail || 'Atenção: Verifique os dados inseridos.',
    error: detail || 'Erro ao processar solicitação.'
  }
  
  toast.add({
    severity,
    summary: severity.charAt(0).toUpperCase() + severity.slice(1),
    detail: messages[severity as keyof typeof messages],
    life: 3000
  })
}

const showDialog = () => {
  dialogVisible.value = true
}

const showConfirm = () => {
  confirm.require({
    message: 'Tem certeza que deseja executar esta ação?',
    header: 'Confirmação',
    icon: 'pi pi-exclamation-triangle',
    rejectClass: 'p-button-secondary p-button-outlined',
    rejectLabel: 'Cancelar',
    acceptLabel: 'Confirmar',
    accept: () => {
      showToast('success', 'Ação confirmada!')
    },
    reject: () => {
      showToast('info', 'Ação cancelada')
    }
  })
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('pt-BR').format(date)
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Ativo': return 'success'
    case 'Inativo': return 'danger'
    case 'Pendente': return 'warning'
    default: return 'info'
  }
}
</script>

<style scoped>
.primevue-demo {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.demo-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
}

.demo-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2.5rem;
}

.demo-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.demo-card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field label {
  font-weight: 600;
  color: #374151;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.col-12 {
  grid-column: span 12;
}

@media (min-width: 768px) {
  .col-md-4 {
    grid-column: span 4;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .primevue-demo {
    padding: 1rem;
  }
  
  .demo-header {
    padding: 1.5rem;
  }
  
  .demo-header h1 {
    font-size: 2rem;
  }
  
  .flex {
    flex-direction: column;
  }
  
  .flex-wrap {
    flex-wrap: nowrap;
  }
}
</style>