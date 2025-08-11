import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { useMemoryOptimization } from '../../hooks/useMemoryOptimization';

interface VirtualizedListProps<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  overscan?: number; // Number of items to render outside visible area
  renderItem: (item: T, index: number) => React.ReactNode;
  className?: string;
  onScroll?: (scrollTop: number) => void;
}

/**
 * Virtualized list component for rendering large datasets efficiently
 * Only renders visible items + overscan to improve performance
 */
function VirtualizedList<T>({
  items,
  itemHeight,
  containerHeight,
  overscan = 5,
  renderItem,
  className = '',
  onScroll
}: VirtualizedListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef<HTMLDivElement>(null);
  const { createTimeout, clearManagedTimeout } = useMemoryOptimization();
  
  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight),
      items.length - 1
    );
    
    return {
      startIndex: Math.max(0, startIndex - overscan),
      endIndex: Math.min(items.length - 1, endIndex + overscan),
      visibleStartIndex: startIndex,
      visibleEndIndex: endIndex
    };
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan]);

  // Get visible items
  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.startIndex, visibleRange.endIndex + 1);
  }, [items, visibleRange.startIndex, visibleRange.endIndex]);

  // Handle scroll with debouncing
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const newScrollTop = e.currentTarget.scrollTop;
    setScrollTop(newScrollTop);
    onScroll?.(newScrollTop);
  }, [onScroll]);

  // Scroll to specific item
  const scrollToItem = useCallback((index: number, alignment: 'start' | 'center' | 'end' = 'start') => {
    if (!scrollElementRef.current) return;

    let scrollTop: number;
    
    switch (alignment) {
      case 'start':
        scrollTop = index * itemHeight;
        break;
      case 'center':
        scrollTop = index * itemHeight - containerHeight / 2 + itemHeight / 2;
        break;
      case 'end':
        scrollTop = index * itemHeight - containerHeight + itemHeight;
        break;
      default:
        scrollTop = index * itemHeight;
    }

    scrollElementRef.current.scrollTop = Math.max(0, scrollTop);
  }, [itemHeight, containerHeight]);

  const totalHeight = items.length * itemHeight;
  const offsetY = visibleRange.startIndex * itemHeight;

  return (
    <div
      ref={scrollElementRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map((item, index) => (
            <div
              key={visibleRange.startIndex + index}
              style={{ height: itemHeight }}
            >
              {renderItem(item, visibleRange.startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default VirtualizedList;