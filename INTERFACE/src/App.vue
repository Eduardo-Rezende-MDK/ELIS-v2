<template>
  <div id="app">
    <header class="header">
      <h1>🎉 Hello World com Vue.js!</h1>
      <p>Bem-vindo ao ELIS v2 - Plataforma Educacional Inteligente</p>
    </header>
    
    <main class="main-content">
      <div class="welcome-card">
        <h2>{{ message }}</h2>
        <p>Contador: <strong>{{ counter }}</strong></p>
        
        <div class="button-group">
          <button @click="increment" class="btn btn-primary">
            ➕ Incrementar
          </button>
          <button @click="decrement" class="btn btn-secondary">
            ➖ Decrementar
          </button>
          <button @click="reset" class="btn btn-danger">
            🔄 Reset
          </button>
        </div>
      </div>
      
      <div class="input-section">
        <h3>Interação com Vue.js</h3>
        <input 
          v-model="userInput" 
          @keyup.enter="addMessage"
          placeholder="Digite uma mensagem e pressione Enter"
          class="input-field"
        />
        
        <div v-if="messages.length > 0" class="messages">
          <h4>Suas mensagens:</h4>
          <ul>
            <li v-for="(msg, index) in messages" :key="index" class="message-item">
              {{ msg }}
              <button @click="removeMessage(index)" class="btn-remove">❌</button>
            </li>
          </ul>
        </div>
      </div>
      
      <div class="info-section">
        <h3>📋 Informações do Projeto</h3>
        <div class="info-grid">
          <div class="info-card">
            <h4>🚀 Framework</h4>
            <p>Vue.js 3</p>
          </div>
          <div class="info-card">
            <h4>⚡ Build Tool</h4>
            <p>Vite</p>
          </div>
          <div class="info-card">
            <h4>🎨 Estilo</h4>
            <p>CSS Moderno</p>
          </div>
          <div class="info-card">
            <h4>📱 Responsivo</h4>
            <p>Mobile First</p>
          </div>
        </div>
      </div>
    </main>
    
    <footer class="footer">
      <p>© 2025 ELIS v2 - Desenvolvido com ❤️ e Vue.js</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      message: 'Olá, Vue.js está funcionando perfeitamente!',
      counter: 0,
      userInput: '',
      messages: []
    }
  },
  methods: {
    increment() {
      this.counter++
    },
    decrement() {
      this.counter--
    },
    reset() {
      this.counter = 0
    },
    addMessage() {
      if (this.userInput.trim()) {
        this.messages.push(this.userInput.trim())
        this.userInput = ''
      }
    },
    removeMessage(index) {
      this.messages.splice(index, 1)
    }
  },
  mounted() {
    console.log('🎉 Vue.js App montado com sucesso!')
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.header p {
  color: #7f8c8d;
  font-size: 1.2rem;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.welcome-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.welcome-card h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

.welcome-card p {
  font-size: 1.2rem;
  color: #34495e;
  margin-bottom: 2rem;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-primary {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.btn-secondary {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
}

.btn-danger {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.input-section {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.input-section h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.input-field {
  width: 100%;
  padding: 1rem;
  border: 2px solid #ecf0f1;
  border-radius: 10px;
  font-size: 1rem;
  margin-bottom: 1rem;
  transition: border-color 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.messages {
  margin-top: 1.5rem;
}

.messages h4 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.messages ul {
  list-style: none;
}

.message-item {
  background: #f8f9fa;
  padding: 0.8rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-left: 4px solid #3498db;
}

.btn-remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0.2rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.btn-remove:hover {
  background: rgba(231, 76, 60, 0.1);
}

.info-section {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.info-section h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  text-align: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-card {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  padding: 1.5rem;
  border-radius: 15px;
  text-align: center;
  transition: transform 0.3s ease;
}

.info-card:hover {
  transform: translateY(-5px);
}

.info-card h4 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.info-card p {
  color: #7f8c8d;
  font-weight: 600;
}

.footer {
  background: rgba(44, 62, 80, 0.9);
  color: white;
  text-align: center;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
}

/* Responsividade */
@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .header p {
    font-size: 1rem;
  }
  
  .main-content {
    padding: 1rem;
  }
  
  .welcome-card,
  .input-section,
  .info-section {
    padding: 1.5rem;
  }
  
  .button-group {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 200px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>