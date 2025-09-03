<template>
  <!-- Header / App Bar -->
  <v-app-bar
    :elevation="2"
    color="primary"
    dark
    app
    class="backdrop-blur"
  >
    <v-toolbar-title>
      <img src="/logo-branco.png" alt="Estudaí Logo" class="mr-2" style="width: 48px; height: 48px; vertical-align: middle;">
      Estudaí
    </v-toolbar-title>
    
    <v-spacer></v-spacer>
    
    <v-app-bar-nav-icon @click="$emit('toggle-drawer')"></v-app-bar-nav-icon>
  </v-app-bar>
</template>

<script setup lang="ts">
// Emits
defineEmits<{
  'toggle-drawer': []
}>()
</script>