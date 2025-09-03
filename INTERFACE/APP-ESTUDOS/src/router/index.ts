import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('../views/LayoutBase.vue'),
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/Dashboard.vue'),
        },
        {
          path: 'primevue',
          name: 'primevue',
          component: () => import('../views/PrimeVueDemo.vue'),
        },
        {
          path: 'vuetify',
          name: 'vuetify',
          component: () => import('../views/VuetifyDemo.vue'),
        },
        {
          path: 'blank-template',
          name: 'blank-template',
          component: () => import('../views/BlankTemplate.vue'),
        },
        {
          path: 'trabalhos',
          name: 'trabalhos-list',
          component: () => import('../views/TrabalhosList.vue'),
        },
        {
          path: 'trabalhos/novo',
          name: 'trabalhos-novo',
          component: () => import('../views/TrabalhosNovo.vue'),
        },
        {
          path: 'trabalhos/novo/diagrama',
          name: 'trabalhos-novo-diagrama',
          component: () => import('../views/TrabalhosNovoDiagrama.vue'),
        },
      ],
    },
  ],
})

export default router
