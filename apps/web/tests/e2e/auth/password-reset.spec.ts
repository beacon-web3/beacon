import { expect, test } from '@playwright/test'

import { csrfToken, prepareAuthPage, recaptchaToken, validPassword } from './helpers'

test.beforeEach(async ({ context, page }) => {
  await prepareAuthPage(context, page)
})

test('password reset request shows network failures distinctly', async ({ page }) => {
  await page.route('**/api/auth/password-reset/', async (route) => {
    await route.abort('failed')
  })

  await page.goto('/reset-password')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Email address').fill('user@example.com')
  await page.getByRole('button', { name: 'Send reset instructions' }).click()

  await expect(page.getByRole('alert')).toContainText(
    'Network error. Check your connection and try again.'
  )
})

test('password reset submits generic request', async ({ page }) => {
  await page.route('**/api/auth/password-reset/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.headers()['x-csrftoken']).toBe(csrfToken)
    expect(request.postDataJSON()).toEqual({
      email: 'user@example.com',
      recaptcha_token: recaptchaToken
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

test('password reset confirm submits uid token and password to the auth api', async ({ page }) => {
  await page.route('**/api/auth/password-reset/confirm/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.headers()['x-csrftoken']).toBe(csrfToken)
    expect(request.postDataJSON()).toEqual({
      uid: 'uid-123',
      token: 'token-456',
      password: validPassword
    })

    await route.fulfill({
      contentType: 'application/json',
      status: 200,
      body: JSON.stringify({ detail: 'Password reset complete.' })
    })
  })

  await page.goto('/reset-password/confirm?uid=uid-123&token=token-456')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('New password').fill(validPassword)
  await page.getByRole('button', { name: 'Reset password' }).click()

  await expect(page.getByRole('status')).toContainText(
    'Password has been reset.'
  )
})

test('password reset confirm shows invalid token details', async ({ page }) => {
  await page.route('**/api/auth/password-reset/confirm/', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      status: 400,
      body: JSON.stringify({ non_field_errors: ['Invalid password reset token.'] })
    })
  })

  await page.goto('/reset-password/confirm?uid=uid-123&token=token-456')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('New password').fill(validPassword)
  await page.getByRole('button', { name: 'Reset password' }).click()

  await expect(page.getByRole('alert')).toContainText('Invalid password reset token.')
})

test('password reset confirm blocks weak passwords before calling the auth api', async ({ page }) => {
  let resetConfirmRequested = false

  await page.route('**/api/auth/password-reset/confirm/', async (route) => {
    resetConfirmRequested = true
    await route.fulfill({ status: 500 })
  })

  await page.goto('/reset-password/confirm?uid=uid-123&token=token-456')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('New password').fill('weak')
  await page.getByRole('button', { name: 'Reset password' }).click()

  await expect(page.getByText(
    'Password must be longer than 8 characters'
  )).toBeVisible()
  expect(resetConfirmRequested).toBe(false)
})
