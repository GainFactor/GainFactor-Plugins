'use client';

import Panzoom, { type PanzoomObject } from '@panzoom/panzoom';
import { Expand, Minus, Plus, RotateCcw } from 'lucide-react';
import { useLayoutEffect, useRef, useState, type RefObject } from 'react';

type InteractiveCanvasOptions = {
  viewportRef: RefObject<HTMLElement | null>;
  targetRef: RefObject<HTMLElement | SVGElement | null>;
  enabled?: boolean;
  refreshKey?: unknown;
  minScale?: number;
  maxScale?: number;
};

export function useInteractiveCanvas({
  viewportRef,
  targetRef,
  enabled = true,
  refreshKey,
  minScale = 0.5,
  maxScale = 4,
}: InteractiveCanvasOptions) {
  const instanceRef = useRef<PanzoomObject>(null);
  const [scale, setScale] = useState(1);

  useLayoutEffect(() => {
    const viewport = viewportRef.current;
    const target = targetRef.current;
    if (!enabled || !viewport || !target) return;

    const instance = Panzoom(target, {
      canvas: true,
      minScale,
      maxScale,
      step: 0.25,
      panOnlyWhenZoomed: true,
      pinchAndPan: true,
      overflow: 'hidden',
    });
    instanceRef.current = instance;
    target.dataset.scale = '1';

    const handleChange = (event: Event) => {
      const nextScale = (event as CustomEvent<{ scale: number }>).detail.scale;
      setScale(nextScale);
      target.dataset.scale = String(Number(nextScale.toFixed(2)));
      viewport.dataset.zoomed = nextScale > 1 ? 'true' : 'false';
    };
    const handleStart = () => { viewport.dataset.dragging = 'true'; };
    const handleEnd = () => { delete viewport.dataset.dragging; };
    const handleWheel = (event: WheelEvent) => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault();
      instance.zoomWithWheel(event);
    };

    target.addEventListener('panzoomchange', handleChange);
    target.addEventListener('panzoomstart', handleStart);
    target.addEventListener('panzoomend', handleEnd);
    viewport.addEventListener('wheel', handleWheel, { passive: false });

    return () => {
      viewport.removeEventListener('wheel', handleWheel);
      target.removeEventListener('panzoomchange', handleChange);
      target.removeEventListener('panzoomstart', handleStart);
      target.removeEventListener('panzoomend', handleEnd);
      instance.destroy();
      if (instanceRef.current === instance) instanceRef.current = null;
      delete viewport.dataset.dragging;
      delete viewport.dataset.zoomed;
    };
  }, [enabled, maxScale, minScale, refreshKey, targetRef, viewportRef]);

  return {
    scale,
    zoomIn: () => instanceRef.current?.zoomIn({ animate: true }),
    zoomOut: () => instanceRef.current?.zoomOut({ animate: true }),
    reset: () => instanceRef.current?.reset({ animate: true }),
  };
}

export function InteractiveCanvasControls({
  label,
  controller,
  onFullscreen,
  disabled = false,
}: {
  label: string;
  controller: ReturnType<typeof useInteractiveCanvas>;
  onFullscreen?: () => void;
  disabled?: boolean;
}) {
  return (
    <span className="gf-panzoom-controls">
      <button type="button" aria-label={`缩小${label}`} disabled={disabled} onClick={controller.zoomOut}><Minus aria-hidden="true" /></button>
      <button type="button" aria-label={`放大${label}`} disabled={disabled} onClick={controller.zoomIn}><Plus aria-hidden="true" /></button>
      <output aria-live="polite">{Math.round(controller.scale * 100)}%</output>
      <button type="button" aria-label={`重置${label}缩放`} disabled={disabled} onClick={controller.reset}><RotateCcw aria-hidden="true" /></button>
      {onFullscreen ? <button type="button" aria-label={`全屏查看${label}`} onClick={onFullscreen}><Expand aria-hidden="true" /></button> : null}
    </span>
  );
}
