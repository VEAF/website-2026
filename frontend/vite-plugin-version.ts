import { type Plugin } from 'vite'
import { readFileSync, writeFileSync } from 'fs'
import { resolve } from 'path'

function readSemver(): string {
  try {
    return readFileSync(resolve(__dirname, '..', 'VERSION'), 'utf-8').trim()
  } catch {
    return 'dev'
  }
}

export function versionPlugin(): Plugin {
  const version = new Date().toISOString().slice(0, 19)
  const semver = readSemver()

  return {
    name: 'version-plugin',
    config() {
      return {
        define: {
          __APP_VERSION__: JSON.stringify(version),
          __APP_SEMVER__: JSON.stringify(semver),
        },
      }
    },
    writeBundle(options) {
      const dir = options.dir ?? resolve('dist')
      writeFileSync(resolve(dir, 'version.json'), JSON.stringify({ version }))
    },
  }
}
