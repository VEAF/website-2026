import { type Plugin } from 'vite'
import { writeFileSync } from 'fs'
import { resolve } from 'path'

export function versionPlugin(): Plugin {
  const version = new Date().toISOString().slice(0, 19)

  return {
    name: 'version-plugin',
    config() {
      return {
        define: {
          __APP_VERSION__: JSON.stringify(version),
        },
      }
    },
    writeBundle(options) {
      const dir = options.dir ?? resolve('dist')
      writeFileSync(resolve(dir, 'version.json'), JSON.stringify({ version }))
    },
  }
}
