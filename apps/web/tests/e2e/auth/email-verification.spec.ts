import { expect, test } from '@playwright/test'

import { captchaToken, csrfToken, prepareAuthPage } from './helpers'

test.beforeEach(async ({ context, page }) => {
  await prepareAuthPage(context, page)
})

test('email verification submits a six digit OTP to the auth api', async ({ page }) => {
  await page.route('**/api/auth/email-verification/confirm/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.headers()['x-csrftoken']).toBe(csrfToken)
    expect(request.postDataJSON()).toEqual({
      email: 'user@example.com',
      otp: '123456'
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

  await page.goto('/verify-email?email=user%40example.com')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Verification code').fill('123456')
  await page.getByRole('button', { name: 'Verify email' }).click()

  await expect(page.getByRole('status')).toContainText(
    'Email verified for user@example.com.'
  )
})

test('email verification resend submits email and captcha token', async ({ page }) => {
  await page.route('**/api/auth/email-verification/request/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.headers()['x-csrftoken']).toBe(csrfToken)
    expect(request.postDataJSON()).toEqual({
      email: 'user@example.com',
      captcha_token: captchaToken
    })

    await route.fulfill({
      contentType: 'application/json',
      status: 202,
      body: JSON.stringify({ detail: 'If an account exists, a verification code will be sent.' })
    })
  })

  await page.goto('/verify-email?email=user%40example.com')
  await page.waitForLoadState('networkidle')
  await page.getByRole('button', { name: 'Send a new code' }).click()

  await expect(page.getByRole('status')).toContainText(
    'If an account exists, a verification code will be sent.'
  )
})

test('email verification shows invalid otp details', async ({ page }) => {
  await page.route('**/api/auth/email-verification/confirm/', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      status: 400,
      body: JSON.stringify({ otp: ['Invalid verification code.'] })
    })
  })

  await page.goto('/verify-email?email=user%40example.com')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Verification code').fill('123456')
  await page.getByRole('button', { name: 'Verify email' }).click()

  await expect(page.getByRole('alert')).toContainText('Invalid verification code.')
})
