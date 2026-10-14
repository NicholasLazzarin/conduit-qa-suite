import { test, expect } from './fixtures';

const API = 'http://localhost:8000/api';

const articlePayload = (title: string) => ({
  article: { title, description: 'Resumo', body: 'Conteúdo', tagList: [] },
});

test('login com senha errada é recusado com 401', async ({ request, newUser }) => {
  const res = await request.post(`${API}/users/login`, {
    data: { user: { email: newUser.email, password: 'senha-errada' } },
  });
  expect(res.status()).toBe(401);
});

test('criar artigo sem token é recusado', async ({ request }) => {
  const res = await request.post(`${API}/articles`, {
    data: articlePayload(`Sem token ${Date.now()}`),
  });
  // Suposição: 401. Se vier outro número, o teste mostra qual é.
  expect(res.status()).toBe(401);
});

test('título repetido gera um slug diferente', async ({ request, authToken, newArticle }) => {
  const res = await request.post(`${API}/articles`, {
    headers: { Authorization: `Bearer ${authToken}` },
    data: articlePayload(newArticle.title),
  });
  expect(res.status()).toBe(201);

  const body = await res.json();
  expect(body.article.slug).not.toBe(newArticle.slug);
});

test('criar artigo sem título retorna 422', async ({ request, authToken }) => {
  const res = await request.post(`${API}/articles`, {
    headers: { Authorization: `Bearer ${authToken}` },
    data: { article: { description: 'Resumo', body: 'Conteúdo', tagList: [] } },
  });
  expect(res.status()).toBe(422);
});

test('outro usuário não consegue editar o artigo de alguém', async ({ request, newArticle }) => {
  const id = `${Date.now()}${Math.floor(Math.random() * 1000)}`;
  const other = { username: `other${id}`, email: `other${id}@example.com`, password: 'Senha@12345' };

  await request.post(`${API}/users`, { data: { user: other } });
  const login = await request.post(`${API}/users/login`, {
    data: { user: { email: other.email, password: other.password } },
  });
  const { user } = await login.json();

  const res = await request.put(`${API}/articles/${newArticle.slug}`, {
    headers: { Authorization: `Bearer ${user.token}` },
    data: { article: { body: 'Tentativa de edição por outro usuário' } },
  });
  // Suposição: 403. Pode ser 401 ou 404 neste backend.
  expect(res.status()).toBe(403);
});

test('listar artigos é público e retorna uma lista', async ({ request }) => {
  const res = await request.get(`${API}/articles?limit=5&offset=0`);
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(Array.isArray(body.articles)).toBeTruthy();
});