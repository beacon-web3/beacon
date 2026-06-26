import { expect, test } from '@playwright/test'

import { csrfToken, prepareAuthPage, recaptchaToken, validPassword } from './helpers'

test.beforeEach(async ({ context, page }) => {
  await prepareAuthPage(context, page)
})

test('login submits identifier and password to the auth api', async ({ page }) => {
  await page.route('**/api/auth/login/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.headers()['x-csrftoken']).toBe(csrfToken)
    expect(request.postDataJSON()).toEqual({
      identifier: 'readerone',
      password: validPassword,
      recaptcha_token: recaptchaToken
    })

    await route.fulfill({
      contentType: 'application/json',
      status: 200,
      body: JSON.stringify({
        account: {
          id: 1,
          email: 'user@example.com',
          username: 'readerone',
          display_name: 'Reader One'
        }
      })
    })
  })

  await page.goto('/login')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Email or username').fill('readerone')
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByRole('button', { name: 'Log in' }).click()

  await expect(page.getByRole('status')).toContainText(
    'Logged in as user@example.com.'
  )
})

test('login shows throttling failures distinctly', async ({ page }) => {
  await page.route('**/api/auth/login/', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      status: 429,
      body: JSON.stringify({ detail: 'Request was throttled.' })
    })
  })

  await page.goto('/login')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Email or username').fill('readerone')
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByRole('button', { name: 'Log in' }).click()

  await expect(page.getByRole('alert')).toContainText(
    'Too many attempts. Try again later.'
  )
})

test('login hides unsafe api detail responses', async ({ page }) => {
  await page.route('**/api/auth/login/', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      status: 403,
      body: JSON.stringify({ detail: 'CSRF Failed: Referer checking failed.' })
    })
  })

  await page.goto('/login')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Email or username').fill('readerone')
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByRole('button', { name: 'Log in' }).click()

  const alert = page.getByRole('alert')
  await expect(alert).toContainText('We could not log you in.')
  await expect(alert).not.toContainText('CSRF Failed')
})
