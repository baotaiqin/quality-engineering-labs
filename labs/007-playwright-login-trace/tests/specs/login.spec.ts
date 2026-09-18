import { test, expect } from '@playwright/test';

const account = { username: 'reader', password: 'local-pass-2026' };

test('正确账号登录后可以访问概览页', async ({ page }, testInfo) => {
  await page.goto('/login');
  await expect(page.getByRole('heading', { name: '登录账户' })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('login-page.png') });

  await page.getByLabel('用户名').fill(account.username);
  await page.getByLabel('密码').fill(account.password);
  await page.getByRole('button', { name: '登录' }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole('heading', { name: '欢迎回来，reader' })).toBeVisible();
  await expect(page.getByText('当前会话有效')).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath('dashboard.png') });
});

test('错误密码显示明确提示且不进入概览页', async ({ page }, testInfo) => {
  await page.goto('/login');
  await page.getByLabel('用户名').fill(account.username);
  await page.getByLabel('密码').fill('wrong-pass');
  await page.getByRole('button', { name: '登录' }).click();

  await expect(page.getByRole('alert')).toHaveText('用户名或密码错误');
  await expect(page).toHaveURL(/\/login$/);
  await page.screenshot({ path: testInfo.outputPath('invalid-password.png') });
});

test('未登录时无法直接打开概览页', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole('heading', { name: '登录账户' })).toBeVisible();
});

test('退出后受保护页面重新要求登录', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('用户名').fill(account.username);
  await page.getByLabel('密码').fill(account.password);
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByRole('heading', { name: '欢迎回来，reader' })).toBeVisible();

  await page.getByRole('button', { name: '退出登录' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/login$/);
});
