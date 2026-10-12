import { test, expect } from './fixtures';

test('usuário logado consegue criar um artigo', async ({ loggedInPage: page }) => {
  const title = `Artigo ${Date.now()}`;

  await page.goto('/editor');
  await page.getByPlaceholder('Article Title').fill(title);
  await page.getByPlaceholder("What's this article about?").fill('Resumo do artigo');
  await page.getByPlaceholder('Write your article (in markdown)').fill('Conteúdo do artigo de teste.');
  await page.getByRole('button', { name: 'Publish Article' }).click();

  await expect(page).not.toHaveURL(/\/editor/);

  await page.getByRole('button', { name: 'Global Feed' }).click();
  const articleLink = page.getByText(title).first();
  await expect(articleLink).toBeVisible();

  await articleLink.click();
  await expect(page).toHaveURL(/\/article\//);
  await expect(page.getByRole('heading', { name: title })).toBeVisible();
});