<template>
  <v-container fluid class="pa-6">
    <!-- Breadcrumbs -->
    <v-breadcrumbs
      v-if="breadcrumbs && breadcrumbs.length > 0"
      :items="breadcrumbs"
      class="pa-0 mb-4"
    >
      <template v-slot:prepend>
        <v-icon size="small">mdi-home</v-icon>
      </template>
      <template v-slot:divider>
        <v-icon size="small">mdi-chevron-right</v-icon>
      </template>
    </v-breadcrumbs>

    <!-- Header Content -->
    <v-row align="center" class="mb-4">
      <!-- Title -->
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold text-grey-darken-4 mb-0">
          {{ title }}
        </h1>
      </v-col>
    </v-row>

    <!-- Statistics/Features Row -->
    <div v-if="features && features.length > 0" class="d-flex align-center flex-wrap gap-6 mb-4">
      <div
        v-for="feature in features"
        :key="feature.id || feature.text"
        class="d-flex align-center"
      >
        <v-icon
          :color="feature.color || 'grey-darken-1'"
          size="16"
          class="mr-2"
        >
          {{ feature.icon }}
        </v-icon>
        <span class="text-subtitle-1 font-weight-bold text-grey-darken-4 mr-1">
          {{ feature.value || feature.text }}
        </span>
        <span class="text-body-2 text-grey-darken-1">
          {{ feature.label || feature.text }}
        </span>
      </div>
    </div>

    <!-- Right Side - Action Buttons -->
    <v-row v-if="actions && actions.length > 0">
      <v-col cols="12" class="text-right">
        <div class="d-flex justify-end ga-2">
          <v-btn
            v-for="(action, index) in actions"
            :key="action.id || index"
            :variant="action.outlined ? 'outlined' : 'flat'"
            :color="action.color || 'success'"
            :prepend-icon="action.icon"
            :loading="action.loading"
            :class="action.class"
            size="small"
            @click="handleActionClick(action)"
          >
            {{ action.label }}
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Horizontal Divider After Actions -->
    <v-divider class="mt-4"></v-divider>
  </v-container>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

// Types
interface BreadcrumbItem {
  title: string
  href?: string
  disabled?: boolean
}

interface FeatureItem {
  id?: string
  icon: string
  text: string
  label?: string
  value?: string
  color?: string
}

interface ActionItem {
  id?: string
  label: string
  icon?: string
  outlined?: boolean
  loading?: boolean
  class?: string
  color?: string
  handler?: () => void
}

// Props
const props = defineProps<{
  title: string
  breadcrumbs?: BreadcrumbItem[]
  features?: FeatureItem[]
  actions?: ActionItem[]
}>()

// Emits
const emit = defineEmits<{
  'breadcrumb-click': [item: BreadcrumbItem]
  'action-click': [action: ActionItem]
}>()

// Methods
const handleActionClick = (action: ActionItem) => {
  if (action.handler) {
    action.handler()
  } else {
    emit('action-click', action)
  }
}
</script>

<style scoped>
.v-btn {
  text-transform: none;
  font-weight: 500;
  border-radius: 6px;
}

.text-h4 {
  color: #212121;
  font-size: 1.75rem !important;
}

.text-subtitle-1 {
  font-size: 1rem !important;
  line-height: 1.2;
}

.text-body-2 {
  font-size: 0.875rem !important;
  line-height: 1.2;
}
</style>