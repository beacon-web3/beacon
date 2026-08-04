import { defineEventHandler } from 'h3'
import { useRuntimeConfig } from 'nitropack/runtime'
import { generateChallenge } from 'capjs-core'

export default defineEventHandler(() => {
  const config = useRuntimeConfig()
  const secret = config.captchaSecret as string
  return generateChallenge(secret, {
    format: 2,
    protocols: ['sha256-pow'],
    challengeCount: 5,
    challengeSize: 16,
    challengeDifficulty: 4
  })
})
