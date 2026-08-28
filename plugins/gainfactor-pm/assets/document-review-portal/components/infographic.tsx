'use client';

import {
  getFonts,
  Infographic as AntVInfographic,
  loadSVGResource,
  registerResourceLoader,
  setDefaultFont,
} from '@antv/infographic';
import { useEffect, useRef, useState } from 'react';
import dynamicIconImports from 'lucide-react/dynamicIconImports';
import { FigureFrame } from './figure-frame';
import { InteractiveCanvasControls, useInteractiveCanvas } from './interactive-canvas';

type IconName = keyof typeof dynamicIconImports;

const localIcon = '<symbol viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 12h8M12 8v8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>';

function escapeAttribute(value: unknown) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('"', '&quot;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

async function loadLucideIcon(name: string) {
  const loader = dynamicIconImports[name as IconName];
  if (!loader) return loadSVGResource(localIcon) as unknown as SVGSymbolElement;
  const icon = await loader();
  const body = icon.__iconNode.map(([tag, attributes]) => {
    const serialized = Object.entries(attributes)
      .filter(([key]) => key !== 'key')
      .map(([key, value]) => `${key}="${escapeAttribute(value)}"`)
      .join(' ');
    return `<${tag}${serialized ? ` ${serialized}` : ''}/>`;
  }).join('');
  return loadSVGResource(
    `<symbol viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${body}</symbol>`,
  ) as unknown as SVGSymbolElement;
}

// Disable AntV's built-in remote font stylesheets and semantic icon service.
for (const font of getFonts()) {
  font.baseUrl = '';
  font.fontWeight = {};
}
setDefaultFont('system-ui');
registerResourceLoader(async ({ data }) => loadLucideIcon(data));

export function Infographic({ syntax, caption }: { syntax: string; caption?: string }) {
  const fullscreenRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string>();
  const [rendered, setRendered] = useState(false);
  const templateFamily = syntax.match(/^infographic\s+([a-z0-9]+)-/)?.[1] ?? 'unknown';
  const fullscreen = () => fullscreenRef.current?.requestFullscreen?.();
  const panzoom = useInteractiveCanvas({ viewportRef, targetRef: containerRef, enabled: rendered, refreshKey: syntax, maxScale: 2.5 });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    let infographic: AntVInfographic | undefined;
    let cancelled = false;
    let scheduleFrame = 0;
    let renderGeneration = 0;
    const layoutFrames = new Set<number>();
    let lastSize = '';

    const fail = (reason: unknown, generation: number, instance?: AntVInfographic) => {
      if (cancelled || generation !== renderGeneration) return;
      instance?.destroy();
      if (infographic === instance) infographic = undefined;
      container.replaceChildren();
      container.dataset.rendered = 'false';
      setRendered(false);
      setError(reason instanceof Error ? reason.message : '图形未生成有效内容');
    };

    const waitForLayout = (generation: number) => new Promise<DOMRect | null>((resolve) => {
      const measure = () => {
        if (cancelled || generation !== renderGeneration) {
          resolve(null);
          return;
        }
        const bounds = container.getBoundingClientRect();
        if (bounds.width > 1 && bounds.height > 1) resolve(bounds);
        else {
          const frame = requestAnimationFrame(() => {
            layoutFrames.delete(frame);
            measure();
          });
          layoutFrames.add(frame);
        }
      };
      measure();
    });

    const render = async (generation: number) => {
      let instance: AntVInfographic | undefined;
      try {
        if (/(?:https?:\/\/|ref:(?:url|remote|search):)/i.test(syntax)) {
          throw new Error('文档门户已禁用远程 Infographic 资源');
        }
        const bounds = await waitForLayout(generation);
        if (!bounds || cancelled || generation !== renderGeneration) return;
        const styles = getComputedStyle(document.documentElement);
        const token = (name: string) => styles.getPropertyValue(name).trim();
        const themedSyntax = `${syntax.trim()}\n\ntheme\n  colorPrimary ${token('--doc-chart-1')}\n  colorBg ${token('--color-fd-background')}\n  palette ${[
          '--doc-chart-1',
          '--doc-chart-2',
          '--doc-chart-3',
          '--doc-chart-4',
          '--doc-chart-5',
          '--doc-chart-6',
        ].map(token).join(' ')}`;
        infographic?.destroy();
        container.replaceChildren();
        setError(undefined);
        setRendered(false);
        instance = new AntVInfographic({
          container,
          width: Math.floor(bounds.width),
          height: '100%',
          editable: false,
        });
        infographic = instance;
        instance.on('error', (reason) => fail(reason, generation, instance));
        await Promise.resolve(instance.render(themedSyntax));
        await new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
        if (cancelled || generation !== renderGeneration || infographic !== instance) return;
        const surface = container.querySelector<SVGSVGElement | HTMLCanvasElement>('svg, canvas');
        const surfaceBounds = surface?.getBoundingClientRect();
        const hasGraphics = surface instanceof HTMLCanvasElement
          ? surface.width > 0 && surface.height > 0
          : Boolean(surface?.querySelector('path, rect, circle, ellipse, line, polyline, polygon, text, image, use'));
        if (!surface || !surfaceBounds || surfaceBounds.width <= 1 || surfaceBounds.height <= 1 || !hasGraphics) {
          throw new Error('图形渲染为空，请检查模板语法与数据');
        }
        container.dataset.rendered = 'true';
        setRendered(true);
      } catch (reason) {
        fail(reason, generation, instance);
      }
    };

    const scheduleRender = () => {
      const generation = ++renderGeneration;
      cancelAnimationFrame(scheduleFrame);
      scheduleFrame = requestAnimationFrame(() => void render(generation));
    };
    const resizeObserver = new ResizeObserver(([entry]) => {
      const nextSize = `${Math.round(entry.contentRect.width)}`;
      if (lastSize && nextSize !== lastSize) scheduleRender();
      lastSize = nextSize;
    });
    const themeObserver = new MutationObserver(scheduleRender);
    resizeObserver.observe(container);
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme', 'style'] });
    scheduleRender();

    return () => {
      cancelled = true;
      renderGeneration += 1;
      cancelAnimationFrame(scheduleFrame);
      for (const frame of layoutFrames) cancelAnimationFrame(frame);
      layoutFrames.clear();
      resizeObserver.disconnect();
      themeObserver.disconnect();
      infographic?.destroy();
    };
  }, [syntax]);

  return (
    <div ref={fullscreenRef} className="antv-infographic-fullscreen-root">
      <FigureFrame
        className="antv-infographic"
        title="信息图"
        actions={
          <InteractiveCanvasControls label="信息图" controller={panzoom} onFullscreen={fullscreen} disabled={!rendered} />
        }
        caption={caption}
        error={error ? <><strong>图形渲染失败</strong><span>{error}</span></> : null}
      >
        <div ref={viewportRef} className="antv-infographic-viewport" role="region" aria-label="信息图画布，按 Ctrl 或 Command 配合滚轮缩放">
          <div
            ref={containerRef}
            className="antv-infographic-canvas"
            data-template-family={templateFamily}
            aria-busy={!rendered && !error}
          />
        </div>
      </FigureFrame>
    </div>
  );
}
