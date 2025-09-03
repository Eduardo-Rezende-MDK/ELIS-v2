<template>
  <div class="page-container">
    <!-- Page Header Component -->
    <PageHeader
      :title="pageTitle"
      :features="features"
      :actions="actions"
      @action-click="handleActionClick"
    />

    <!-- Step by Step Content -->
    <v-container fluid class="pa-6">
      <div class="steps-content">
        <v-list class="pa-0">
          <v-list-item
            v-for="(step, index) in steps"
            :key="index"
            class="step-item mb-3"
          >
            <v-list-item-title class="text-h6 mb-2">
              {{ step.title }}
            </v-list-item-title>
            
            <v-list-item-subtitle class="text-body-1 step-description">
              {{ step.description }}
            </v-list-item-subtitle>
            
            <template v-slot:append v-if="step.completed">
              <v-icon color="success">mdi-check-circle</v-icon>
            </template>
          </v-list-item>
        </v-list>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../components/PageHeader.vue'

// Composables
const router = useRouter()

// Reactive data
const loading = ref(false)

// Page configuration
const pageTitle = 'Passos do Trabalho'

// Steps data
const steps = ref([
  {
    title: 'Passo 1: Definição do Tema',
    description: 'Solicitar ao usuário que informe o tema desejado para o trabalho universitário.',
    completed: false
  },
  {
    title: 'Passo 2: Enriquecimento Temático Abrangente',
    description: 'Desenvolver um mapeamento completo do universo relacionado ao tema, incluindo assuntos correlacionados, conexões interdisciplinares, contextos históricos, aplicações práticas, tendências atuais, debates acadêmicos e tópicos complementares que ampliem a compreensão do assunto.',
    completed: false
  },
  {
    title: 'Passo 3: Geração de Conteúdo',
    description: 'A IA processará o tema informado e gerará um resumo conciso sobre o assunto.',
    completed: false
  },
  {
    title: 'Passo 4: Apresentação do Resumo',
    description: 'Apresentar ao usuário o resumo gerado pela IA sobre o tema escolhido.',
    completed: false
  },
  {
    title: 'Passo 5: Confirmação do Usuário',
    description: 'Pedir confirmação ao usuário se o assunto apresentado está correto e corresponde ao desejado.',
    completed: false
  },
  {
    title: 'Passo 6: Desenvolvimento do Trabalho',
    description: 'Após confirmação, prosseguir com o desenvolvimento completo do trabalho universitário.',
    completed: false
  },
  {
    title: 'Passo 7: Definição de Requisitos Acadêmicos',
    description: 'Estabelecer número de páginas exigidas, normas de formatação (ABNT, APA, Vancouver), e critérios de avaliação específicos.',
    completed: false
  },
  {
    title: 'Passo 8: Estruturação da Dissertação',
    description: 'Organizar a estrutura completa incluindo introdução, desenvolvimento, conclusão, referências bibliográficas e anexos.',
    completed: false
  },
  {
    title: 'Passo 9: Formatação de Citações e Referências',
    description: 'Aplicar formatação adequada para citações diretas, indiretas e referências bibliográficas conforme norma escolhida.',
    completed: false
  },
  {
    title: 'Passo 10: Revisão Ortográfica e Gramatical',
    description: 'Realizar correção ortográfica, gramatical e de concordância em todo o texto do trabalho.',
    completed: false
  },
  {
    title: 'Passo 11: Verificação de Plágio',
    description: 'Executar verificação de originalidade do conteúdo e ajustar trechos que possam configurar plágio.',
    completed: false
  },
  {
    title: 'Passo 12: Definição de Modalidade de Trabalho',
    description: 'Determinar se o trabalho será individual ou em grupo, definir número de participantes e distribuição de responsabilidades.',
    completed: false
  },
  {
    title: 'Passo 13: Configuração da Ferramenta AutorText',
    description: 'Ativar e configurar a ferramenta de texto autoral AutorText para garantir originalidade e autenticidade do conteúdo produzido.',
    completed: false
  },
  {
    title: 'Passo 14: Implementação da Ferramenta QR Code Multimídia',
    description: 'Desenvolver e configurar a ferramenta QRConnect para gerar códigos QR personalizáveis que vinculem trabalhos impressos a conteúdos multimídia (vídeos, áudios, imagens interativas) e experiências de realidade aumentada, incluindo personalização de design e rastreamento de métricas de acesso.',
    completed: false
  },
  {
    title: 'Passo 15: Configuração da Ferramenta de Modo Áudio',
    description: 'Ativar e configurar a ferramenta VoiceMode que permite interação por voz sem necessidade de digitar ou ler, oferecendo funcionalidades de fala e escuta para comunicação verbal e recebimento de respostas em áudio.',
    completed: false
  },
  {
    title: 'Passo 16: Implementação da Ferramenta de Aprendizado Eficaz',
    description: 'Desenvolver e configurar a ferramenta LearnSmart que apresenta modelo didático interativo com explicações progressivas, conexões contextuais, exemplos práticos, quizzes de verificação, feedback personalizado e interface intuitiva para promover compreensão profunda em vez de reprodução superficial de informações.',
    completed: false
  },
  {
    title: 'Passo 17: Configuração da Ferramenta de Revisão Colaborativa',
    description: 'Implementar e configurar a ferramenta ReviewPro que oferece funcionalidades completas para análise, comentários e edição colaborativa de documentos, com usabilidade otimizada tanto para usuários independentes quanto para equipes de trabalho em grupo.',
    completed: false
  },
  {
    title: 'Passo 18: Implementação do Sistema de Gerenciamento de Mídia',
    description: 'Desenvolver e configurar a ferramenta MediaManager que oferece sistema eficiente para geração, busca, armazenamento, organização, edição e recuperação rápida de arquivos multimídia, incluindo funcionalidades avançadas para criação e pesquisa de imagens.',
    completed: false
  },
  {
    title: 'Passo 19: Configuração da Ferramenta de Impressão e Exportação PDF',
    description: 'Implementar e configurar a ferramenta PrintExport que oferece exportação em alta qualidade para PDF, integração com repositórios Git, compatibilidade com plataformas de compartilhamento, interface intuitiva, manutenção de formatação original, processamento rápido, suporte a múltiplos formatos e segurança para documentos confidenciais.',
    completed: false
  },
  {
    title: 'Passo 20: Implementação da Galeria de Templates Visuais',
    description: 'Desenvolver e configurar a ferramenta TemplateGallery com interface intuitiva que prioriza a exibição e seleção de templates de filtros visuais, oferecendo galeria organizada com pré-visualizações, categorização por estilos, busca rápida e aplicação instantânea de filtros, minimizando a necessidade de edição manual de texto.',
    completed: false
  },
  {
    title: 'Passo 21: Finalização e Entrega',
    description: 'Preparar documento final, definir cronograma de entrega e realizar submissão conforme diretrizes acadêmicas.',
    completed: false
  }
])

const features = [
  {
    id: 'steps',
    icon: 'mdi-format-list-numbered',
    value: '21 Passos',
    label: 'Estrutura Sequencial',
    color: 'primary'
  },
  {
    id: 'progress',
    icon: 'mdi-progress-check',
    value: 'Progresso',
    label: 'Acompanhamento',
    color: 'info'
  },
  {
    id: 'customizable',
    icon: 'mdi-pencil',
    value: 'Editável',
    label: 'Personalização',
    color: 'success'
  }
]

const actions = [
  {
    id: 'back',
    label: 'Voltar',
    icon: 'mdi-arrow-left',
    outlined: true,
    color: 'grey',
    handler: () => voltar()
  },
  {
    id: 'save-diagram',
    label: 'Salvar Diagrama',
    icon: 'mdi-content-save',
    color: 'success',
    loading: loading.value,
    handler: () => salvarDiagrama()
  }
]

// Methods
const salvarDiagrama = async () => {
  loading.value = true
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Show success message or redirect
    console.log('Diagrama salvo com sucesso!')
    
  } catch (error) {
    console.error('Erro ao salvar diagrama:', error)
  } finally {
    loading.value = false
  }
}

const voltar = () => {
  router.push('/trabalhos/novo')
}

const handleActionClick = (action: any) => {
  // Actions are handled by their individual handlers
  console.log('Action clicked:', action.id)
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: white;
}

.steps-content {
  max-width: 1200px;
  margin: 0 auto;
  min-height: 400px;
}

.step-item {
  border-radius: 8px;
  padding: 16px;
  transition: background-color 0.2s ease;
}

.step-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.step-description {
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: unset !important;
  max-width: none !important;
  width: auto !important;
  height: auto !important;
  max-height: none !important;
  line-height: 1.5 !important;
  word-wrap: break-word !important;
  word-break: break-word !important;
  display: block !important;
}

/* Responsive Design */
@media (max-width: 768px) {
  .steps-content {
    min-height: 300px;
    padding: 0 8px;
  }
  
  .step-item {
    padding: 12px 8px;
  }
  
  .step-item .v-list-item-title {
    font-size: 1.1rem !important;
    line-height: 1.3 !important;
    white-space: normal !important;
    word-wrap: break-word !important;
  }
  
  .step-item .v-list-item-subtitle {
    font-size: 0.9rem !important;
    line-height: 1.4 !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow: visible !important;
    text-overflow: unset !important;
  }
}

@media (max-width: 480px) {
  .steps-content {
    padding: 0 4px;
  }
  
  .step-item {
    padding: 10px 6px;
  }
  
  .step-item .v-avatar {
    margin-right: 8px !important;
  }
  
  .step-item .v-list-item-title {
    font-size: 1rem !important;
    margin-bottom: 4px !important;
  }
  
  .step-item .v-list-item-subtitle {
    font-size: 0.85rem !important;
  }
}
</style>