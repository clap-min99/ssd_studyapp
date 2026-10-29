// Run against the local preview DB with Playwright Core installed in reports/browser-check.
// shortcut: Windows Chrome and local ports 5173/8000 only; generalize when adding browser CI.
const { chromium } = require('../reports/browser-check/node_modules/playwright-core');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');

(async () => {
  const output = path.resolve('reports/browser-check');
  await fs.mkdir(output, { recursive: true });
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
  });
  const results = [];
  try {
    for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }, { width: 320, height: 740 }]) {
      const context = await browser.newContext({ viewport });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('response', response => {
        if (response.url().includes('/api/') && response.status() >= 400) {
          errors.push(`${response.status()} ${response.url()}`);
        }
      });
      const origin = 'http://127.0.0.1:5173';
      const bootstrap = await context.request.get(`${origin}/api/auth/session/`);
      assert.equal(bootstrap.status(), 200);
      const session = await bootstrap.json();
      const login = await context.request.post(`${origin}/api/auth/session/login/`, {
        headers: { 'X-CSRFToken': session.csrfToken, Origin: origin },
        data: { username: 'firmware-preview', password: process.env.FIRMWARE_PREVIEW_PASSWORD },
      });
      assert.equal(login.status(), 200, await login.text());
      await page.goto(`${origin}/chapters`);
      await page.locator('.launch-screen').waitFor({ state: 'detached' });
      await page.getByRole('button', { name: '펌웨어 동작 원리', exact: true }).click();
      await page.getByRole('heading', { name: 'C 코드에서 레지스터까지', exact: true }).click();
      await page.getByRole('heading', { name: 'C 코드에서 레지스터까지', exact: true, level: 1 }).waitFor();
      await page.locator('.chapter-card').nth(2).waitFor();
      assert.equal(await page.locator('.chapter-card').count(), 3);
      await page.locator('.chapter-card').first().click();
      for (let index = 1; index <= 3; index++) {
        await page.locator('.lesson-content').waitFor();
        await page.getByRole('heading', { name: new RegExp(`^${index}\\.`) }).waitFor();
        if (index > 1) assert.equal(await page.evaluate(() => scrollY), 0, '새 레슨은 맨 위에서 시작해야 합니다.');
        assert.equal(await page.locator('pre code.language-c').count(), 1);
        assert.ok(await page.locator('.lesson-content table').count() >= 1);
        const details = page.locator('.lesson-content details');
        await details.locator('summary').click();
        assert.equal(await details.getAttribute('open'), '');
        assert.ok(await details.locator('p').first().isVisible());
        const geometry = await page.evaluate(() => ({
          viewport: innerWidth,
          documentWidth: document.documentElement.scrollWidth,
          code: [...document.querySelectorAll('.lesson-content pre')].map(element => ({
            width: element.clientWidth, content: element.scrollWidth,
          })),
        }));
        assert.ok(geometry.documentWidth <= viewport.width, JSON.stringify(geometry));
        await page.screenshot({ path: path.join(output, `${viewport.width}-lesson-${index}.png`), fullPage: true });
        results.push({ viewport: viewport.width, lesson: index, ...geometry });
        if (index < 3) {
          await page.getByRole('button', { name: /^다음 레슨:/ }).click();
        } else {
          await page.getByRole('button', { name: '← 이전 레슨', exact: true }).click();
          await page.getByRole('heading', { name: /^2\./ }).waitFor();
        }
      }
      assert.deepEqual(errors, []);
      await context.close();
    }
    await fs.writeFile(path.join(output, 'results.json'), JSON.stringify(results, null, 2));
    console.log(JSON.stringify({ checked: results.length, results }, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
