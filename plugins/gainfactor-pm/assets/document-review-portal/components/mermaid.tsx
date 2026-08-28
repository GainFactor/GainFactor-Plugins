'use client';

import { useTheme } from 'next-themes';
import { useEffect, useId, useRef, useState } from 'react';
import { FigureFrame } from './figure-frame';
import { InteractiveCanvasControls, useInteractiveCanvas } from './interactive-canvas';
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
  const panTargetRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState('');
  const [error, setError] = useState(false);
  const panzoom = useInteractiveCanvas({ viewportRef: canvasRef, targetRef: panTargetRef, enabled: Boolean(svg), refreshKey: svg, minScale: 0.2, maxScale: 2.5 });

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

  const fullscreen = () => containerRef.current?.requestFullscreen?.();

  return (
    <div ref={containerRef} className="mermaid-fullscreen-root">
    <FigureFrame className="mermaid-frame" title="流程图" actions={
        <InteractiveCanvasControls label="流程图" controller={panzoom} onFullscreen={fullscreen} disabled={!svg} />}>
      <div
        className="mermaid-canvas"
        ref={canvasRef}
      >
        {error ? (
          <p role="alert">流程图暂时无法渲染，请检查图表语法。</p>
        ) : svg ? (
          <div
            className="mermaid-svg"
            ref={panTargetRef}
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
