import { test, expect } from './fixtures';

test('usuário cadastrado consegue fazer login', async ({ page, newUser }) => {
  await page.goto('/login');
  await page.getByPlaceholder('Email').fill(newUser.email);
  await page.getByPlaceholder('Password').fill(newUser.password);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByRole('link', { name: newUser.username })).toBeVisible();
});