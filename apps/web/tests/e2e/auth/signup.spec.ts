import { expect, test } from '@playwright/test'

import { captchaToken, csrfToken, prepareAuthPage, validPassword } from './helpers'

test.beforeEach(async ({ context, page }) => {
  await prepareAuthPage(context, page)
})

test('signup submits account fields to the auth api', async ({ page }) => {
  await page.route('**/api/auth/signup/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.headers()['accept-language']).toBe('en')
    expect(request.headers()['x-csrftoken']).toBe(csrfToken)
    expect(request.postDataJSON()).toEqual({
      email: 'new@example.com',
      username: 'readerone',
      display_name: 'Reader One',
      password: validPassword,
      password_confirmation: validPassword,
      captcha_token: captchaToken
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
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByLabel('Confirm password').fill(validPassword)
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByRole('status')).toContainText(
    'Account created for new@example.com.'
  )
})

test('signup sends the active locale to the auth api', async ({ page }) => {
  await page.route('**/api/auth/signup/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.headers()['accept-language']).toBe('fr')
    expect(request.headers()['x-csrftoken']).toBe(csrfToken)

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

  await page.goto('/fr/signup')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Nom affiché').fill('Reader One')
  await page.getByLabel('Nom d\'utilisateur').fill('readerone')
  await page.getByLabel('Adresse email').fill('new@example.com')
  await page.getByLabel('Mot de passe', { exact: true }).fill(validPassword)
  await page.getByLabel('Confirmer le mot de passe').fill(validPassword)
  await page.getByRole('button', { name: 'Créer un compte' }).click()

  await expect(page.getByRole('status')).toContainText(
    'Compte créé pour new@example.com.'
  )
})

test('signup shows safe api validation details', async ({ page }) => {
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
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByLabel('Confirm password').fill(validPassword)
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByRole('alert')).toContainText(
    'An account with this email already exists.'
  )
})

test('signup blocks weak passwords before calling the auth api', async ({ page }) => {
  let signupRequested = false

  await page.route('**/api/auth/signup/', async (route) => {
    signupRequested = true
    await route.fulfill({ status: 500 })
  })

  await page.goto('/signup')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Display name').fill('Reader One')
  await page.getByLabel('Username').fill('readerone')
  await page.getByLabel('Email address').fill('new@example.com')
  await page.getByLabel('Password', { exact: true }).fill('weak')
  await page.getByLabel('Confirm password').fill('weak')
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByText(
    'Password must be longer than 8 characters'
  )).toBeVisible()
  expect(signupRequested).toBe(false)
})

test('signup shows password requirements progressively', async ({ page }) => {
  await page.goto('/signup')
  await page.waitForLoadState('networkidle')

  const passwordInput = page.getByLabel('Password', { exact: true })

  await expect(page.getByText(
    'Password must be longer than 8 characters'
  )).toBeVisible()
  await expect(page.getByText('Password must include a lowercase letter.')).toHaveCount(0)

  await passwordInput.fill('longpassword')
  await expect(page.getByText(
    'Password must include an uppercase letter'
  )).toBeVisible()
  await expect(page.getByText('Password must include a number.')).toHaveCount(0)

  await passwordInput.fill('Longpassword')
  await expect(page.getByText('Password must include a number')).toBeVisible()
  await expect(page.getByText('Password must include a special character.')).toHaveCount(0)

  await passwordInput.fill('Longpassword1')
  await expect(page.getByText(
    'Password must include a special character'
  )).toBeVisible()

  await passwordInput.fill(validPassword)
  await expect(page.getByText('Password must include a special character.')).toHaveCount(0)
})

test('signup password fields can toggle visibility', async ({ page }) => {
  await page.goto('/signup')
  await page.waitForLoadState('networkidle')

  const passwordInput = page.getByLabel('Password', { exact: true })
  const passwordConfirmationInput = page.getByLabel('Confirm password')

  await expect(passwordInput).toHaveAttribute('type', 'password')
  await expect(passwordConfirmationInput).toHaveAttribute('type', 'password')

  await page.getByRole('button', { name: 'Show password' }).first().click()
  await expect(passwordInput).toHaveAttribute('type', 'text')
  await page.getByRole('button', { name: 'Hide password' }).click()
  await expect(passwordInput).toHaveAttribute('type', 'password')

  await page.getByRole('button', { name: 'Show password' }).nth(1).click()
  await expect(passwordConfirmationInput).toHaveAttribute('type', 'text')
  await page.getByRole('button', { name: 'Hide password' }).click()
  await expect(passwordConfirmationInput).toHaveAttribute('type', 'password')
})

test('signup blocks mismatched password confirmation', async ({ page }) => {
  let signupRequested = false

  await page.route('**/api/auth/signup/', async (route) => {
    signupRequested = true
    await route.fulfill({ status: 500 })
  })

  await page.goto('/signup')
  await page.waitForLoadState('networkidle')
  await page.getByLabel('Display name').fill('Reader One')
  await page.getByLabel('Username').fill('readerone')
  await page.getByLabel('Email address').fill('new@example.com')
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByLabel('Confirm password').fill('Different-password-12345!')
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByText('Passwords do not match')).toBeVisible()
  expect(signupRequested).toBe(false)
})
