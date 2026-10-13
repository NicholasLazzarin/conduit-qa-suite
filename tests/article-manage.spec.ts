import { test, expect } from './fixtures';

const API = 'http://localhost:8000/api';

test('autor consegue editar o conteúdo de um artigo', async ({ loggedInPage: page, newArticle }) => {
  const newBody = `Conteúdo editado ${Date.now()}`;

  await page.goto(`/editor/${newArticle.slug}`);
  await page.waitForLoadState('networkidle');
  await expect(page.getByPlaceholder('Article Title')).toHaveValue(newArticle.title);

  await page.getByPlaceholder('Write your article (in markdown)').fill(newBody);
  await page.getByRole('button', { name: 'Publish Article' }).click();

  await page.goto(`/article/${newArticle.slug}`);
  await expect(page.getByText(newBody)).toBeVisible();
});

test('autor consegue apagar um artigo', async ({ loggedInPage: page, request, newArticle }) => {
  await page.goto(`/article/${newArticle.slug}`);
  await page.getByRole('button', { name: 'Delete Article' }).first().click();

  await expect
    .poll(async () => (await request.get(`${API}/articles/${newArticle.slug}`)).status())
    .toBe(404);
});