import { expect, test } from '@playwright/test'

const validPassword = 'Strong-password-12345!'

test('signup submits account fields to the auth api', async ({ page }) => {
  await page.route('**/api/auth/signup/', async (route) => {
    const request = route.request()

    expect(request.method()).toBe('POST')
    expect(request.postDataJSON()).toEqual({
      email: 'new@example.com',
      username: 'readerone',
      display_name: 'Reader One',
      password: validPassword,
      password_confirmation: validPassword,
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
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByLabel('Confirm password').fill(validPassword)
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
      password: validPassword,
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
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
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
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByLabel('Confirm password').fill(validPassword)
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByRole('alert')).toContainText(
    'We could not create that account.'
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
