import { expect, test } from '@playwright/test'

test('home page loads', async ({ page }) => {
  await page.goto('/')

  await expect(page).toHaveTitle(/Beacon/i)
  await expect(
    page.getByRole('heading', {
      name: 'Find the books before everyone else does.'
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

test('home page fits narrow mobile screens', async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 900 })
  await page.goto('/')

  await expect(
    page.getByText('Early book signals', { exact: true })
  ).toBeVisible()

  const horizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth
  )

  expect(horizontalOverflow).toBeLessThanOrEqual(0)
})

test('french home page loads with ltr direction', async ({ page }) => {
  await page.goto('/fr')

  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr')
  await expect(
    page.getByRole('heading', {
      name: /Trouvez les livres avant tout le monde\./
    })
  ).toBeVisible()
})
