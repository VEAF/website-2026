import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { fullWidth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: () => import('@/views/ResetPasswordView.vue'),
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarView.vue'),
    },
    {
      path: '/calendar/new',
      name: 'event-create',
      component: () => import('@/views/EventEditView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/calendar/:id',
      name: 'event-detail',
      component: () => import('@/views/EventDetailView.vue'),
      props: true,
    },
    {
      path: '/calendar/:id/edit',
      name: 'event-edit',
      component: () => import('@/views/EventEditView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/roster',
      name: 'roster',
      component: () => import('@/views/RosterView.vue'),
    },
    {
      path: '/servers',
      name: 'servers',
      component: () => import('@/views/ServersView.vue'),
    },
    {
      path: '/servers/:serverName',
      name: 'server-detail',
      component: () => import('@/views/ServerDetailView.vue'),
      props: true,
    },
    {
      path: '/user/:id',
      name: 'user-profile',
      component: () => import('@/views/UserProfileView.vue'),
      props: true,
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileEditView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/map/:server',
      name: 'map',
      component: () => import('@/views/MapView.vue'),
      props: true,
    },
    {
      path: '/mission-maker',
      name: 'mission-maker',
      component: () => import('@/views/MissionMakerView.vue'),
    },
    {
      path: '/teamspeak',
      name: 'teamspeak',
      component: () => import('@/views/TeamSpeakView.vue'),
    },
    {
      path: '/office',
      name: 'office',
      component: () => import('@/views/OfficeView.vue'),
    },
    {
      path: '/recruitment/:userId',
      name: 'recruitment',
      component: () => import('@/views/RecruitmentView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/metrics',
      name: 'metrics',
      component: () => import('@/views/MetricsView.vue'),
    },
    {
      path: '/pages/:slug(.*)',
      name: 'page',
      component: () => import('@/views/PageView.vue'),
      props: true,
    },
    // Admin routes
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/admin/DashboardView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/UsersView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/modules',
      name: 'admin-modules',
      component: () => import('@/views/admin/ModulesView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/calendar',
      name: 'admin-calendar',
      component: () => import('@/views/admin/CalendarAdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/pages',
      name: 'admin-pages',
      component: () => import('@/views/admin/PagesView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/files',
      name: 'admin-files',
      component: () => import('@/views/admin/FilesView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/servers',
      name: 'admin-servers',
      component: () => import('@/views/admin/ServersView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/urls',
      name: 'admin-urls',
      component: () => import('@/views/admin/UrlsView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/menu',
      name: 'admin-menu',
      component: () => import('@/views/admin/MenuView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Fetch user if token exists but user not loaded
  if (auth.isAuthenticated && !auth.user) {
    await auth.fetchUser()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'home' }
  }
})

export default router
