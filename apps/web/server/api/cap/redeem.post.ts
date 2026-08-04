import { defineEventHandler, readBody, createError } from 'h3'
import { useRuntimeConfig } from 'nitropack/runtime'
import { validateChallenge } from 'capjs-core'

function base64url(input: string): string {
  return btoa(input).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '')
}

async function signJwt(payload: Record<string, unknown>, secret: string, expiresMs: number): Promise<string> {
  const header = base64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const now = Math.floor(Date.now() / 1000)
  const body = base64url(JSON.stringify({ ...payload, iat: now, exp: now + Math.floor(expiresMs / 1000) }))
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(`${header}.${body}`))
  return `${header}.${body}.${base64url(String.fromCharCode(...new Uint8Array(sig)))}`
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const secret = config.captchaSecret as string
  const body = await readBody(event)

  const result = await validateChallenge(secret, body, {
    signToken: async ({ scope, expires, iat }) => signJwt({ scope }, secret, expires - (iat ?? 0))
  })

  if (!result || result.success !== true) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid solution' })
  }

  return { token: result.token, expires: result.expires }
})
