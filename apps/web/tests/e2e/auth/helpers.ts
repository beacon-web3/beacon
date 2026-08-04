import type { BrowserContext, Page } from '@playwright/test'

export const validPassword = 'Strong-password-12345!'
export const csrfToken = 'playwright-csrf-token'
export const captchaToken = 'playwright-captcha-jwt'

export async function prepareAuthPage(context: BrowserContext, page: Page) {
  await context.addCookies([
    {
      name: 'csrftoken',
      value: csrfToken,
      url: 'http://127.0.0.1:3000'
    }
  ])

  await page.route('**/api/cap/challenge', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      status: 200,
      body: JSON.stringify({
        token: 'test-challenge-token',
        challenges: []
      })
    })
  })

  await page.route('**/api/cap/redeem', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      status: 200,
      body: JSON.stringify({
        token: captchaToken
      })
    })
  })
}
