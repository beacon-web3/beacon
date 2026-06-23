import { expect, test } from '@playwright/test'

test('signup submits account fields to the auth api', async ({ page }) => {
  await page.route('**/api/auth/signup/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.postDataJSON()).toEqual({
      email: 'new@example.com',
      username: 'readerone',
      display_name: 'Reader One',
      password: 'strong-password-12345',
      recaptcha_token: ''
    })

    await route.fulfill({
      contentType: 'application/json',
      status: 201,
      body: JSON.stringify({
        account: {
          id: 1,
          email: 'new@example.com',
          username: 'readerone',
          display_name: 'Reader One'
        }
      })
    })
  })

  await page.goto('/signup')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Display name').fill('Reader One')
  await page.getByLabel('Username').fill('readerone')
  await page.getByLabel('Email address').fill('new@example.com')
  await page.getByLabel('Password').fill('strong-password-12345')
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByRole('status')).toContainText(
    'Account created for new@example.com.'
  )
})

test('login submits identifier and password to the auth api', async ({ page }) => {
  await page.route('**/api/auth/login/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.postDataJSON()).toEqual({
      identifier: 'readerone',
      password: 'strong-password-12345',
      recaptcha_token: ''
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
  await page.getByLabel('Password').fill('strong-password-12345')
  await page.getByRole('button', { name: 'Log in' }).click()

  await expect(page.getByRole('status')).toContainText(
    'Logged in as user@example.com.'
  )
})

test('signup shows api failures', async ({ page }) => {
  await page.route('**/api/auth/signup/', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      status: 400,
      body: JSON.stringify({ email: ['An account with this email already exists.'] })
    })
  })

  await page.goto('/signup')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Display name').fill('Reader One')
  await page.getByLabel('Username').fill('readerone')
  await page.getByLabel('Email address').fill('existing@example.com')
  await page.getByLabel('Password').fill('strong-password-12345')
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByRole('alert')).toContainText(
    'We could not create that account.'
  )
})

test('password reset submits generic request', async ({ page }) => {
  await page.route('**/api/auth/password-reset/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.postDataJSON()).toEqual({
      email: 'user@example.com',
      recaptcha_token: ''
    })

    await route.fulfill({
      contentType: 'application/json',
      status: 202,
      body: JSON.stringify({
        detail: 'If an account exists, password reset instructions will be sent.'
      })
    })
  })

  await page.goto('/reset-password')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Email address').fill('user@example.com')
  await page.getByRole('button', { name: 'Send reset instructions' }).click()

  await expect(page.getByRole('status')).toContainText(
    'If an account exists, reset instructions will be sent.'
  )
})
