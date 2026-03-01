<script setup lang="ts">
import { useConfirm } from '@/composables/useConfirm'
import AppBreadcrumb from '@/components/ui/AppBreadcrumb.vue'

const { confirm } = useConfirm()

const veafColors = [
  { shade: '50', hex: '#f0f8fd', bg: 'bg-veaf-50' },
  { shade: '100', hex: '#d9eef9', bg: 'bg-veaf-100' },
  { shade: '200', hex: '#b3ddf3', bg: 'bg-veaf-200' },
  { shade: '300', hex: '#7ec7ed', bg: 'bg-veaf-300' },
  { shade: '400', hex: '#4ab3e7', bg: 'bg-veaf-400' },
  { shade: '500', hex: '#2fa4e7', bg: 'bg-veaf-500' },
  { shade: '600', hex: '#1e8cc7', bg: 'bg-veaf-600' },
  { shade: '700', hex: '#1a75a8', bg: 'bg-veaf-700' },
  { shade: '800', hex: '#165e87', bg: 'bg-veaf-800' },
  { shade: '900', hex: '#033c73', bg: 'bg-veaf-900' },
]

async function showConfirm() {
  const result = await confirm('Ceci est un exemple de modale de confirmation. Voulez-vous continuer ?')
  if (result) {
    alert('Confirmé !')
  }
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-sm p-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">Systeme de design VEAF</h1>
      <p class="text-gray-600">Reference des composants UI et tokens de design du site VEAF.</p>
    </div>

    <!-- Table of contents -->
    <nav class="card mb-8">
      <h2 class="text-lg font-semibold mb-3">Sommaire</h2>
      <div class="flex flex-wrap gap-2">
        <a href="#couleurs" class="btn-secondary btn btn-sm">Couleurs</a>
        <a href="#degrades" class="btn-secondary btn btn-sm">Degrades</a>
        <a href="#typographie" class="btn-secondary btn btn-sm">Typographie</a>
        <a href="#boutons" class="btn-secondary btn btn-sm">Boutons</a>
        <a href="#formulaires" class="btn-secondary btn btn-sm">Formulaires</a>
        <a href="#cartes" class="btn-secondary btn btn-sm">Cartes</a>
        <a href="#badges" class="btn-secondary btn btn-sm">Badges</a>
        <a href="#alertes" class="btn-secondary btn btn-sm">Alertes</a>
        <a href="#table" class="btn-secondary btn btn-sm">Table</a>
        <a href="#modale" class="btn-secondary btn btn-sm">Modale</a>
        <a href="#breadcrumb" class="btn-secondary btn btn-sm">Breadcrumb</a>
        <a href="#icones" class="btn-secondary btn btn-sm">Icones</a>
      </div>
    </nav>

    <!-- Couleurs -->
    <section id="couleurs" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Palette de couleurs</h2>
      <p class="text-sm text-gray-500 mb-6">Palette VEAF basee sur le bleu cerulean (#2fa4e7), declinee en 10 nuances.</p>

      <h3 class="text-lg font-semibold mb-3">Couleurs VEAF</h3>
      <div class="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2 mb-8">
        <div v-for="color in veafColors" :key="color.shade" class="text-center">
          <div
            :class="[color.bg, 'rounded-lg h-16 mb-1 border border-gray-200']"
          ></div>
          <p class="text-xs font-medium">{{ color.shade }}</p>
          <p class="text-xs text-gray-500">{{ color.hex }}</p>
        </div>
      </div>

      <h3 class="text-lg font-semibold mb-3">Couleurs semantiques</h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div class="text-center">
          <div class="bg-success-500 rounded-lg h-16 mb-1"></div>
          <p class="text-xs font-medium">Succes</p>
          <p class="text-xs text-gray-500">#73a839</p>
        </div>
        <div class="text-center">
          <div class="bg-warning-500 rounded-lg h-16 mb-1"></div>
          <p class="text-xs font-medium">Avertissement</p>
          <p class="text-xs text-gray-500">#dd5600</p>
        </div>
        <div class="text-center">
          <div class="bg-danger-500 rounded-lg h-16 mb-1"></div>
          <p class="text-xs font-medium">Danger</p>
          <p class="text-xs text-gray-500">#c71c22</p>
        </div>
        <div class="text-center">
          <div class="bg-gray-500 rounded-lg h-16 mb-1"></div>
          <p class="text-xs font-medium">Neutre</p>
        </div>
      </div>
    </section>

    <!-- Degrades -->
    <section id="degrades" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Degrades</h2>
      <p class="text-sm text-gray-500 mb-6">Degrades utilises dans le design (navbar, sections, roster).</p>

      <div class="space-y-4">
        <div>
          <p class="text-sm font-medium mb-1">bg-veaf-gradient <span class="text-gray-500">(navbar, splash)</span></p>
          <div class="bg-veaf-gradient h-16 rounded-lg"></div>
        </div>
        <div>
          <p class="text-sm font-medium mb-1">bg-veaf-gradient-dark <span class="text-gray-500">(roster period)</span></p>
          <div class="bg-veaf-gradient-dark h-16 rounded-lg"></div>
        </div>
        <div>
          <p class="text-sm font-medium mb-1">bg-veaf-section <span class="text-gray-500">(section icons)</span></p>
          <div class="bg-veaf-section h-16 rounded-lg"></div>
        </div>
      </div>
    </section>

    <!-- Typographie -->
    <section id="typographie" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Typographie</h2>
      <p class="text-sm text-gray-500 mb-6">Hierarchie typographique basee sur la police systeme sans-serif. Couleur de texte : #495057.</p>

      <div class="card space-y-4">
        <div>
          <p class="text-xs text-gray-400 mb-1">text-4xl font-bold</p>
          <p class="text-4xl font-bold">Titre de niveau 1</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 mb-1">text-3xl font-bold</p>
          <p class="text-3xl font-bold">Titre de niveau 2</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 mb-1">text-2xl font-bold</p>
          <p class="text-2xl font-bold">Titre de niveau 3</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 mb-1">text-xl font-semibold</p>
          <p class="text-xl font-semibold">Titre de niveau 4</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 mb-1">text-lg font-semibold</p>
          <p class="text-lg font-semibold">Titre de niveau 5</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 mb-1">text-base font-medium</p>
          <p class="text-base font-medium">Titre de niveau 6</p>
        </div>
        <hr class="border-gray-200" />
        <div>
          <p class="text-xs text-gray-400 mb-1">text-base (corps de texte)</p>
          <p class="text-base">Ceci est un paragraphe de texte standard. Le corps de texte utilise la taille par defaut (1rem / 16px) avec la couleur #495057 pour une lecture confortable.</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 mb-1">text-sm</p>
          <p class="text-sm">Texte de petite taille (0.875rem), utilise pour les labels, descriptions et textes secondaires.</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 mb-1">text-xs</p>
          <p class="text-xs">Texte tres petit (0.75rem), utilise pour les badges, annotations et metadonnees.</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 mb-1">Liens</p>
          <p>Voici un <a href="#">lien standard</a> dans un paragraphe de texte.</p>
        </div>
      </div>
    </section>

    <!-- Boutons -->
    <section id="boutons" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Boutons</h2>
      <p class="text-sm text-gray-500 mb-6">Variantes de boutons avec classes CSS dediees (.btn-*).</p>

      <div class="card space-y-6">
        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Variantes</p>
          <div class="flex flex-wrap gap-2">
            <button class="btn-primary">Primary</button>
            <button class="btn-secondary">Secondary</button>
            <button class="btn-danger">Danger</button>
            <button class="btn-success">Success</button>
            <button class="btn-warning">Warning</button>
            <button class="btn-info">Info</button>
          </div>
        </div>

        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Desactives</p>
          <div class="flex flex-wrap gap-2">
            <button class="btn-primary" disabled>Primary</button>
            <button class="btn-secondary" disabled>Secondary</button>
            <button class="btn-danger" disabled>Danger</button>
            <button class="btn-success" disabled>Success</button>
            <button class="btn-warning" disabled>Warning</button>
            <button class="btn-info" disabled>Info</button>
          </div>
        </div>

        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Tailles</p>
          <div class="flex flex-wrap items-center gap-2">
            <button class="btn-primary btn-sm">Petit (btn-sm)</button>
            <button class="btn-primary">Normal</button>
            <button class="btn-primary btn-lg">Grand (btn-lg)</button>
          </div>
        </div>

        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Avec icones</p>
          <div class="flex flex-wrap gap-2">
            <button class="btn-primary"><i class="fa-solid fa-plus mr-1"></i>Ajouter</button>
            <button class="btn-danger"><i class="fa-solid fa-trash mr-1"></i>Supprimer</button>
            <button class="btn-success"><i class="fa-solid fa-check mr-1"></i>Valider</button>
            <button class="btn-secondary"><i class="fa-solid fa-xmark mr-1"></i>Annuler</button>
            <button class="btn-info"><i class="fa-solid fa-download mr-1"></i>Telecharger</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Formulaires -->
    <section id="formulaires" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Formulaires</h2>
      <p class="text-sm text-gray-500 mb-6">Elements de formulaire avec classes .label et .input.</p>

      <div class="card">
        <form @submit.prevent class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="label">Champ texte</label>
              <input type="text" class="input" placeholder="Saisissez du texte..." />
            </div>
            <div>
              <label class="label">Email</label>
              <input type="email" class="input" placeholder="nom@exemple.fr" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="label">Liste deroulante</label>
              <select class="input">
                <option value="">-- Choisir --</option>
                <option value="1">Option 1</option>
                <option value="2">Option 2</option>
                <option value="3">Option 3</option>
              </select>
            </div>
            <div>
              <label class="label">Mot de passe</label>
              <input type="password" class="input" placeholder="********" />
            </div>
          </div>

          <div>
            <label class="label">Zone de texte</label>
            <textarea class="input" rows="3" placeholder="Ecrivez quelque chose..."></textarea>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="label">Cases a cocher</label>
              <div class="space-y-2">
                <label class="flex items-center space-x-2">
                  <input type="checkbox" class="rounded" checked />
                  <span class="text-sm">Option A (cochee)</span>
                </label>
                <label class="flex items-center space-x-2">
                  <input type="checkbox" class="rounded" />
                  <span class="text-sm">Option B</span>
                </label>
              </div>
            </div>
            <div>
              <label class="label">Boutons radio</label>
              <div class="space-y-2">
                <label class="flex items-center space-x-2">
                  <input type="radio" name="radio-example" checked />
                  <span class="text-sm">Choix 1 (selectionne)</span>
                </label>
                <label class="flex items-center space-x-2">
                  <input type="radio" name="radio-example" />
                  <span class="text-sm">Choix 2</span>
                </label>
              </div>
            </div>
          </div>

          <div>
            <label class="label">Champ desactive</label>
            <input type="text" class="input" disabled value="Ce champ est desactive" />
          </div>

          <div class="flex justify-end space-x-3">
            <button type="button" class="btn-secondary">Annuler</button>
            <button type="submit" class="btn-primary">Enregistrer</button>
          </div>
        </form>
      </div>
    </section>

    <!-- Cartes -->
    <section id="cartes" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Cartes</h2>
      <p class="text-sm text-gray-500 mb-6">Conteneur .card pour regrouper le contenu.</p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card">
          <h3 class="text-lg font-semibold mb-2">Carte standard</h3>
          <p class="text-sm text-gray-600">Classe <code class="text-xs bg-gray-100 px-1 py-0.5 rounded">.card</code> — fond blanc, bordure, ombre legere, padding p-6.</p>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-lg font-semibold mb-2">Carte avec ombre forte</h3>
          <p class="text-sm text-gray-600">Variante avec <code class="text-xs bg-gray-100 px-1 py-0.5 rounded">shadow-lg</code> pour les elements mis en avant, similaire au container-main de l'ancien site.</p>
        </div>
      </div>
    </section>

    <!-- Badges -->
    <section id="badges" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Badges</h2>
      <p class="text-sm text-gray-500 mb-6">Etiquettes semantiques (.badge-*) et badges de type de module.</p>

      <div class="card space-y-6">
        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Badges semantiques</p>
          <div class="flex flex-wrap gap-2">
            <span class="badge-primary">Primary</span>
            <span class="badge-success">Succes</span>
            <span class="badge-warning">Avertissement</span>
            <span class="badge-danger">Danger</span>
            <span class="badge-neutral">Neutre</span>
          </div>
        </div>

        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Badges de type module</p>
          <div class="flex flex-wrap gap-2">
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium module-aircraft">Avion</span>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium module-helicopter">Helicoptere</span>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium module-special">Special</span>
          </div>
        </div>

        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Exemples de statut</p>
          <div class="flex flex-wrap gap-2">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Actif</span>
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Cadet</span>
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Invite</span>
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-veaf-100 text-veaf-800">Bureau</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Alertes -->
    <section id="alertes" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Alertes</h2>
      <p class="text-sm text-gray-500 mb-6">Messages d'information contextuels (.alert-*).</p>

      <div class="space-y-3">
        <div class="alert-info">
          <i class="fa-solid fa-circle-info mr-2"></i>
          Ceci est un message d'information.
        </div>
        <div class="alert-success">
          <i class="fa-solid fa-circle-check mr-2"></i>
          Operation realisee avec succes.
        </div>
        <div class="alert-warning">
          <i class="fa-solid fa-triangle-exclamation mr-2"></i>
          Attention, cette action est irreversible.
        </div>
        <div class="alert-danger">
          <i class="fa-solid fa-circle-xmark mr-2"></i>
          Une erreur est survenue lors du traitement.
        </div>
      </div>
    </section>

    <!-- Table -->
    <section id="table" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Table</h2>
      <p class="text-sm text-gray-500 mb-6">Pattern de table admin avec utilitaires Tailwind.</p>

      <div class="card overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b text-left">
              <th class="p-2">Nom</th>
              <th class="p-2">Email</th>
              <th class="p-2">Statut</th>
              <th class="p-2">Role</th>
              <th class="p-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b hover:bg-gray-50">
              <td class="p-2 font-medium">Jean Dupont</td>
              <td class="p-2 text-gray-500">jean@veaf.org</td>
              <td class="p-2"><span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Membre</span></td>
              <td class="p-2">Pilote</td>
              <td class="p-2 text-right">
                <button class="text-veaf-600 hover:text-veaf-800 text-sm mr-2"><i class="fa-solid fa-pen mr-1"></i>Modifier</button>
                <button class="text-red-600 hover:text-red-800 text-sm"><i class="fa-solid fa-trash mr-1"></i>Supprimer</button>
              </td>
            </tr>
            <tr class="border-b hover:bg-gray-50">
              <td class="p-2 font-medium">Marie Martin</td>
              <td class="p-2 text-gray-500">marie@veaf.org</td>
              <td class="p-2"><span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Cadet</span></td>
              <td class="p-2">Stagiaire</td>
              <td class="p-2 text-right">
                <button class="text-veaf-600 hover:text-veaf-800 text-sm mr-2"><i class="fa-solid fa-pen mr-1"></i>Modifier</button>
                <button class="text-red-600 hover:text-red-800 text-sm"><i class="fa-solid fa-trash mr-1"></i>Supprimer</button>
              </td>
            </tr>
            <tr class="border-b hover:bg-gray-50">
              <td class="p-2 font-medium">Pierre Bernard</td>
              <td class="p-2 text-gray-500">pierre@veaf.org</td>
              <td class="p-2"><span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-veaf-100 text-veaf-800">Bureau</span></td>
              <td class="p-2">Commandant</td>
              <td class="p-2 text-right">
                <button class="text-veaf-600 hover:text-veaf-800 text-sm mr-2"><i class="fa-solid fa-pen mr-1"></i>Modifier</button>
                <button class="text-red-600 hover:text-red-800 text-sm"><i class="fa-solid fa-trash mr-1"></i>Supprimer</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div class="flex items-center justify-between mt-4 text-sm">
          <span class="text-gray-500">3 resultats</span>
          <div class="flex items-center space-x-2">
            <button class="btn-secondary btn-sm" disabled><i class="fa-solid fa-chevron-left mr-1"></i>Precedent</button>
            <span class="text-gray-600">Page 1 / 1</span>
            <button class="btn-secondary btn-sm" disabled>Suivant<i class="fa-solid fa-chevron-right ml-1"></i></button>
          </div>
        </div>
      </div>
    </section>

    <!-- Modale -->
    <section id="modale" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Modale</h2>
      <p class="text-sm text-gray-500 mb-6">Modale de confirmation utilisant le composable useConfirm().</p>

      <div class="card">
        <button class="btn-primary" @click="showConfirm">
          <i class="fa-solid fa-question-circle mr-1"></i>Ouvrir la modale de confirmation
        </button>
      </div>
    </section>

    <!-- Breadcrumb -->
    <section id="breadcrumb" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Breadcrumb</h2>
      <p class="text-sm text-gray-500 mb-6">Navigation en fil d'Ariane, style fleches de manuels de vol. Composant AppBreadcrumb.</p>

      <div class="card space-y-6">
        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Page courante (depuis le routeur)</p>
          <AppBreadcrumb :show-title="false" />
        </div>

        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Exemple a 2 niveaux</p>
          <nav class="flex overflow-x-auto scrollbar-hide">
            <ol class="flex items-center flex-nowrap">
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-first breadcrumb-segment-primary" style="z-index: 2">
                  <i class="fa-solid fa-house mr-1.5 text-xs"></i><span>Accueil</span>
                </span>
              </li>
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-active breadcrumb-segment-info" style="z-index: 1">
                  <i class="fa-solid fa-users mr-1.5 text-xs"></i><span>Roster</span>
                </span>
              </li>
            </ol>
          </nav>
        </div>

        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Exemple a 3 niveaux</p>
          <nav class="flex overflow-x-auto scrollbar-hide">
            <ol class="flex items-center flex-nowrap">
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-first breadcrumb-segment-primary" style="z-index: 3">
                  <i class="fa-solid fa-house mr-1.5 text-xs"></i><span>Accueil</span>
                </span>
              </li>
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-primary" style="z-index: 2">
                  <i class="fa-solid fa-server mr-1.5 text-xs"></i><span>Serveurs</span>
                </span>
              </li>
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-active breadcrumb-segment-info" style="z-index: 1">
                  <span>VEAF-DCS-Caucasus</span>
                </span>
              </li>
            </ol>
          </nav>
        </div>

        <div>
          <p class="text-sm font-medium text-gray-600 mb-3">Exemple admin a 4 niveaux</p>
          <nav class="flex overflow-x-auto scrollbar-hide">
            <ol class="flex items-center flex-nowrap">
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-first breadcrumb-segment-primary" style="z-index: 4">
                  <i class="fa-solid fa-house mr-1.5 text-xs"></i><span>Accueil</span>
                </span>
              </li>
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-primary" style="z-index: 3">
                  <i class="fa-solid fa-screwdriver-wrench mr-1.5 text-xs"></i><span>Administration</span>
                </span>
              </li>
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-primary" style="z-index: 2">
                  <span>Pages</span>
                </span>
              </li>
              <li class="flex-shrink-0">
                <span class="breadcrumb-segment breadcrumb-segment-active breadcrumb-segment-info" style="z-index: 1">
                  <span>Reglement interieur</span>
                </span>
              </li>
            </ol>
          </nav>
        </div>
      </div>
    </section>

    <!-- Icones -->
    <section id="icones" class="mb-12">
      <h2 class="text-2xl font-bold mb-1 pb-2 border-b border-gray-200">Icones</h2>
      <p class="text-sm text-gray-500 mb-6">FontAwesome 6 Free — icones solid et brands courantes.</p>

      <div class="card">
        <h3 class="text-sm font-medium text-gray-600 mb-3">Solid (fa-solid)</h3>
        <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-4 mb-6">
          <div v-for="icon in [
            'fa-user', 'fa-users', 'fa-gear', 'fa-bars', 'fa-plus', 'fa-trash', 'fa-pen',
            'fa-check', 'fa-xmark', 'fa-magnifying-glass', 'fa-calendar', 'fa-plane',
            'fa-helicopter', 'fa-server', 'fa-download', 'fa-upload', 'fa-right-from-bracket',
            'fa-right-to-bracket', 'fa-chevron-down', 'fa-chevron-right', 'fa-chevron-left',
            'fa-triangle-exclamation', 'fa-circle-info', 'fa-circle-check',
          ]" :key="icon" class="flex flex-col items-center text-center gap-1">
            <i :class="`fa-solid ${icon} text-xl text-gray-700`"></i>
            <span class="text-xs text-gray-500 truncate w-full">{{ icon }}</span>
          </div>
        </div>

        <h3 class="text-sm font-medium text-gray-600 mb-3">Brands (fa-brands)</h3>
        <div class="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-4 mb-6">
          <div v-for="icon in [
            'fa-discord', 'fa-teamspeak', 'fa-github', 'fa-youtube',
          ]" :key="icon" class="flex flex-col items-center text-center gap-1">
            <i :class="`fa-brands ${icon} text-xl text-gray-700`"></i>
            <span class="text-xs text-gray-500 truncate w-full">{{ icon }}</span>
          </div>
        </div>

        <h3 class="text-sm font-medium text-gray-600 mb-3">Tailles</h3>
        <div class="flex items-end gap-4">
          <div class="text-center">
            <i class="fa-solid fa-plane text-xs text-veaf-500"></i>
            <p class="text-xs text-gray-500 mt-1">text-xs</p>
          </div>
          <div class="text-center">
            <i class="fa-solid fa-plane text-sm text-veaf-500"></i>
            <p class="text-xs text-gray-500 mt-1">text-sm</p>
          </div>
          <div class="text-center">
            <i class="fa-solid fa-plane text-base text-veaf-500"></i>
            <p class="text-xs text-gray-500 mt-1">text-base</p>
          </div>
          <div class="text-center">
            <i class="fa-solid fa-plane text-xl text-veaf-500"></i>
            <p class="text-xs text-gray-500 mt-1">text-xl</p>
          </div>
          <div class="text-center">
            <i class="fa-solid fa-plane text-2xl text-veaf-500"></i>
            <p class="text-xs text-gray-500 mt-1">text-2xl</p>
          </div>
          <div class="text-center">
            <i class="fa-solid fa-plane text-4xl text-veaf-500"></i>
            <p class="text-xs text-gray-500 mt-1">text-4xl</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
