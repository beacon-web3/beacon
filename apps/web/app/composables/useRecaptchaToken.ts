type RecaptchaApi = {
  execute: (widgetId: number) => void
  ready?: (callback: () => void) => void
  render: (container: HTMLElement, parameters: RecaptchaRenderParameters) => number
  reset: (widgetId: number) => void
}

type RecaptchaRenderParameters = {
  'callback': (token: string) => void
  'error-callback': () => void
  'expired-callback': () => void
  'sitekey': string
  'size': 'invisible'
}

declare global {
  interface Window {
    grecaptcha?: RecaptchaApi
  }
}

const RECAPTCHA_SCRIPT_ID = 'beacon-recaptcha-v2'

let recaptchaScriptPromise: Promise<void> | undefined

function loadRecaptchaScript() {
  if (window.grecaptcha) {
    return Promise.resolve()
  }

  if (recaptchaScriptPromise) {
    return recaptchaScriptPromise
  }

  recaptchaScriptPromise = new Promise((resolve, reject) => {
    const existingScript = document.getElementById(RECAPTCHA_SCRIPT_ID)
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(), { once: true })
      existingScript.addEventListener('error', () => reject(new Error('reCAPTCHA failed to load')), { once: true })
      return
    }

    const script = document.createElement('script')
    script.id = RECAPTCHA_SCRIPT_ID
    script.src = 'https://www.google.com/recaptcha/api.js?render=explicit'
    script.async = true
    script.defer = true
    script.addEventListener('load', () => resolve(), { once: true })
    script.addEventListener('error', () => reject(new Error('reCAPTCHA failed to load')), { once: true })
    document.head.append(script)
  })

  return recaptchaScriptPromise
}

function runWhenRecaptchaReady(recaptcha: RecaptchaApi) {
  return new Promise<void>((resolve) => {
    if (recaptcha.ready) {
      recaptcha.ready(resolve)
      return
    }

    resolve()
  })
}

export function useRecaptchaToken() {
  const config = useRuntimeConfig()

  const siteKey = computed(() => {
    return typeof config.public.recaptchaSiteKey === 'string'
      ? config.public.recaptchaSiteKey
      : ''
  })

  async function executeRecaptcha() {
    if (!import.meta.client || !siteKey.value) {
      return ''
    }

    await loadRecaptchaScript()

    const recaptcha = window.grecaptcha
    if (!recaptcha) {
      throw new Error('reCAPTCHA is unavailable')
    }

    await runWhenRecaptchaReady(recaptcha)

    const container = document.createElement('div')
    container.hidden = true
    document.body.append(container)

    return await new Promise<string>((resolve, reject) => {
      const widgetId = recaptcha.render(container, {
        'sitekey': siteKey.value,
        'size': 'invisible',
        'callback': (token: string) => {
          recaptcha.reset(widgetId)
          container.remove()
          resolve(token)
        },
        'error-callback': () => {
          recaptcha.reset(widgetId)
          container.remove()
          reject(new Error('reCAPTCHA verification failed'))
        },
        'expired-callback': () => {
          recaptcha.reset(widgetId)
          container.remove()
          reject(new Error('reCAPTCHA token expired'))
        }
      })

      recaptcha.execute(widgetId)
    })
  }

  return { executeRecaptcha }
}
