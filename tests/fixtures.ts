import { test as base, expect, Page } from '@playwright/test';

const API = 'http://localhost:8000/api';

type User = { username: string; email: string; password: string };
type Article = { title: string; slug: string };

export const test = base.extend<{
  newUser: User;
  authToken: string;
  loggedInPage: Page;
  newArticle: Article;
}>({
  newUser: async ({ request }, use) => {
    const id = `${Date.now()}${Math.floor(Math.random() * 1000)}`;
    const user = {
      username: `user${id}`,
      email: `user${id}@example.com`,
      password: 'Senha@12345',
    };

    const res = await request.post(`${API}/users`, { data: { user } });
    expect(res.ok()).toBeTruthy();

    await use(user);
  },

  authToken: async ({ request, newUser }, use) => {
    const res = await request.post(`${API}/users/login`, {
      data: { user: { email: newUser.email, password: newUser.password } },
    });
    expect(res.ok()).toBeTruthy();
    const { user } = await res.json();

    await use(user.token);
  },

  loggedInPage: async ({ page, authToken }, use) => {
    await page.addInitScript((token) => {
      window.localStorage.setItem('jwt', token);
    }, authToken);

    await page.goto('/');
    await use(page);
  },

  newArticle: async ({ request, authToken }, use) => {
    const title = `Artigo API ${Date.now()}${Math.floor(Math.random() * 1000)}`;

    const res = await request.post(`${API}/articles`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: {
        article: {
          title,
          description: 'Resumo criado pela API',
          body: 'Conteúdo criado pela API.',
          tagList: [],
        },
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    const article = body.article ?? body;

    await use({ title, slug: article.slug });
  },
});

export { expect };