import type { BrowserContext, Page } from '@playwright/test'

export const validPassword = 'Strong-password-12345!'
export const csrfToken = 'playwright-csrf-token'
export const recaptchaToken = 'playwright-recaptcha-token'

export async function prepareAuthPage(context: BrowserContext, page: Page) {
  await context.addCookies([
    {
      name: 'csrftoken',
      value: csrfToken,
      url: 'http://127.0.0.1:3000'
    }
  ])

  await page.addInitScript((token) => {
    let callback: ((value: string) => void) | undefined
    const recaptchaWindow = window as unknown as {
      grecaptcha: {
        execute: () => void
        ready: (readyCallback: () => void) => void
        render: (_container: HTMLElement, parameters: { callback: (value: string) => void }) => number
        reset: () => undefined
      }
    }

    recaptchaWindow.grecaptcha = {
      ready: (readyCallback: () => void) => readyCallback(),
      render: (_container: HTMLElement, parameters: { callback: (value: string) => void }) => {
        callback = parameters.callback
        return 1
      },
      execute: () => callback?.(token),
      reset: () => undefined
    }
  }, recaptchaToken)
}
