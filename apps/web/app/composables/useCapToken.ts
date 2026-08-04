async function solvePoW(salt: string, target: string): Promise<number> {
  const targetBytes = hexToBytes(target)
  for (let nonce = 0; nonce < 10_000_000; nonce++) {
    const hash = new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(salt + nonce)))
    if (matchesPrefix(hash, targetBytes)) return nonce
  }
  throw new Error('No PoW solution found')
}

function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length >> 1)
  for (let i = 0; i < bytes.length; i++) {
    const a = hex.charCodeAt(i * 2)
    const b = hex.charCodeAt(i * 2 + 1)
    bytes[i] = ((a <= 57 ? a - 48 : (a | 32) - 87) << 4) | (b <= 57 ? b - 48 : (b | 32) - 87)
  }
  return bytes
}

function matchesPrefix(hash: Uint8Array, target: Uint8Array): boolean {
  for (let i = 0; i < target.length; i++) {
    if (hash[i] !== target[i]) return false
  }
  return true
}

export function useCapToken() {
  async function executeCaptcha(): Promise<string> {
    const challengeRes = await $fetch<{ token: string, challenges: Array<{ protocol: string, payload: { salt: string, target: string } }> }>('/api/cap/challenge', { method: 'POST' })
    const solutions = await Promise.all(
      challengeRes.challenges.map(async c => ({ nonce: await solvePoW(c.payload.salt, c.payload.target) }))
    )
    const redeemRes = await $fetch<{ token: string }>('/api/cap/redeem', {
      method: 'POST',
      body: { token: challengeRes.token, solutions }
    })
    return redeemRes.token
  }

  return { executeCaptcha }
}
