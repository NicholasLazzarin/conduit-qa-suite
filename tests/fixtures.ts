import { test as base, expect, Page } from '@playwright/test';

const API = 'http://localhost:8000/api';

type User = { username: string; email: string; password: string };

export const test = base.extend<{ newUser: User; loggedInPage: Page }>({
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

  loggedInPage: async ({ page, request, newUser }, use) => {
    const res = await request.post(`${API}/users/login`, {
      data: { user: { email: newUser.email, password: newUser.password } },
    });
    expect(res.ok()).toBeTruthy();
    const { user } = await res.json();

    await page.addInitScript((token) => {
      window.localStorage.setItem('jwt', token);
    }, user.token);

    await page.goto('/');
    await use(page);
  },
});

export { expect };