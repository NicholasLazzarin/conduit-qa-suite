import { test as base, expect } from '@playwright/test';

const API = 'http://localhost:8000/api';

type User = { username: string; email: string; password: string };

export const test = base.extend<{ newUser: User }>({
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
});

export { expect };