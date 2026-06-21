import { expect, test } from '@playwright/test'

test('home page loads', async ({ page }) => {
  await page.goto('/')

  await expect(page).toHaveTitle(/Beacon/i)
  await expect(
    page.getByRole('heading', {
      name: 'Beacon helps people discover valuable books before they become obvious.'
    })
  ).toBeVisible()
  await expect(page.getByRole('link', { name: /join early access/i }).first()).toHaveAttribute(
    'href',
    '/signup'
  )
  await expect(page.getByRole('link', { name: /log in/i }).first()).toHaveAttribute(
    'href',
    '/login'
  )
})

test('french home page loads with ltr direction', async ({ page }) => {
  await page.goto('/fr')

  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr')
  await expect(
    page.getByRole('heading', {
      name: /Beacon aide à découvrir des livres précieux avant qu'ils ne deviennent évidents\./
    })
  ).toBeVisible()
})
