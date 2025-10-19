'use client';

import React, { useState, useRef, useCallback } from 'react';
import type { RouteResponse, UsedDoc } from '@/lib/types';

interface Props {
  data?: Partial<RouteResponse> | null;
  isVisible?: boolean;
  width?: number;
  onToggle?: (visible: boolean) => void;
  onWidthChange?: (width: number) => void;
}

export const TechPanel = ({
  data,
  isVisible = true,
  width = 320,
  onToggle,
  onWidthChange
}: Props) => {
  const [isResizing, setIsResizing] = useState(false);
  const [localWidth, setLocalWidth] = useState(width);
  const resizeRef = useRef<HTMLDivElement>(null);

  const handleToggle = useCallback(() => {
    onToggle?.(!isVisible);
  }, [isVisible, onToggle]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;

    const newWidth = window.innerWidth - e.clientX;
    if (newWidth >= 200 && newWidth <= 600) {
      setLocalWidth(newWidth);
      onWidthChange?.(newWidth);
    }
  }, [isResizing, onWidthChange]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  // Add global mouse event listeners for resizing
  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isResizing, handleMouseMove, handleMouseUp]);

  if (!isVisible) {
    return (
      <aside className="relative hidden lg:block">
        <button
          onClick={handleToggle}
          className="absolute left-0 top-4 w-6 h-12 bg-white border border-gray-300 rounded-l-md shadow-sm hover:bg-gray-50 flex items-center justify-center text-gray-600 hover:text-gray-800 z-10"
          title="Показать техническую панель"
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </aside>
    );
  }

  const currentWidth = localWidth;

  if (!data) {
    return (
      <aside
        className="relative bg-white border-l hidden lg:block overflow-hidden"
        style={{ width: `${currentWidth}px` }}
      >
        <div className="p-4 h-full flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div className="text-sm text-gray-500">Technical panel</div>
            <button
              onClick={handleToggle}
              className="p-1 text-gray-400 hover:text-gray-600 rounded"
              title="Скрыть панель"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="flex-1 text-sm text-gray-500">
            Нет данных для отображения
          </div>
        </div>
        <div
          ref={resizeRef}
          onMouseDown={handleMouseDown}
          className="absolute left-0 top-0 w-1 h-full cursor-col-resize bg-gray-200 hover:bg-blue-400 active:bg-blue-500"
        />
      </aside>
    );
  }

  const usedDocs = data.extra?.used_docs || [] as UsedDoc[];

  return (
    <aside
      className="relative bg-white border-l hidden lg:block overflow-hidden"
      style={{ width: `${currentWidth}px` }}
    >
      <div className="p-4 h-full flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Technical panel</h3>
          <button
            onClick={handleToggle}
            className="p-1 text-gray-400 hover:text-gray-600 rounded"
            title="Скрыть панель"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="text-sm text-gray-700 mb-2">
            <span className="font-medium">Intent:</span> {data.intent}
          </div>
          <div className="text-sm text-gray-700 mb-2">
            <span className="font-medium">Agent:</span> {data.agent}
          </div>
          <div className="text-sm text-gray-700 mb-4">
            <span className="font-medium">Confidence:</span> {(data.confidence ?? 0).toFixed(2)}
          </div>

          <details className="text-sm">
            <summary className="cursor-pointer font-medium">
              Used documents ({usedDocs.length})
            </summary>
            <ul className="mt-2 space-y-2">
              {usedDocs.map((d, i) => (
                <li key={i} className="text-xs text-gray-600 border rounded p-2">
                  <div className="font-medium">{d.source}</div>
                  <div>chunk: {d.chunk} • score: {d.score?.toFixed(3)}</div>
                </li>
              ))}
            </ul>
          </details>
        </div>
      </div>

      <div
        ref={resizeRef}
        onMouseDown={handleMouseDown}
        className="absolute left-0 top-0 w-1 h-full cursor-col-resize bg-gray-200 hover:bg-blue-400 active:bg-blue-500"
      />
    </aside>
  );
};