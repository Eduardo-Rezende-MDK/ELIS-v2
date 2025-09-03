<template>
<v-footer app color="grey-lighten-4" class="text-center d-flex flex-column flex-md-row align-center justify-space-between pa-2 border-t">
<div class="d-flex align-center  mb-md-0">
<v-icon class="mr-2" color="primary">mdi-copyright</v-icon>
<span class="text-body-2">{{ currentYear }} ELIS v2. Todos os direitos reservados.</span>
</div>
</v-footer>
</template>
<script setup lang="ts">
import { computed } from 'vue'
const currentYear = computed(() => new Date().getFullYear())
</script>