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
      path: '/reset-password/:token',
      name: 'reset-password-confirm',
      component: () => import('@/views/ResetPasswordConfirmView.vue'),
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/CalendarView.vue'),
      meta: {
        fullWidth: true,
        breadcrumb: [{ label: 'Calendrier', icon: 'fa-solid fa-calendar-days' }],
      },
    },
    {
      path: '/calendar/new',
      name: 'event-create',
      component: () => import('@/views/EventEditView.vue'),
      meta: {
        requiresAuth: true,
        fullWidth: true,
        breadcrumb: [
          { label: 'Calendrier', to: 'calendar', icon: 'fa-solid fa-calendar-days' },
          { label: 'Créer un événement' },
        ],
      },
    },
    {
      path: '/calendar/:id',
      name: 'event-detail',
      component: () => import('@/views/EventDetailView.vue'),
      meta: { fullWidth: true },
      props: true,
    },
    {
      path: '/calendar/:id/edit',
      name: 'event-edit',
      component: () => import('@/views/EventEditView.vue'),
      meta: {
        requiresAuth: true,
        fullWidth: true,
        breadcrumb: [
          { label: 'Calendrier', to: 'calendar', icon: 'fa-solid fa-calendar-days' },
          { label: "Modifier l'événement" },
        ],
      },
      props: true,
    },
    {
      path: '/roster',
      name: 'roster',
      component: () => import('@/views/RosterView.vue'),
      meta: {
        breadcrumb: [{ label: 'Roster', icon: 'fa-solid fa-users' }],
      },
    },
    {
      path: '/servers',
      name: 'servers',
      component: () => import('@/views/ServersView.vue'),
      meta: {
        breadcrumb: [{ label: 'Serveurs', icon: 'fa-solid fa-server' }],
      },
    },
    {
      path: '/servers/:serverName',
      name: 'server-detail',
      component: () => import('@/views/ServerDetailView.vue'),
      props: true,
      meta: {
        breadcrumb: [
          { label: 'Serveurs', to: 'servers', icon: 'fa-solid fa-server' },
          { label: '' },
        ],
      },
    },
    {
      path: '/user/:nickname',
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
      meta: {
        breadcrumb: [{ label: 'TeamSpeak', icon: 'fa-brands fa-teamspeak' }],
      },
    },
    {
      path: '/discord',
      name: 'discord-voice',
      component: () => import('@/views/DiscordVoiceView.vue'),
      meta: {
        breadcrumb: [{ label: 'Discord', icon: 'fa-brands fa-discord' }],
      },
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
      path: '/design-system',
      name: 'design-system',
      component: () => import('@/views/DesignSystemView.vue'),
      meta: {
        breadcrumb: [{ label: 'Design System', icon: 'fa-solid fa-palette' }],
      },
    },
    // Admin routes
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/admin/DashboardView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', icon: 'fa-solid fa-screwdriver-wrench' },
        ],
      },
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/UsersView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Utilisateurs' },
        ],
      },
    },
    {
      path: '/admin/modules',
      name: 'admin-modules',
      component: () => import('@/views/admin/ModulesView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Modules' },
        ],
      },
    },
    {
      path: '/admin/calendar',
      name: 'admin-calendar',
      component: () => import('@/views/admin/CalendarAdminView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Calendrier' },
        ],
      },
    },
    {
      path: '/admin/pages',
      name: 'admin-pages',
      component: () => import('@/views/admin/PagesView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Pages' },
        ],
      },
    },
    {
      path: '/admin/pages/:id',
      name: 'admin-page-detail',
      component: () => import('@/views/admin/PageDetailView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Pages', to: 'admin-pages' },
          { label: '' },
        ],
      },
    },
    {
      path: '/admin/files',
      name: 'admin-files',
      component: () => import('@/views/admin/FilesView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Fichiers' },
        ],
      },
    },
    {
      path: '/admin/servers',
      name: 'admin-servers',
      component: () => import('@/views/admin/ServersView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Serveurs' },
        ],
      },
    },
    {
      path: '/admin/urls',
      name: 'admin-urls',
      component: () => import('@/views/admin/UrlsView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'URLs' },
        ],
      },
    },
    {
      path: '/admin/menu',
      name: 'admin-menu',
      component: () => import('@/views/admin/MenuView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Menu' },
        ],
      },
    },
    {
      path: '/admin/activities',
      name: 'admin-activities',
      component: () => import('@/views/admin/ActivitiesView.vue'),
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
        breadcrumb: [
          { label: 'Administration', to: 'admin', icon: 'fa-solid fa-screwdriver-wrench' },
          { label: 'Activités' },
        ],
      },
    },
    // Error pages
    {
      path: '/error/404',
      name: 'error-404',
      component: () => import('@/views/Error404View.vue'),
      meta: {
        breadcrumb: [{ label: 'Erreur 404', icon: 'fa-solid fa-plane-slash' }],
      },
    },
    {
      path: '/error/403',
      name: 'error-403',
      component: () => import('@/views/Error403View.vue'),
      meta: {
        breadcrumb: [{ label: 'Erreur 403', icon: 'fa-solid fa-lock' }],
      },
    },
    {
      path: '/error/500',
      name: 'error-500',
      component: () => import('@/views/Error500View.vue'),
      meta: {
        breadcrumb: [{ label: 'Erreur 500', icon: 'fa-solid fa-explosion' }],
      },
    },
    // Discord OAuth callback
    {
      path: '/auth/discord/callback',
      name: 'discord-callback',
      component: () => import('@/views/DiscordCallbackView.vue'),
    },
    // Redirect old /pages/ URLs
    {
      path: '/pages/:slug(.*)',
      redirect: to => ({ name: 'page', params: { slug: to.params.slug } }),
    },
    // CMS catch-all (must be LAST)
    {
      path: '/:slug(.*)',
      name: 'page',
      component: () => import('@/views/PageView.vue'),
      props: true,
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
    return { name: 'error-403' }
  }
})

export default router
