import { ref } from 'vue'

const visible = ref(false)
const discordUrl = ref('')

export function useDiscordSupport() {
  function setUrl(url: string) {
    discordUrl.value = url
  }

  function open() {
    if (discordUrl.value) {
      visible.value = true
    }
  }

  function close() {
    visible.value = false
  }

  return { visible, discordUrl, setUrl, open, close }
}
