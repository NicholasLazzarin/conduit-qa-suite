import { test, expect } from '@playwright/test';

test('usuário consegue se cadastrar', async ({ page }) => {
  const id = Date.now();
  const username = `user${id}`;

  await page.goto('/register');

  await page.getByPlaceholder('Username').fill(username);
  await page.getByPlaceholder('Email').fill(`${username}@example.com`);
  await page.getByPlaceholder('Password').fill('Senha@12345');
  await page.getByRole('button', { name: 'Sign up' }).click();

  await expect(page.getByRole('link', { name: username })).toBeVisible();
});