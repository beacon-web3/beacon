import { expect, test } from '@playwright/test'

test('signup submits email to the auth api', async ({ page }) => {
  await page.route('**/api/auth/signup/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.postDataJSON()).toEqual({ email: 'new@example.com' })

    await route.fulfill({
      contentType: 'application/json',
      status: 201,
      body: JSON.stringify({ account: { id: 1, email: 'new@example.com' } })
    })
  })

  await page.goto('/signup')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Email address').fill('new@example.com')
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByRole('status')).toContainText(
    'Account created for new@example.com.'
  )
})

test('login submits email to the auth api', async ({ page }) => {
  await page.route('**/api/auth/login/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.postDataJSON()).toEqual({ email: 'user@example.com' })

    await route.fulfill({
      contentType: 'application/json',
      status: 200,
      body: JSON.stringify({ account: { id: 1, email: 'user@example.com' } })
    })
  })

  await page.goto('/login')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Email address').fill('user@example.com')
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
  await page.getByLabel('Email address').fill('existing@example.com')
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByRole('alert')).toContainText(
    'We could not create that account.'
  )
})
