<template>
  <v-app>
    <v-main>
      <v-container>
        <div class="vuetify-demo">
          <!-- Header -->
          <v-row class="mb-6">
            <v-col cols="12" class="text-center">
              <h1 class="display-2 mb-4">🎨 Vuetify Demo</h1>
              <p class="subtitle-1">Demonstração dos componentes Vuetify Material Design</p>
            </v-col>
          </v-row>
          
          <!-- Botões -->
          <v-row class="mb-6">
            <v-col cols="12">
              <v-card>
                <v-card-title>
                  <v-icon class="mr-2">mdi-gesture-tap-button</v-icon>
                  Botões Material Design
                </v-card-title>
                <v-card-text>
                  <div class="d-flex flex-wrap ga-2 mb-4">
                    <v-btn color="primary">Primary</v-btn>
                    <v-btn color="secondary">Secondary</v-btn>
                    <v-btn color="success">Success</v-btn>
                    <v-btn color="error">Error</v-btn>
                    <v-btn color="warning">Warning</v-btn>
                    <v-btn color="info">Info</v-btn>
                  </div>
                  
                  <v-divider class="my-4"></v-divider>
                  
                  <div class="d-flex flex-wrap ga-2 mb-4">
                    <v-btn variant="outlined" color="primary">Outlined</v-btn>
                    <v-btn variant="text" color="primary">Text</v-btn>
                    <v-btn variant="tonal" color="primary">Tonal</v-btn>
                    <v-btn variant="elevated" color="primary">Elevated</v-btn>
                  </div>
                  
                  <div class="d-flex flex-wrap ga-2">
                    <v-btn size="x-small">X-Small</v-btn>
                    <v-btn size="small">Small</v-btn>
                    <v-btn size="default">Default</v-btn>
                    <v-btn size="large">Large</v-btn>
                    <v-btn size="x-large">X-Large</v-btn>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Formulários -->
          <v-row class="mb-6">
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>
                  <v-icon class="mr-2">mdi-form-textbox</v-icon>
                  Formulários
                </v-card-title>
                <v-card-text>
                  <v-form ref="form" v-model="valid">
                    <v-text-field
                      v-model="formData.name"
                      label="Nome"
                      variant="outlined"
                      :rules="nameRules"
                      class="mb-3"
                      prepend-inner-icon="mdi-account"
                    ></v-text-field>
                    
                    <v-text-field
                      v-model="formData.email"
                      label="Email"
                      type="email"
                      variant="outlined"
                      :rules="emailRules"
                      class="mb-3"
                      prepend-inner-icon="mdi-email"
                    ></v-text-field>
                    
                    <v-select
                      v-model="formData.framework"
                      :items="frameworks"
                      label="Framework"
                      variant="outlined"
                      class="mb-3"
                      prepend-inner-icon="mdi-code-tags"
                    ></v-select>
                    
                    <v-textarea
                      v-model="formData.message"
                      label="Mensagem"
                      variant="outlined"
                      rows="3"
                      class="mb-3"
                      prepend-inner-icon="mdi-message-text"
                    ></v-textarea>
                    
                    <v-checkbox
                      v-model="formData.agree"
                      label="Aceito os termos e condições"
                      :rules="[v => !!v || 'Você deve aceitar os termos']"
                      class="mb-3"
                    ></v-checkbox>
                    
                    <v-btn 
                      color="primary" 
                      @click="submitForm"
                      :disabled="!valid"
                      prepend-icon="mdi-send"
                    >
                      Enviar Formulário
                    </v-btn>
                  </v-form>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>
                  <v-icon class="mr-2">mdi-table</v-icon>
                  Dados da Tabela
                </v-card-title>
                <v-card-text>
                  <v-data-table
                    :headers="headers"
                    :items="items"
                    :items-per-page="5"
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
                    <template v-slot:item.actions="{ item }">
                      <v-btn
                        icon="mdi-pencil"
                        size="small"
                        variant="text"
                        @click="editItem(item)"
                      ></v-btn>
                      <v-btn
                        icon="mdi-delete"
                        size="small"
                        variant="text"
                        color="error"
                        @click="deleteItem(item)"
                      ></v-btn>
                    </template>
                  </v-data-table>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Cards e Layout -->
          <v-row class="mb-6">
            <v-col cols="12" sm="6" md="4" v-for="card in cards" :key="card.id">
              <v-card class="h-100" elevation="2">
                <v-card-title class="d-flex align-center">
                  <v-icon :icon="card.icon" class="mr-2" :color="card.color"></v-icon>
                  {{ card.title }}
                </v-card-title>
                <v-card-text>
                  {{ card.description }}
                </v-card-text>
                <v-card-actions>
                  <v-btn color="primary" variant="text">Saiba Mais</v-btn>
                  <v-spacer></v-spacer>
                  <v-btn
                    :icon="card.favorite ? 'mdi-heart' : 'mdi-heart-outline'"
                    @click="card.favorite = !card.favorite"
                    :color="card.favorite ? 'red' : 'grey'"
                  ></v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Navegação e Feedback -->
          <v-row class="mb-6">
            <v-col cols="12">
              <v-card>
                <v-card-title>
                  <v-icon class="mr-2">mdi-bell-ring</v-icon>
                  Componentes de Feedback
                </v-card-title>
                <v-card-text>
                  <div class="d-flex flex-wrap ga-2 mb-4">
                    <v-btn @click="showSnackbar('success')" color="success" prepend-icon="mdi-check">Sucesso</v-btn>
                    <v-btn @click="showSnackbar('error')" color="error" prepend-icon="mdi-alert">Erro</v-btn>
                    <v-btn @click="showSnackbar('warning')" color="warning" prepend-icon="mdi-alert-outline">Aviso</v-btn>
                    <v-btn @click="showSnackbar('info')" color="info" prepend-icon="mdi-information">Info</v-btn>
                  </div>
                  
                  <div class="mb-4">
                    <v-btn @click="showDialog" color="primary" prepend-icon="mdi-dialog">Mostrar Dialog</v-btn>
                    <v-btn @click="showBottomSheet" color="secondary" prepend-icon="mdi-dock-bottom" class="ml-2">Bottom Sheet</v-btn>
                  </div>
                  
                  <v-progress-linear
                    v-model="progress"
                    color="primary"
                    height="8"
                    class="mb-4"
                  ></v-progress-linear>
                  
                  <v-slider
                    v-model="progress"
                    label="Progress"
                    min="0"
                    max="100"
                    step="1"
                    thumb-label
                  ></v-slider>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Expansão e Navegação -->
          <v-row class="mb-6">
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>
                  <v-icon class="mr-2">mdi-view-list</v-icon>
                  Lista Expansível
                </v-card-title>
                <v-card-text>
                  <v-expansion-panels>
                    <v-expansion-panel
                      v-for="(item, i) in expansionItems"
                      :key="i"
                      :title="item.title"
                    >
                      <v-expansion-panel-text>
                        {{ item.content }}
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-card>
                <v-card-title>
                  <v-icon class="mr-2">mdi-tab</v-icon>
                  Tabs
                </v-card-title>
                <v-card-text>
                  <v-tabs v-model="tab" color="primary">
                    <v-tab value="tab1">Tab 1</v-tab>
                    <v-tab value="tab2">Tab 2</v-tab>
                    <v-tab value="tab3">Tab 3</v-tab>
                  </v-tabs>
                  
                  <v-tabs-window v-model="tab">
                    <v-tabs-window-item value="tab1">
                      <v-card-text>Conteúdo da Tab 1 com informações importantes.</v-card-text>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="tab2">
                      <v-card-text>Conteúdo da Tab 2 com dados adicionais.</v-card-text>
                    </v-tabs-window-item>
                    <v-tabs-window-item value="tab3">
                      <v-card-text>Conteúdo da Tab 3 com configurações.</v-card-text>
                    </v-tabs-window-item>
                  </v-tabs-window>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-container>
      
      <!-- Snackbar -->
      <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        :timeout="3000"
        location="top"
      >
        {{ snackbar.text }}
        <template v-slot:actions>
          <v-btn variant="text" @click="snackbar.show = false">Fechar</v-btn>
        </template>
      </v-snackbar>
      
      <!-- Dialog -->
      <v-dialog v-model="dialog" max-width="500px">
        <v-card>
          <v-card-title>
            <span class="text-h5">Informações do Formulário</span>
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <v-list-item-title>Nome:</v-list-item-title>
                <v-list-item-subtitle>{{ formData.name || 'Não informado' }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>Email:</v-list-item-title>
                <v-list-item-subtitle>{{ formData.email || 'Não informado' }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>Framework:</v-list-item-title>
                <v-list-item-subtitle>{{ formData.framework || 'Não selecionado' }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>Mensagem:</v-list-item-title>
                <v-list-item-subtitle>{{ formData.message || 'Vazia' }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>Termos:</v-list-item-title>
                <v-list-item-subtitle>{{ formData.agree ? 'Aceitos' : 'Não aceitos' }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="dialog = false">Fechar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      
      <!-- Bottom Sheet -->
      <v-bottom-sheet v-model="bottomSheet">
        <v-card>
          <v-card-title>Bottom Sheet</v-card-title>
          <v-card-text>
            <p>Este é um exemplo de Bottom Sheet do Vuetify.</p>
            <p>Útil para ações secundárias e informações adicionais.</p>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="bottomSheet = false">Fechar</v-btn>
          </v-card-actions>
        </v-card>
      </v-bottom-sheet>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// Dados reativos
const valid = ref(false)
const progress = ref(60)
const tab = ref('tab1')
const dialog = ref(false)
const bottomSheet = ref(false)

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success'
})

const formData = reactive({
  name: '',
  email: '',
  framework: '',
  message: '',
  agree: false
})

// Regras de validação
const nameRules = [
  (v: string) => !!v || 'Nome é obrigatório',
  (v: string) => v.length >= 2 || 'Nome deve ter pelo menos 2 caracteres'
]

const emailRules = [
  (v: string) => !!v || 'Email é obrigatório',
  (v: string) => /.+@.+\..+/.test(v) || 'Email deve ser válido'
]

const frameworks = ['Vue.js', 'React', 'Angular', 'Svelte', 'Solid.js']

const headers = [
  { title: 'Nome', key: 'name', sortable: true },
  { title: 'Categoria', key: 'category', sortable: true },
  { title: 'Preço', key: 'price', sortable: true },
  { title: 'Status', key: 'status', sortable: false },
  { title: 'Ações', key: 'actions', sortable: false }
]

const items = ref([
  { name: 'Produto A', category: 'Categoria 1', price: 'R$ 100,00', status: 'Ativo' },
  { name: 'Produto B', category: 'Categoria 2', price: 'R$ 200,00', status: 'Inativo' },
  { name: 'Produto C', category: 'Categoria 1', price: 'R$ 150,00', status: 'Ativo' },
  { name: 'Produto D', category: 'Categoria 3', price: 'R$ 300,00', status: 'Pendente' },
  { name: 'Produto E', category: 'Categoria 2', price: 'R$ 250,00', status: 'Ativo' }
])

const cards = ref([
  {
    id: 1,
    title: 'Material Design',
    description: 'Componentes seguindo as diretrizes do Google Material Design 3.',
    icon: 'mdi-palette',
    color: 'primary',
    favorite: false
  },
  {
    id: 2,
    title: 'Responsivo',
    description: 'Layout totalmente responsivo para todos os dispositivos.',
    icon: 'mdi-responsive',
    color: 'success',
    favorite: true
  },
  {
    id: 3,
    title: 'Customizável',
    description: 'Temas e cores facilmente customizáveis via SASS.',
    icon: 'mdi-cog',
    color: 'warning',
    favorite: false
  }
])

const expansionItems = [
  {
    title: 'Instalação',
    content: 'Para instalar o Vuetify, use: npm install vuetify'
  },
  {
    title: 'Configuração',
    content: 'Configure o Vuetify no seu main.ts seguindo a documentação oficial.'
  },
  {
    title: 'Componentes',
    content: 'O Vuetify oferece mais de 100 componentes Material Design prontos para uso.'
  }
]

// Métodos
const submitForm = () => {
  if (valid.value) {
    showSnackbar('success', 'Formulário enviado com sucesso!')
    dialog.value = true
  } else {
    showSnackbar('error', 'Preencha todos os campos corretamente')
  }
}

const showSnackbar = (color: string, text?: string) => {
  const messages = {
    success: text || 'Operação realizada com sucesso!',
    error: text || 'Erro ao processar solicitação.',
    warning: text || 'Atenção: Verifique os dados inseridos.',
    info: text || 'Informação importante.'
  }
  
  snackbar.color = color
  snackbar.text = messages[color as keyof typeof messages]
  snackbar.show = true
}

const showDialog = () => {
  dialog.value = true
}

const showBottomSheet = () => {
  bottomSheet.value = true
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Ativo': return 'success'
    case 'Inativo': return 'error'
    case 'Pendente': return 'warning'
    default: return 'info'
  }
}

const editItem = (item: any) => {
  showSnackbar('info', `Editando: ${item.name}`)
}

const deleteItem = (item: any) => {
  showSnackbar('warning', `Excluindo: ${item.name}`)
}
</script>

<style scoped>
.vuetify-demo {
  padding: 1rem;
}

.display-2 {
  font-size: 2.5rem !important;
  font-weight: 300;
  line-height: 1.2;
}

.subtitle-1 {
  font-size: 1rem !important;
  font-weight: 400;
  line-height: 1.75;
}

.h-100 {
  height: 100%;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .display-2 {
    font-size: 2rem !important;
  }
  
  .d-flex.flex-wrap {
    flex-direction: column;
  }
  
  .d-flex.flex-wrap .v-btn {
    margin-bottom: 0.5rem;
  }
}
</style>