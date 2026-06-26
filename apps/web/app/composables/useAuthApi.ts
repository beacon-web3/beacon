type AuthHttpMethod = 'DELETE' | 'GET' | 'PATCH' | 'POST' | 'PUT'

type AuthFetchOptions = {
  baseURL?: string
  body?: BodyInit | null | Record<string, unknown>
  credentials?: RequestCredentials
  headers?: HeadersInit
  method?: AuthHttpMethod
}

const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

export function useAuthApi() {
  const csrfToken = useCookie<string | null>('csrftoken')

  async function authFetch<T>(url: string, options: AuthFetchOptions = {}) {
    const method = options.method ?? 'GET'
    const headers = new Headers(options.headers)

    if (UNSAFE_METHODS.has(method) && csrfToken.value) {
      headers.set('X-CSRFToken', csrfToken.value)
    }

    return await $fetch<T>(url, {
      ...options,
      credentials: options.credentials ?? 'include',
      headers,
      method
    })
  }

  return { authFetch }
}
