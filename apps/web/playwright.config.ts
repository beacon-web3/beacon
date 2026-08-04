import { defineConfig, devices } from '@playwright/test'

const captchaSecret = process.env.CAPTCHA_SECRET ?? 'playwright-test-secret'
process.env.CAPTCHA_SECRET = captchaSecret

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  reporter: 'html',
  use: {
    baseURL: 'http://127.0.0.1:3000',
    trace: 'on-first-retry'
  },
  webServer: {
    command: `CAPTCHA_SECRET=${captchaSecret} pnpm dev --host 127.0.0.1`,
    url: 'http://127.0.0.1:3000',
    reuseExistingServer: false,
    timeout: 120_000
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ]
})
