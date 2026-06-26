type ApiHttpMethod = 'DELETE' | 'GET' | 'PATCH' | 'POST' | 'PUT'

type ApiFetchRequestContext = {
  headers: Headers
  method: ApiHttpMethod
  url: string
}

type ApiFetchResponseContext<T> = {
  data: T
  method: ApiHttpMethod
  url: string
}

type ApiFetchOptions<T> = {
  baseURL?: string
  body?: BodyInit | null | Record<string, unknown>
  credentials?: RequestCredentials
  headers?: HeadersInit
  method?: ApiHttpMethod
  onRequest?: (context: ApiFetchRequestContext) => void | Promise<void>
  onResponse?: (context: ApiFetchResponseContext<T>) => void | Promise<void>
  retry?: number | false
  retryDelay?: number
  timeout?: number
}

type ApiFetchErrorOptions = {
  cause?: unknown
  data?: unknown
  statusCode?: number
  statusMessage?: string
}

type FetchErrorShape = {
  data?: unknown
  message?: string
  response?: {
    status?: number
    statusText?: string
  }
  status?: number
  statusCode?: number
  statusMessage?: string
}

const UNSAFE_METHODS = new Set<ApiHttpMethod>(['POST', 'PUT', 'PATCH', 'DELETE'])
const DEFAULT_TIMEOUT_MS = 15000

export class ApiFetchError extends Error {
  data?: unknown
  statusCode?: number
  statusMessage?: string

  constructor(message: string, options: ApiFetchErrorOptions = {}) {
    super(message, { cause: options.cause })
    this.name = 'ApiFetchError'
    this.data = options.data
    this.statusCode = options.statusCode
    this.statusMessage = options.statusMessage
  }
}

export function useApiFetch() {
  const config = useRuntimeConfig()
  const csrfToken = useCookie<string | null>('csrftoken')

  const apiBaseUrl = computed(() => {
    return typeof config.public.apiBaseUrl === 'string'
      ? config.public.apiBaseUrl
      : undefined
  })

  async function apiFetch<T>(url: string, options: ApiFetchOptions<T> = {}) {
    const { onRequest, onResponse, ...fetchOptions } = options
    const method = options.method ?? 'GET'
    const headers = new Headers(options.headers)

    if (UNSAFE_METHODS.has(method) && csrfToken.value) {
      headers.set('X-CSRFToken', csrfToken.value)
    }

    await onRequest?.({ headers, method, url })

    try {
      const data = await $fetch<T>(url, {
        ...fetchOptions,
        baseURL: fetchOptions.baseURL ?? apiBaseUrl.value,
        credentials: fetchOptions.credentials ?? 'include',
        headers,
        method,
        timeout: fetchOptions.timeout ?? DEFAULT_TIMEOUT_MS
      })

      await onResponse?.({ data, method, url })

      return data
    } catch (error) {
      throw normalizeApiFetchError(error)
    }
  }

  return { apiFetch }
}

function normalizeApiFetchError(error: unknown) {
  if (error instanceof ApiFetchError) {
    return error
  }

  if (typeof error === 'object' && error !== null) {
    const fetchError = error as FetchErrorShape
    const statusCode = fetchError.statusCode ?? fetchError.status ?? fetchError.response?.status
    const statusMessage = fetchError.statusMessage ?? fetchError.response?.statusText
    const message = fetchError.message ?? statusMessage ?? 'API request failed'

    return new ApiFetchError(message, {
      cause: error,
      data: fetchError.data,
      statusCode,
      statusMessage
    })
  }

  return new ApiFetchError('API request failed', { cause: error })
}
