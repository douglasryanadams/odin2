// @ts-check
import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('http://localhost:8080/');
  await expect(page).toHaveTitle(/Odin/);
});

test('has search box', async ({ page }) => {
  await page.goto('http://localhost:8080/');
  await expect(page.getByLabel('Search')).toBeVisible()
});

