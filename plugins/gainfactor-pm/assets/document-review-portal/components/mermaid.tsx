'use client';

import { Expand, Minus, Plus, RotateCcw } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useId, useRef, useState, type PointerEvent } from 'react';
import { FigureFrame } from './figure-frame';

const controls = [
  { icon: Minus, label: '缩小', delta: -0.1 },
  { icon: Plus, label: '放大', delta: 0.1 },
] as const;

const clampWheelDelta = (value: number) => Math.max(-60, Math.min(60, value * 0.35));
let renderQueue: Promise<void> = Promise.resolve();
let elkRegistered = false;

const cleanupMermaidArtifacts = (...renderIds: string[]) => {
  for (const renderId of renderIds) {
    document.getElementById(`d${renderId}`)?.remove();
    const renderedNode = document.getElementById(renderId);
    if (renderedNode?.parentElement === document.body) renderedNode.remove();
  }
};

export function Mermaid({ chart }: { chart: string }) {
  const id = useId().replace(/:/g, '');
  const { resolvedTheme } = useTheme();
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef({ active: false, x: 0, y: 0, offsetX: 0, offsetY: 0 });
  const [svg, setSvg] = useState('');
  const [error, setError] = useState(false);
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const changeScale = (delta: number) => setScale((value) => Math.min(2.5, Math.max(0.2, value + delta)));

  useEffect(() => {
    let cancelled = false;
    const elkRenderId = `mermaid-${id}-elk`;
    const dagreRenderId = `mermaid-${id}-dagre`;

    const renderChart = async () => {
      try {
        const [{ default: mermaid }, { default: elkLayouts }] = await Promise.all([
          import('mermaid'),
          import('@mermaid-js/layout-elk'),
        ]);
        if (!elkRegistered) {
          mermaid.registerLayoutLoaders(elkLayouts);
          elkRegistered = true;
        }

        const themeStyles = getComputedStyle(document.documentElement);
        const themeToken = (name: string) => themeStyles.getPropertyValue(name).trim();

        const initialize = (layout: 'elk' | 'dagre') => mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'strict',
          layout,
          ...(layout === 'elk' ? {
            elk: {
              mergeEdges: false,
              nodePlacementStrategy: 'LINEAR_SEGMENTS',
            },
          } : {}),
          theme: 'base',
          themeVariables: {
            darkMode: resolvedTheme === 'dark',
            background: themeToken('--color-fd-background'),
            primaryColor: themeToken('--doc-diagram-primary'),
            primaryTextColor: themeToken('--doc-diagram-primary-text'),
            primaryBorderColor: themeToken('--doc-diagram-primary-border'),
            lineColor: themeToken('--doc-diagram-line'),
            secondaryColor: themeToken('--doc-diagram-secondary'),
            tertiaryColor: themeToken('--doc-diagram-tertiary'),
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif',
            fontSize: '14px',
          },
          themeCSS: `
            .node rect, .node polygon, .node path { stroke-width: 1.25px; }
            .node rect { rx: 6px; ry: 6px; }
            .flowchart-link, .edgePath path { stroke-width: 1.25px; }
            .edgeLabel { border-radius: 4px; }
          `,
          flowchart: { htmlLabels: true, curve: 'linear', nodeSpacing: 36, rankSpacing: 48 },
        });

        let result;
        const prefersElk = chart.trimStart().startsWith('erDiagram');
        if (prefersElk) {
          try {
            cleanupMermaidArtifacts(elkRenderId);
            initialize('elk');
            result = await mermaid.render(elkRenderId, chart);
          } catch {
            cleanupMermaidArtifacts(elkRenderId, dagreRenderId);
            initialize('dagre');
            result = await mermaid.render(dagreRenderId, chart);
          }
        } else {
          cleanupMermaidArtifacts(dagreRenderId);
          initialize('dagre');
          result = await mermaid.render(dagreRenderId, chart);
        }

        if (!cancelled) {
          setSvg(result.svg);
          setError(false);
        }
      } catch {
        if (!cancelled) {
          setSvg('');
          setError(true);
        }
      } finally {
        cleanupMermaidArtifacts(elkRenderId, dagreRenderId);
      }
    };

    renderQueue = renderQueue.then(renderChart, renderChart);

    return () => {
      cancelled = true;
      cleanupMermaidArtifacts(elkRenderId, dagreRenderId);
    };
  }, [chart, id, resolvedTheme]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleWheel = (event: globalThis.WheelEvent) => {
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault();
        changeScale(event.deltaY > 0 ? -0.1 : 0.1);
        return;
      }

      const horizontalDelta = event.shiftKey ? event.deltaY : event.deltaX;
      if (!event.shiftKey && Math.abs(horizontalDelta) <= Math.abs(event.deltaY)) return;

      event.preventDefault();
      setOffset((value) => ({
        x: value.x - clampWheelDelta(horizontalDelta),
        y: value.y,
      }));
    };

    canvas.addEventListener('wheel', handleWheel, { passive: false });
    return () => canvas.removeEventListener('wheel', handleWheel);
  }, []);

  const reset = () => {
    setScale(1);
    setOffset({ x: 0, y: 0 });
  };
  const fullscreen = () => containerRef.current?.requestFullscreen?.();

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || event.button !== 0) return;
    dragRef.current = { active: true, x: event.clientX, y: event.clientY, offsetX: offset.x, offsetY: offset.y };
    canvas.setPointerCapture(event.pointerId);
    canvas.dataset.dragging = 'true';
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const canvas = canvasRef.current;
    const drag = dragRef.current;
    if (!canvas || !drag.active) return;
    setOffset({ x: drag.offsetX + event.clientX - drag.x, y: drag.offsetY + event.clientY - drag.y });
  };

  const stopDragging = (event: PointerEvent<HTMLDivElement>) => {
    const canvas = canvasRef.current;
    dragRef.current.active = false;
    if (canvas?.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    if (canvas) delete canvas.dataset.dragging;
  };

  return (
    <div ref={containerRef} className="mermaid-fullscreen-root">
    <FigureFrame className="mermaid-frame" title="流程图" actions={
        <span className="mermaid-controls">
          {controls.map(({ icon: Icon, label, delta }) => (
            <button key={label} type="button" aria-label={label} onClick={() => changeScale(delta)}>
              <Icon aria-hidden="true" />
            </button>
          ))}
          <output className="mermaid-scale" aria-live="polite">{Math.round(scale * 100)}%</output>
          <button type="button" aria-label="重置缩放" onClick={reset}>
            <RotateCcw aria-hidden="true" />
          </button>
          <button type="button" aria-label="全屏查看" onClick={fullscreen}>
            <Expand aria-hidden="true" />
          </button>
        </span>}>
      <div
        className="mermaid-canvas"
        ref={canvasRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={stopDragging}
        onPointerCancel={stopDragging}
      >
        {error ? (
          <p role="alert">流程图暂时无法渲染，请检查图表语法。</p>
        ) : svg ? (
          <div
            className="mermaid-svg"
            style={{ transform: `translate3d(${offset.x}px, ${offset.y}px, 0) scale(${scale})` }}
            dangerouslySetInnerHTML={{ __html: svg }}
          />
        ) : (
          <p>正在渲染流程图…</p>
        )}
      </div>
    </FigureFrame>
    </div>
  );
}
