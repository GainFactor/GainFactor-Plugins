import AxeBuilder from '@axe-core/playwright';
import { chromium } from '@playwright/test';
import { spawn } from 'node:child_process';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

const failures = [];
const warnings = [];
const brandContrastExemption = ".gainfactor-docs-layout [data-sidebar-placeholder] a[data-active='true']";
const capabilities = JSON.parse(readFileSync('portal-capabilities.json', 'utf8'));
const expectedComponents = new Set(['FieldList', 'Panel', 'Board', 'PersonaBrief', 'SectionHeading', 'Citation', 'Source', 'SourceIndex', 'Screenshot', 'ScreenshotGallery', 'EvidenceStep', 'Mermaid', 'Infographic']);
const registeredComponents = new Set(capabilities.contentTools.map((tool) => tool.component).filter(Boolean));
if (capabilities.schemaVersion !== 2
  || capabilities.visualFoundation?.shell !== 'fumadocs-notebook'
  || capabilities.visualFoundation?.visualGrammar !== 'nextra-content-first'
  || capabilities.visualFoundation?.primitiveLibrary !== '@radix-ui/themes'
  || capabilities.visualFoundation?.version !== '3.3.0') {
  failures.push('portal-capabilities.json 的视觉基础契约不完整');
}
for (const component of expectedComponents) {
  if (!registeredComponents.has(component)) failures.push(`能力清单缺少公开组件：${component}`);
}

const walk = (directory) => existsSync(directory) ? readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
  const path = join(directory, entry.name);
  return entry.isDirectory() ? walk(path) : [path];
}) : [];
const removedNames = Object.keys(capabilities.removedComponents ?? {});
for (const file of walk('content').filter((path) => /\.mdx?$/.test(path))) {
  const source = readFileSync(file, 'utf8');
  for (const name of removedNames) {
    const offset = source.search(new RegExp(`<${name}\\b`));
    if (offset >= 0) failures.push(`${file}:${source.slice(0, offset).split('\n').length} 仍使用已删除组件 ${name}`);
  }
}
if (failures.length) {
  console.error(`发布源文件门禁失败（${failures.length} 项）\n${failures.map((item) => `- ${item}`).join('\n')}`);
  process.exit(1);
}

const externalUrl = process.env.PORTAL_URL || process.argv[2];
const baseUrl = (externalUrl || 'http://127.0.0.1:4173').replace(/\/$/, '');
const server = externalUrl ? undefined : spawn('pnpm', ['exec', 'serve', 'out', '-l', '4173', '--no-clipboard'], { stdio: 'ignore' });
if (server) {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try { if ((await fetch(baseUrl)).ok) break; } catch {}
    await new Promise((resolve) => setTimeout(resolve, 250));
    if (attempt === 59) throw new Error('无法启动视觉发布检查服务器');
  }
}

const routes = new Set(['/', '/component-gallery', '/portal-release-check']);
for (const file of walk('out/docs').filter((path) => path.endsWith('.html'))) {
  const route = `/${relative('out', file).split(sep).join('/').replace(/(?:\/index)?\.html$/, '')}`;
  routes.add(route);
}
const allViewports = [
  { name: 'wide', width: 1920, height: 1080 },
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 390, height: 844 },
  { name: 'compact', width: 320, height: 720 },
];
const viewports = process.env.PORTAL_GATE_QUICK === '1' ? [allViewports[1]] : allViewports;
const selectedRoutes = process.env.PORTAL_GATE_QUICK === '1'
  ? ['/docs/portal-release-check-mdx', '/component-gallery', '/']
  : routes;
const executableCandidates = [
  process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
].filter(Boolean);
const browser = await chromium.launch({ headless: true, executablePath: executableCandidates.find(existsSync) });

try {
  for (const viewport of viewports) {
    for (const theme of ['light', 'dark']) {
      const context = await browser.newContext({ viewport, colorScheme: theme });
      const page = await context.newPage();
      page.on('pageerror', (error) => failures.push(`${viewport.name}/${theme}: 页面异常：${error.message}`));
      for (const route of selectedRoutes) {
        const prefix = `${viewport.name}/${theme}${route}`;
        const response = await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle' });
        if (!response?.ok()) {
          failures.push(`${prefix}: HTTP ${response?.status() ?? '无响应'}`);
          continue;
        }
        await page.evaluate((selectedTheme) => {
          document.documentElement.classList.toggle('dark', selectedTheme === 'dark');
          document.documentElement.style.colorScheme = selectedTheme;
          window.dispatchEvent(new Event('resize'));
        }, theme);
        await page.waitForTimeout(350);
        await page.waitForFunction(() => [...document.querySelectorAll('.antv-infographic-canvas')].every((node) => ['true', 'error'].includes(node.getAttribute('data-rendered') ?? '')), null, { timeout: 15_000 }).catch(() => {});
        await page.evaluate(async () => {
          for (const image of document.images) {
            image.scrollIntoView({ block: 'center' });
            if (!image.complete) await new Promise((resolve) => { image.addEventListener('load', resolve, { once: true }); image.addEventListener('error', resolve, { once: true }); setTimeout(resolve, 5000); });
          }
          scrollTo(0, 0);
        });
        const audit = await page.evaluate(() => {
          const errors = [];
          const notices = [];
          const visible = (element) => Boolean(element && element.getClientRects().length && getComputedStyle(element).visibility !== 'hidden');
          if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) errors.push(`页面横向溢出 ${document.documentElement.scrollWidth - document.documentElement.clientWidth}px`);
          for (const image of document.images) {
            if (visible(image) && (!image.complete || image.naturalWidth < 1 || image.naturalHeight < 1)) errors.push(`图片加载失败：${image.currentSrc || image.src}`);
          }
          for (const link of document.querySelectorAll('a[href^="#"]')) {
            const id = decodeURIComponent(link.getAttribute('href').slice(1));
            if (id && !document.getElementById(id)) errors.push(`无效内部引用：#${id}`);
          }
          for (const container of document.querySelectorAll('.antv-infographic-canvas, .mermaid')) {
            const surface = container.querySelector('svg, canvas');
            const bounds = surface?.getBoundingClientRect();
            const hasGraphics = surface instanceof HTMLCanvasElement
              ? surface.width > 0 && surface.height > 0
              : Boolean(surface?.querySelector('path, rect, circle, ellipse, line, polyline, polygon, text, image, use, foreignObject'));
            if (!surface || !bounds || bounds.width <= 1 || bounds.height <= 1 || !hasGraphics) errors.push(`${container.classList.contains('mermaid') ? 'Mermaid' : 'Infographic'} 为空或尺寸无效`);
            const frame = container.closest('.gf-figure-stage');
            if (frame && (container.scrollWidth > frame.clientWidth + 2 || container.scrollHeight > frame.clientHeight + 2)) errors.push('图形组件被容器裁切');
          }
          for (const list of document.querySelectorAll('.gf-field-list')) {
            const columns = getComputedStyle(list).gridTemplateColumns.split(' ').filter(Boolean).length;
            if (columns > 4) errors.push(`FieldList 超过四列：${columns}`);
            if (innerWidth <= 640 && columns !== 1) errors.push(`FieldList 移动端未切换为单列：${columns}`);
            for (const item of list.querySelectorAll('.gf-field-span-full')) {
              if (getComputedStyle(item).gridColumnEnd !== '-1') errors.push('FieldList 长字段未占满整行');
            }
            for (const item of list.querySelectorAll('.gf-field-item')) {
              const label = item.querySelector('.gf-field-label')?.getBoundingClientRect();
              const value = item.querySelector('.gf-field-value')?.getBoundingClientRect();
              if (label && value && getComputedStyle(item).gridTemplateColumns.split(' ').length === 1 && Math.abs(label.left - value.left) > 1) {
                errors.push('FieldList 标签和值未共用左边界');
              }
            }
          }
          for (const callout of document.querySelectorAll('.gf-callout')) {
            const icon = callout.querySelector('.rt-CalloutIcon')?.getBoundingClientRect();
            const titleElement = callout.querySelector('.gf-callout-title');
            const title = titleElement?.getBoundingClientRect();
            if (icon && title && titleElement) {
              const iconCenter = icon.top + icon.height / 2;
              const titleLineCenter = title.top + Number.parseFloat(getComputedStyle(titleElement).lineHeight) / 2;
              if (Math.abs(iconCenter - titleLineCenter) > 3) errors.push('Callout 图标未与标题首行对齐');
            }
          }
          for (const figure of document.querySelectorAll('.gf-figure')) {
            const bounds = figure.getBoundingClientRect();
            if (bounds.right > innerWidth + 2) errors.push('FigureFrame 超出视口或被裁切');
          }
          for (const screenshot of document.querySelectorAll('.gf-screenshot')) {
            const image = screenshot.querySelector('img');
            const bounds = image?.getBoundingClientRect();
            if (!image || !bounds || bounds.width <= 1 || bounds.height <= 1) errors.push('Screenshot 图片为空或尺寸无效');
            if (!screenshot.querySelector('.gf-screenshot-trigger')) errors.push('Screenshot 缺少灯箱入口');
            const metadata = screenshot.querySelector('[data-missing-caption]');
            if (metadata?.dataset.missingCaption === 'true') notices.push('Screenshot 缺少图注');
            if (image && image.naturalHeight / image.naturalWidth > 2 && bounds && bounds.width > 380) errors.push('竖向长图以全宽展示');
            const trigger = screenshot.querySelector('.gf-screenshot-trigger');
            const triggerBounds = trigger?.getBoundingClientRect();
            const triggerOverflow = trigger ? getComputedStyle(trigger).overflowY : '';
            const usesBoundedScroll = Boolean(trigger && triggerBounds
              && ['auto', 'scroll'].includes(triggerOverflow)
              && trigger.scrollHeight > trigger.clientHeight + 1
              && triggerBounds.height <= innerHeight * 0.7 + 2);
            if (bounds && bounds.height > innerHeight * 0.7 + 2 && !usesBoundedScroll) errors.push('Screenshot 显示高度超过 70vh');
          }
          for (const component of document.querySelectorAll('[data-doc-component]')) {
            if (component.scrollWidth > component.clientWidth + 1) errors.push(`${component.dataset.docComponent} 组件横向溢出`);
          }
          return { errors, notices };
        });
        failures.push(...audit.errors.map((error) => `${prefix}: ${error}`));
        warnings.push(...audit.notices.map((warning) => `${prefix}: ${warning}`));

        const axe = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
        for (const violation of axe.violations.filter((item) => ['critical', 'serious'].includes(item.impact))) {
          const nodes = [];
          for (const node of violation.nodes) {
            const exempt = violation.id === 'color-contrast' && await page.evaluate(({ target, selector }) => {
              try {
                const element = document.querySelector(target);
                return Boolean(element?.matches(selector));
              } catch {
                return false;
              }
            }, { target: node.target.join(' '), selector: brandContrastExemption });
            if (!exempt) nodes.push(node);
          }
          if (nodes.length) failures.push(`${prefix}: axe ${violation.impact} ${violation.id}（${nodes.length} 处：${nodes.slice(0, 3).flatMap((node) => node.target).join(', ')}）`);
        }
        const trigger = page.locator('.gf-screenshot-trigger').first();
        if (await trigger.count()) {
          await trigger.focus();
          await page.keyboard.press('Enter');
          const dialog = page.locator('.gf-screenshot-lightbox[role="dialog"]');
          if (!(await dialog.isVisible())) failures.push(`${prefix}: Screenshot 灯箱无法通过键盘打开`);
          await page.keyboard.press('Escape');
          if (await dialog.isVisible()) failures.push(`${prefix}: Screenshot 灯箱无法通过 Esc 关闭`);
        }
      }
      await context.close();
    }
  }
} finally {
  await browser.close();
  server?.kill();
}

if (failures.length) {
  console.error(`视觉发布门禁失败（${failures.length} 项）\n${failures.map((item) => `- ${item}`).join('\n')}`);
  process.exit(1);
}
if (warnings.length) console.warn(`视觉发布警告（${warnings.length} 项）\n${warnings.map((item) => `- ${item}`).join('\n')}`);
console.log(`${selectedRoutes.length ?? selectedRoutes.size} 个页面 × ${viewports.length} 种宽度 × 明暗主题通过布局、媒体、引用、图形、键盘与 axe 门禁。`);
