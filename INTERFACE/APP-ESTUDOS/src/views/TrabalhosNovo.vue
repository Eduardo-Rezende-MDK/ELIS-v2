<template>
  <div class="page-container">
    <!-- Page Header Component -->
    <PageHeader
      :title="pageTitle"
      :features="features"
      :actions="actions"
      @action-click="handleActionClick"
    />

    <!-- Chat Component -->
    <div class="chat-container">
      <!-- Chat Header -->
      <div class="chat-header">
        <div class="d-flex align-center">
          <v-icon class="mr-2" color="primary">mdi-chat</v-icon>
          <span class="chat-title">Assistente IA - Criação de Trabalho</span>
          <v-spacer></v-spacer>
          <v-chip :color="isOnline ? 'success' : 'error'" size="small">
            <v-icon start :icon="isOnline ? 'mdi-circle' : 'mdi-circle-outline'"></v-icon>
            {{ isOnline ? 'Online' : 'Offline' }}
          </v-chip>
        </div>
      </div>
      
      <!-- Messages Area -->
      <div class="chat-messages" ref="messagesContainer">
        <div class="messages-content">
          <div 
            v-for="(message, index) in messages" 
            :key="index" 
            class="message-wrapper"
            :class="{ 'own-message': message.isOwn }"
          >
            <div class="message-bubble" :class="{ 'own-bubble': message.isOwn }">
              <div class="message-content">
                <p class="message-text">{{ message.text }}</p>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>
            </div>
          </div>
          
          <!-- Typing Indicator -->
          <div v-if="isTyping" class="typing-indicator">
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Input Area -->
      <div class="chat-input">
        <div class="input-container">
          <v-text-field
            v-model="newMessage"
            placeholder="Descreva como você quer que seu trabalho seja estruturado..."
            variant="outlined"
            density="compact"
            hide-details
            @keyup.enter="sendMessage"
            :disabled="!isOnline"
            class="message-input"
          >
            <template v-slot:prepend-inner>
              <v-icon color="grey-darken-1">mdi-emoticon-outline</v-icon>
            </template>
          </v-text-field>
          <v-btn
            icon="mdi-send"
            color="primary"
            @click="sendMessage"
            :disabled="!newMessage.trim() || !isOnline"
            size="large"
            class="send-button"
          ></v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'

// Composables
const router = useRouter()

// Reactive data
const loading = ref(false)

// Chat data
const messages = ref([
  {
    text: 'Olá! Vou te ajudar a criar seu trabalho. Como você gostaria que ele fosse estruturado? Conte-me sobre o tema, objetivos e qualquer requisito específico.',
    isOwn: false,
    timestamp: new Date()
  }
])
const newMessage = ref('')
const isOnline = ref(true)
const isTyping = ref(false)
const messagesContainer = ref(null)

// Page configuration
const pageTitle = 'Novo Trabalho'



const features = [
  {
    id: 'step',
    icon: 'mdi-numeric-1-circle',
    value: 'Passo 1',
    label: 'Informações Básicas',
    color: 'primary'
  },
  {
    id: 'required',
    icon: 'mdi-asterisk',
    value: '5 campos',
    label: 'Obrigatórios',
    color: 'warning'
  },
  {
    id: 'save',
    icon: 'mdi-content-save-outline',
    value: 'Auto-save',
    label: 'Salvamento Automático',
    color: 'success'
  }
]

const actions = [
  {
    id: 'diagram',
    label: 'Diagrama',
    icon: 'mdi-chart-timeline-variant',
    outlined: true,
    color: 'primary',
    handler: () => navegarParaDiagrama()
  },
  {
    id: 'cancel',
    label: 'Cancelar',
    icon: 'mdi-close',
    outlined: true,
    color: 'grey',
    handler: () => cancelar()
  },
  {
    id: 'save',
    label: 'Salvar Trabalho',
    icon: 'mdi-content-save',
    color: 'success',
    loading: loading.value,
    handler: () => salvar()
  }
]

// Methods
const salvar = async () => {
  loading.value = true
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Redirect to list after success
    router.push('/trabalhos')
    
  } catch (error) {
    console.error('Erro ao salvar trabalho:', error)
  } finally {
    loading.value = false
  }
}

const cancelar = () => {
  router.push('/trabalhos')
}

const navegarParaDiagrama = () => {
  router.push('/trabalhos/novo/diagrama')
}

const handleActionClick = (action: any) => {
  // Actions are handled by their individual handlers
  console.log('Action clicked:', action.id)
}

// Chat methods
const sendMessage = async () => {
  if (!newMessage.value.trim() || !isOnline.value) return
  
  // Add user message
  messages.value.push({
    text: newMessage.value,
    isOwn: true,
    timestamp: new Date()
  })
  
  const userMsg = newMessage.value
  newMessage.value = ''
  
  // Scroll to bottom
  await nextTick()
  scrollToBottom()
  
  // Simulate typing and response
  setTimeout(() => {
    isTyping.value = true
    scrollToBottom()
  }, 500)
  
  setTimeout(() => {
    isTyping.value = false
    messages.value.push({
      text: generateResponse(userMsg),
      isOwn: false,
      timestamp: new Date()
    })
    nextTick(() => scrollToBottom())
  }, 2000)
}

const generateResponse = (userMessage: string) => {
  const responses = [
    'Excelente! Com base no que você me contou, posso sugerir uma estrutura para seu trabalho. Que tal começarmos pela introdução?',
    'Perfeito! Vou organizar essas informações. Você tem alguma preferência para a metodologia ou formato específico?',
    'Ótimo tema! Para desenvolvermos melhor, você poderia me falar sobre o público-alvo e os objetivos principais?',
    'Entendi suas necessidades. Vamos estruturar isso de forma clara e objetiva. Precisa seguir alguma norma específica (ABNT, APA)?',
    'Muito bom! Com essas informações posso te ajudar a criar um trabalho bem estruturado. Qual é o prazo que temos para a entrega?'
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

const formatTime = (timestamp: Date) => {
  return timestamp.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Lifecycle
onMounted(() => {
  nextTick(() => scrollToBottom())
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: white;
  display: flex;
  flex-direction: column;
}

/* Chat Styles */
.chat-container {
  background-color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  padding-bottom: 80px; /* Space for fixed input */
}

.chat-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
  background-color: white;
  position: sticky;
  top: 0;
  z-index: 10;
}

.chat-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1976d2;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  background-color: white;
  scroll-behavior: smooth;
  min-height: 500px;
}

.messages-content {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.message-wrapper {
  display: flex;
  margin-bottom: 12px;
}

.message-wrapper.own-message {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  background-color: #e3f2fd;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-bubble.own-bubble {
  background-color: #1976d2;
  color: white;
}

.message-content {
  display: flex;
  flex-direction: column;
}

.message-text {
  margin: 0 0 4px 0;
  line-height: 1.4;
  word-wrap: break-word;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  align-self: flex-end;
}

.typing-indicator {
  display: flex;
  align-items: center;
  padding: 12px 16px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #9e9e9e;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  background-color: white;
  border-top: 1px solid #e0e0e0;
  padding: 20px 24px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.input-container {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.message-input {
  flex: 1;
}

.send-button {
  flex-shrink: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .chat-header {
    padding: 16px 20px;
  }
  
  .messages-content {
    padding: 20px;
  }
  
  .chat-input {
    padding: 16px 20px;
  }
  
  .chat-container {
    padding-bottom: 90px; /* More space for mobile */
  }
  
  .message-bubble {
    max-width: 85%;
    padding: 10px 14px;
  }
  
  .chat-title {
    font-size: 1.1rem;
  }
}

@media (max-width: 480px) {
  .chat-header {
    padding: 12px 16px;
  }
  
  .messages-content {
    padding: 16px;
  }
  
  .chat-input {
    padding: 12px 16px;
  }
  
  .chat-container {
    padding-bottom: 100px; /* Even more space for small screens */
  }
  
  .input-container {
    gap: 8px;
  }
}

/* Scrollbar Styling */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>