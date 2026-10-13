import { test, expect } from './fixtures';

test('artigo criado pela API abre na página do artigo', async ({ loggedInPage: page, newArticle }) => {
  await page.goto(`/article/${newArticle.slug}`);
  await expect(page.getByRole('heading', { name: newArticle.title })).toBeVisible();
});