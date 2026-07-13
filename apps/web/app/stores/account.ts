import { defineStore } from 'pinia'

export type AccountData = {
  id: number
  email: string
  username: string
  display_name: string
  wallet_address: string | null
  reputation_score: number
  account_credit: string
}

type AccountStatus = 'idle' | 'pending' | 'success' | 'error'

type AccountResponse = {
  account: AccountData
}

export const useAccountStore = defineStore('account', () => {
  const { apiFetch } = useApiFetch()

  const account = ref<AccountData | null>(null)
  const status = ref<AccountStatus>('idle')
  const error = ref<Error | null>(null)

  const isLoggedIn = computed(() => status.value === 'success' && account.value !== null)

  async function fetchAccount() {
    status.value = 'pending'
    error.value = null

    try {
      const response = await apiFetch<AccountResponse>('/api/auth/me/', {
        method: 'GET'
      })
      account.value = response.account
      status.value = 'success'
    } catch (err) {
      account.value = null
      status.value = 'error'
      error.value = err instanceof Error ? err : new Error(String(err))
    }
  }

  async function login(body: Record<string, unknown>) {
    status.value = 'pending'
    error.value = null

    try {
      await apiFetch('/api/auth/login/', {
        method: 'POST',
        body
      })
      await fetchAccount()
    } catch (err) {
      account.value = null
      status.value = 'error'
      error.value = err instanceof Error ? err : new Error(String(err))
      throw err
    }
  }

  async function logout() {
    try {
      await apiFetch('/api/auth/logout/', {
        method: 'POST'
      })
    } finally {
      reset()
    }
  }

  function reset() {
    account.value = null
    status.value = 'idle'
    error.value = null
  }

  return {
    account,
    status,
    error,
    isLoggedIn,
    fetchAccount,
    login,
    logout,
    reset
  }
})
