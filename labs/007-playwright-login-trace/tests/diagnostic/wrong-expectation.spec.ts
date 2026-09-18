import { test, expect } from '@playwright/test';

test('错误预期：登录成功后出现账户已冻结', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('用户名').fill('reader');
  await page.getByLabel('密码').fill('local-pass-2026');
  await page.getByRole('button', { name: '登录' }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole('heading', { name: '账户已冻结' })).toBeVisible({ timeout: 1_500 });
});
