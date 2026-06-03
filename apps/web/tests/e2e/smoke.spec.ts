import { expect, test } from '@playwright/test'

test('home page loads', async ({ page }) => {
  await page.goto('/')

  await expect(page).toHaveTitle(/Beacon/i)
  await expect(
    page.getByRole('heading', {
      name: 'Find signal through the noise.'
    })
  ).toBeVisible()
  await expect(page.getByRole('link', { name: /sign up/i }).first()).toHaveAttribute(
    'href',
    '/signup'
  )
  await expect(page.getByRole('link', { name: /log in/i }).first()).toHaveAttribute(
    'href',
    '/login'
  )
})

test('persian home page loads with rtl direction', async ({ page }) => {
  await page.goto('/fa')

  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
  await expect(page.getByRole('heading', { name: 'سیگنال را از میان نویز پیدا کن.' })).toBeVisible()
})
