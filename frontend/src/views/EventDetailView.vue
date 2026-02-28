<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getEvent, voteEvent, deleteEvent, copyEvent, addChoice, updateChoice, deleteChoice } from '@/api/calendar'
import type { EventDetail, Choice } from '@/types/calendar'
import { useConfirm } from '@/composables/useConfirm'
import { renderMarkdown } from '@/composables/useMarkdown'
import ChoiceModal from '@/components/ui/ChoiceModal.vue'
import { moduleTypeIcon } from '@/constants/modules'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const event = ref<EventDetail | null>(null)
const loading = ref(true)
const activeTab = ref<'description' | 'debrief'>('description')
const showAllChoices = ref(false)

const { confirm } = useConfirm()
const id = Number(route.params.id)

// Choice modal state
const choiceModalVisible = ref(false)
const choiceModalPriority = ref(1)
const choiceModalChoice = ref<Choice | null>(null)

onMounted(async () => {
  try {
    event.value = await getEvent(id)
  } finally {
    loading.value = false
  }
})


const canEdit = computed(() => {
  if (!auth.user || !event.value) return false
  return auth.user.id === event.value.owner_id || auth.isAdmin
})

const userVote = computed(() => {
  if (!event.value || !auth.user) return undefined
  return event.value.votes.find(v => v.user_id === auth.user!.id)
})

const eventStatus = computed(() => {
  if (!event.value) return null
  const now = Date.now()
  const start = new Date(event.value.start_date).getTime()
  const end = new Date(event.value.end_date).getTime()

  if (now < start) {
    const days = Math.ceil((start - now) / (1000 * 60 * 60 * 24))
    return { text: `dans ${days}j`, class: 'bg-green-100 text-green-800' }
  } else if (now < end) {
    return { text: 'en cours !', class: 'bg-yellow-100 text-yellow-800' }
  } else {
    return { text: 'terminé', class: 'bg-red-100 text-red-800' }
  }
})

const isFinished = computed(() => {
  if (!event.value) return false
  return new Date(event.value.end_date).getTime() < Date.now()
})

const canVote = computed(() => {
  if (!event.value || !auth.user) return { allowed: false, reason: '' }
  const e = event.value
  const u = auth.user

  if (!e.registration || isFinished.value) return { allowed: false, reason: '' }

  const isAdmin = u.roles.includes('ROLE_ADMIN')
  const isMember = (u.status >= 2 && u.status <= 8) || isAdmin
  const isCadet = u.status === 1

  if (e.restrictions.includes(2) && !isMember) {
    return { allowed: false, reason: 'Cet événement est réservé aux membres.' }
  }
  if (e.restrictions.includes(1) && !(isCadet || isMember)) {
    return { allowed: false, reason: 'Cet événement est réservé aux cadets et membres.' }
  }
  if (e.sim_dcs && !u.sim_dcs) {
    return { allowed: false, reason: 'Vous devez posséder le simulateur DCS pour participer.' }
  }
  if (e.sim_bms && !u.sim_bms) {
    return { allowed: false, reason: 'Vous devez posséder le simulateur BMS pour participer.' }
  }

  return { allowed: true, reason: '' }
})

const votesYes = computed(() => event.value?.votes.filter(v => v.vote === true) ?? [])
const votesMaybe = computed(() => event.value?.votes.filter(v => v.vote === null) ?? [])
const votesNo = computed(() => event.value?.votes.filter(v => v.vote === false) ?? [])

const userChoices = computed<Record<number, Choice | null>>(() => {
  if (!event.value || !auth.user) return { 1: null, 2: null, 3: null }
  const uc = event.value.choices.filter(c => c.user_id === auth.user!.id)
  return {
    1: uc.find(c => c.priority === 1) ?? null,
    2: uc.find(c => c.priority === 2) ?? null,
    3: uc.find(c => c.priority === 3) ?? null,
  }
})

const usersChoicesMap = computed(() => {
  if (!event.value) return new Map<number, Record<number, Choice | null>>()
  const map = new Map<number, Record<number, Choice | null>>()
  for (const c of event.value.choices) {
    if (!map.has(c.user_id)) {
      map.set(c.user_id, { 1: null, 2: null, 3: null })
    }
    const entry = map.get(c.user_id)!
    if (c.priority >= 1 && c.priority <= 3) {
      entry[c.priority] = c
    }
  }
  return map
})

const imageUrl = computed(() => {
  if (!event.value?.image_uuid) return null
  return `/api/files/${event.value.image_uuid}`
})

async function handleVote(vote: boolean | null) {
  if (!event.value) return
  await voteEvent(event.value.id, { vote })
  event.value = await getEvent(id)
}

async function handleCopy() {
  if (!event.value) return
  const copied = await copyEvent(event.value.id)
  router.push(`/calendar/${copied.id}/edit`)
}

async function handleDelete() {
  if (!event.value || !(await confirm('Supprimer cet événement ?'))) return
  await deleteEvent(event.value.id)
  router.push('/calendar')
}

function openChoiceModal(priority: number) {
  choiceModalPriority.value = priority
  choiceModalChoice.value = userChoices.value[priority] ?? null
  choiceModalVisible.value = true
}

async function handleChoiceSave(data: { module_id: number; task: number; comment: string }) {
  if (!event.value) return
  if (choiceModalChoice.value) {
    await updateChoice(choiceModalChoice.value.id, data)
  } else {
    await addChoice(event.value.id, {
      module_id: data.module_id,
      task: data.task,
      priority: choiceModalPriority.value,
      comment: data.comment,
    })
  }
  event.value = await getEvent(id)
  choiceModalVisible.value = false
}

async function handleChoiceDelete(choiceId: number) {
  if (!event.value) return
  await deleteChoice(choiceId)
  event.value = await getEvent(id)
  choiceModalVisible.value = false
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatTime(d: string) {
  return new Date(d).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function formatShortDate(d: string) {
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}
</script>

<template>
  <div v-if="loading" class="text-center py-12 text-gray-500">Chargement...</div>

  <div v-else-if="event" class="page-container py-6 space-y-6">

    <!-- Bloc 1 : En-tête -->
    <div class="card">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-2xl font-bold">
            <i class="fa-solid fa-circle text-sm mr-2" :style="{ color: event.type_color || '#999' }"></i>
            {{ event.type_as_string }} = {{ event.title }}
          </h1>
          <div class="mt-2 text-sm text-gray-600">
            Le {{ formatDate(event.start_date) }} à {{ formatTime(event.end_date) }}
            <span
              v-if="eventStatus"
              class="text-xs font-medium px-2 py-0.5 rounded-full ml-2"
              :class="eventStatus.class"
            >
              {{ eventStatus.text }}
            </span>
            <span v-if="event.repeat_event !== 0" class="ml-2 text-gray-400" title="événement récurrent">
              <i class="fa-solid fa-clock"></i>
            </span>
          </div>
          <div class="mt-1 text-sm text-gray-500">
            Organisé par {{ event.owner_nickname }}
          </div>
        </div>
        <div v-if="canEdit" class="flex space-x-2 flex-shrink-0">
          <button @click="handleCopy" class="btn-secondary text-sm"><i class="fa-solid fa-copy mr-1"></i>Copier</button>
          <RouterLink :to="`/calendar/${event.id}/edit`" class="btn-secondary text-sm"><i class="fa-solid fa-edit mr-1"></i>Modifier</RouterLink>
          <button @click="handleDelete" class="btn-danger text-sm"><i class="fa-solid fa-trash mr-1"></i>Supprimer</button>
        </div>
      </div>
    </div>

    <!-- Bloc 2 : Image / Bannière -->
    <div v-if="imageUrl || event.map_name" class="card p-0 overflow-hidden">
      <img
        v-if="imageUrl"
        :src="imageUrl"
        :alt="event.title"
        class="w-full h-56 object-cover"
      />
      <div v-else-if="event.map_name" class="w-full h-32 bg-gray-700 flex items-center justify-center">
        <p class="text-white text-xl font-semibold">{{ event.map_name }}</p>
      </div>
    </div>

    <!-- Bloc 3 : Description / Debrief (onglets) + Métadonnées -->
    <div class="card">
      <!-- Onglets -->
      <div class="border-b border-gray-200 mb-4">
        <nav class="flex space-x-4">
          <button
            @click="activeTab = 'description'"
            class="pb-2 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'description'
              ? 'border-veaf-600 text-veaf-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Description
          </button>
          <button
            @click="activeTab = 'debrief'"
            class="pb-2 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'debrief'
              ? 'border-veaf-600 text-veaf-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Debrief
          </button>
        </nav>
      </div>

      <!-- Contenu onglet -->
      <div v-if="activeTab === 'description'" class="prose max-w-none mb-6">
        <div v-if="event.description" v-html="renderMarkdown(event.description)"></div>
        <p v-else class="text-gray-400 italic">Aucune description.</p>
      </div>
      <div v-else class="prose max-w-none mb-6">
        <div v-if="event.debrief" v-html="renderMarkdown(event.debrief)"></div>
        <p v-else class="text-gray-400 italic">Aucun debrief.</p>
      </div>

      <!-- Métadonnées -->
      <hr class="border-gray-200 mb-4" />
      <div class="text-sm space-y-1 text-gray-700">
        <div v-if="event.server_name">
          <strong>Serveur :</strong> {{ event.server_name }}
        </div>
        <div v-if="event.sim_dcs || event.sim_bms">
          <strong>Réservé au(x) simulateur(s) :</strong>
          <span v-if="event.sim_dcs">DCS</span>
          <span v-if="event.sim_dcs && event.sim_bms">, </span>
          <span v-if="event.sim_bms">BMS</span>
        </div>
        <div v-if="event.map_name">
          <strong>Restriction de carte :</strong> {{ event.map_name }}
        </div>
        <div>
          <strong>Restriction de profil :</strong>
          <span v-if="event.restriction_labels.length">{{ event.restriction_labels.join(', ') }}</span>
          <span v-else>ouvert à tout le monde</span>
        </div>
        <div>
          <strong>Restriction de module :</strong>
          <span v-if="event.module_names.length">{{ event.module_names.join(', ') }}</span>
          <span v-else>ouvert à tous les modules</span>
        </div>
      </div>
    </div>

    <!-- Bloc 4 : ATO -->
    <div v-if="event.ato && event.flights.length" class="card">
      <h2 class="text-lg font-semibold mb-4">ATO</h2>
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b text-left">
            <th class="py-2">Flight</th>
            <th class="py-2">Appareil</th>
            <th class="py-2">Mission</th>
            <th class="py-2">Joueurs</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in event.flights" :key="f.id" class="border-b">
            <td class="py-2">{{ f.name }}</td>
            <td class="py-2">
              <span v-if="f.aircraft_name">{{ f.aircraft_name }} x{{ f.nb_slots }}</span>
            </td>
            <td class="py-2">{{ f.mission }}</td>
            <td class="py-2">
              <template v-for="(s, idx) in f.slots" :key="s.id">
                <span v-if="idx > 0">, </span>
                <span>{{ s.user_nickname || s.username || '= vide =' }}</span>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bloc 5 : Participation (Vote + Choix) -->
    <div class="card">
      <h2 class="text-lg font-semibold mb-4">Je participe</h2>

      <!-- Evénement terminé -->
      <div v-if="isFinished" class="bg-blue-50 text-blue-700 border border-blue-200 rounded-md p-3 text-sm">
        Cet événement est maintenant terminé, vous ne pouvez plus participer.
      </div>

      <!-- Inscriptions fermées -->
      <div v-else-if="!event.registration" class="bg-blue-50 text-blue-700 border border-blue-200 rounded-md p-3 text-sm">
        Les inscriptions à cet événement sont terminées. Contactez directement l'organisateur ({{ event.owner_nickname }}) pour plus de précisions.
      </div>

      <!-- Restrictions non respectées -->
      <div v-else-if="auth.isAuthenticated && !canVote.allowed" class="bg-yellow-50 text-yellow-700 border border-yellow-200 rounded-md p-3 text-sm">
        <i class="fa-solid fa-lock mr-1"></i>
        {{ canVote.reason }}
      </div>

      <!-- Boutons de vote (user authentifié + autorisé) -->
      <div v-else-if="auth.isAuthenticated && canVote.allowed">
        <div class="grid grid-cols-3 gap-3">
          <button
            @click="handleVote(true)"
            class="py-2 rounded-md font-medium text-sm transition-colors text-center"
            :class="userVote?.vote === true
              ? 'bg-green-600 text-white hover:bg-green-700'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
          >
            Oui
          </button>
          <button
            @click="handleVote(null)"
            class="py-2 rounded-md font-medium text-sm transition-colors text-center"
            :class="userVote !== undefined && userVote.vote === null
              ? 'bg-veaf-600 text-white hover:bg-veaf-700'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
          >
            Peut-être
          </button>
          <button
            @click="handleVote(false)"
            class="py-2 rounded-md font-medium text-sm transition-colors text-center"
            :class="userVote?.vote === false
              ? 'bg-red-600 text-white hover:bg-red-700'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
          >
            Non
          </button>
        </div>
      </div>

      <!-- Non connecté -->
      <div v-else class="bg-blue-50 text-blue-700 border border-blue-200 rounded-md p-3 text-sm">
        Vous devez être connecté et respecter les restrictions (simulateur, profil, carte, etc...) pour pouvoir vous inscrire à cet événement.
      </div>

      <!-- Cartes de choix (3 cartes sombres, si voté oui/peut-être) -->
      <div
        v-if="auth.isAuthenticated && userVote && userVote.vote !== false && !isFinished"
        class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6"
      >
        <div v-for="n in [1, 2, 3]" :key="n" class="bg-gray-800 text-white rounded-lg p-4 cursor-pointer hover:bg-gray-700 transition-colors" @click="openChoiceModal(n)">
          <div class="flex items-center justify-between mb-3">
            <span class="font-medium">Choix {{ n }}</span>
            <i class="fa-solid fa-pen-to-square text-gray-400"></i>
          </div>
          <div v-if="userChoices[n]" class="flex items-center justify-between">
            <i :class="moduleTypeIcon(userChoices[n]!.module_type)" class="text-3xl"></i>
            <div class="text-right">
              <div class="font-medium">{{ userChoices[n]!.module_name }}</div>
              <div class="text-sm text-gray-300">{{ userChoices[n]!.task_as_string }}</div>
            </div>
          </div>
          <div v-else class="text-center py-2">
            <i class="fa-solid fa-hourglass-start text-3xl text-gray-500"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Bloc 6 : Participants -->
    <div v-if="event.votes.length" class="card">
      <h2 class="text-lg font-semibold mb-4">
        Participants
        <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-green-100 text-green-800 ml-2">{{ votesYes.length }}</span>
        <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-800 ml-1">{{ votesMaybe.length }}</span>
        <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-red-100 text-red-800 ml-1">{{ votesNo.length }}</span>
      </h2>

      <!-- Listes inline par type de vote -->
      <div class="text-sm mb-4 space-y-1">
        <div>
          <span class="text-green-600 font-medium">Oui</span> :
          <template v-for="(v, idx) in votesYes" :key="v.id">
            <span v-if="idx > 0">, </span>
            <span>
              {{ v.user_nickname }}
              <span v-if="v.created_at" class="text-xs text-gray-400" :title="formatDate(v.created_at)">({{ formatShortDate(v.created_at) }})</span>
            </span>
          </template>
        </div>
        <div>
          <span class="text-gray-500 font-medium">Peut-être</span> :
          <template v-for="(v, idx) in votesMaybe" :key="v.id">
            <span v-if="idx > 0">, </span>
            <span>
              {{ v.user_nickname }}
              <span v-if="v.created_at" class="text-xs text-gray-400" :title="formatDate(v.created_at)">({{ formatShortDate(v.created_at) }})</span>
            </span>
          </template>
        </div>
        <div>
          <span class="text-red-600 font-medium">Non</span> :
          <template v-for="(v, idx) in votesNo" :key="v.id">
            <span v-if="idx > 0">, </span>
            <span>
              {{ v.user_nickname }}
              <span v-if="v.created_at" class="text-xs text-gray-400" :title="formatDate(v.created_at)">({{ formatShortDate(v.created_at) }})</span>
            </span>
          </template>
        </div>
      </div>

      <!-- "voir plus" = tableau extensible des choix par joueur -->
      <div>
        <button
          @click="showAllChoices = !showAllChoices"
          class="text-veaf-600 hover:text-veaf-800 text-sm"
        >
          {{ showAllChoices ? 'masquer' : 'voir plus ...' }}
        </button>
        <table v-if="showAllChoices" class="w-full text-sm mt-3">
          <thead>
            <tr class="border-b">
              <th rowspan="2" class="text-left py-2 align-top">Joueurs</th>
              <th colspan="2" class="text-left py-1">Choix 1</th>
              <th colspan="2" class="text-left py-1">Choix 2</th>
              <th colspan="2" class="text-left py-1">Choix 3</th>
            </tr>
            <tr class="border-b text-xs text-gray-500">
              <th class="text-left py-1">Module</th>
              <th class="text-left py-1">Tâche</th>
              <th class="text-left py-1">Module</th>
              <th class="text-left py-1">Tâche</th>
              <th class="text-left py-1">Module</th>
              <th class="text-left py-1">Tâche</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in [...votesYes, ...votesMaybe]" :key="v.id" class="border-b">
              <td class="py-2">
                {{ v.user_nickname }}
                <i v-if="v.vote === null" class="fa-solid fa-exclamation-circle text-yellow-500 ml-1" title="peut-être absent"></i>
                <i v-if="v.comment" class="fa-solid fa-comment text-gray-400 ml-1" :title="v.comment"></i>
                <span v-if="v.created_at" class="text-xs text-gray-400 ml-1">{{ formatShortDate(v.created_at) }}</span>
              </td>
              <template v-for="n in [1, 2, 3]" :key="n">
                <template v-if="usersChoicesMap.get(v.user_id)?.[n]">
                  <td class="py-2">{{ usersChoicesMap.get(v.user_id)![n]!.module_name }}</td>
                  <td class="py-2">
                    {{ usersChoicesMap.get(v.user_id)![n]!.task_as_string }}
                    <i
                      v-if="usersChoicesMap.get(v.user_id)![n]!.comment"
                      class="fa-solid fa-circle-question text-gray-400 ml-1"
                      :title="usersChoicesMap.get(v.user_id)![n]!.comment ?? ''"
                    ></i>
                  </td>
                </template>
                <td v-else colspan="2" class="py-2">&nbsp;</td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Choice Modal -->
    <ChoiceModal
      :visible="choiceModalVisible"
      :priority="choiceModalPriority"
      :choice="choiceModalChoice"
      :event-module-ids="event?.module_ids ?? []"
      @close="choiceModalVisible = false"
      @save="handleChoiceSave"
      @delete="handleChoiceDelete"
    />

  </div>
</template>
