import { test, expect } from './fixtures';

test('usuário logado consegue criar um artigo', async ({ loggedInPage: page }, testInfo) => {
  const title = `Artigo ${Date.now()}`;

  await page.goto('/editor');
  await page.getByPlaceholder('Article Title').fill(title);
  await page.getByPlaceholder("What's this article about?").fill('Resumo do artigo');
  await page.getByPlaceholder('Write your article (in markdown)').fill('Conteúdo do artigo de teste.');
  await page.getByRole('button', { name: 'Publish Article' }).click();

  await expect(page).not.toHaveURL(/\/editor/);

  let attempts = 0;
  try {
    await expect(async () => {
      attempts++;
      await page.getByRole('button', { name: 'Global Feed' }).click();
      await page.getByText(title).first().click({ timeout: 2000 });
      await expect(page).toHaveURL(/\/article\//, { timeout: 2000 });
    }).toPass({ timeout: 20000 });
  } finally {
    testInfo.annotations.push({ type: 'inner-attempts', description: String(attempts) });
  }

  await expect(page.getByRole('heading', { name: title })).toBeVisible();
});