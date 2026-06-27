type SocialAuthStartResponse = {
  authorization_url: string
}

type StartGoogleAuthOptions = {
  next?: string
}

export function useSocialAuthStart() {
  const { apiFetch } = useApiFetch()
  const { getApiErrorMessage } = useApiErrorMessage()

  const isStartingGoogleAuth = shallowRef(false)
  const socialAuthError = shallowRef('')

  async function startGoogleAuth(options: StartGoogleAuthOptions = {}) {
    socialAuthError.value = ''
    isStartingGoogleAuth.value = true

    try {
      const response = await apiFetch<SocialAuthStartResponse>('/api/auth/social/google/start/', {
        method: 'POST',
        body: {
          next: options.next ?? '/dashboard'
        }
      })

      if (import.meta.client) {
        window.location.assign(response.authorization_url)
      }
    } catch (error) {
      socialAuthError.value = getApiErrorMessage(error, {
        fallbackMessageKey: 'auth.socialStartError',
        safeValidationKeys: ['next']
      })
    } finally {
      isStartingGoogleAuth.value = false
    }
  }

  return {
    isStartingGoogleAuth,
    socialAuthError,
    startGoogleAuth
  }
}
