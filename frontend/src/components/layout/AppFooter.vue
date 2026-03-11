<template>
  <footer class="bg-white/50 backdrop-blur-sm text-gray-600 py-6 mt-auto">
    <div class="container mx-auto px-4 text-center text-sm space-y-2">
      <p>
        &copy; {{ new Date().getFullYear() }} VEAF - Virtual European Air Force
        <a href="https://github.com/VEAF/website-2026" target="_blank" rel="noopener noreferrer"
           class="text-gray-500 hover:text-gray-700 transition-colors ml-2" title="Code source sur GitHub">
          <i class="fa-brands fa-github text-lg"></i>
        </a>
      </p>
      <p class="text-xs text-gray-400">
        Code source sous
        <a href="https://opensource.org/licenses/MIT" target="_blank" rel="noopener noreferrer" class="hover:text-gray-600">licence MIT</a>
        — Contenu sous
        <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer" class="hover:text-gray-600">CC BY 4.0</a>
      </p>
    </div>
  </footer>
</template>
