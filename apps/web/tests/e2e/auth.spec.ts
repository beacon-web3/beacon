import { expect, test } from '@playwright/test'

const validPassword = 'Strong-password-12345!'
const csrfToken = 'playwright-csrf-token'
const recaptchaToken = 'playwright-recaptcha-token'

test.beforeEach(async ({ context, page }) => {
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
      recaptcha_token: recaptchaToken
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

test('email verification resend submits email and recaptcha token', async ({ page }) => {
  await page.route('**/api/auth/email-verification/request/', async (route) => {
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

test('signup removes hidden recaptcha containers when cleanup reset fails', async ({ page }) => {
  let signupRequested = false

  await page.route('**/api/auth/signup/', async (route) => {
    signupRequested = true
    await route.fulfill({ status: 500 })
  })

  await page.goto('/signup')
  await page.waitForLoadState('networkidle')
  await page.evaluate(() => {
    const recaptchaWindow = window as unknown as {
      grecaptcha: {
        execute: () => never
        ready: (readyCallback: () => void) => void
        render: () => number
        reset: () => never
      }
    }

    recaptchaWindow.grecaptcha = {
      ready: (readyCallback: () => void) => readyCallback(),
      render: () => 1,
      execute: () => {
        throw new Error('execute failed')
      },
      reset: () => {
        throw new Error('reset failed')
      }
    }
  })

  await page.getByLabel('Display name').fill('Reader One')
  await page.getByLabel('Username').fill('readerone')
  await page.getByLabel('Email address').fill('new@example.com')
  await page.getByLabel('Password', { exact: true }).fill(validPassword)
  await page.getByLabel('Confirm password').fill(validPassword)
  await page.getByRole('button', { name: 'Create account' }).click()

  await expect(page.getByRole('alert')).toContainText(
    'Network error. Check your connection and try again.'
  )
  await expect.poll(async () => page.locator('body > div[hidden]').count()).toBe(0)
  expect(signupRequested).toBe(false)
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
