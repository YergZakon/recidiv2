import { useEffect, useRef, useCallback } from 'react';

/**
 * Hook for optimizing component memory usage
 * Provides cleanup utilities and memory leak prevention
 */
export function useMemoryOptimization() {
  const timeoutsRef = useRef<NodeJS.Timeout[]>([]);
  const intervalsRef = useRef<NodeJS.Timeout[]>([]);
  const abortControllersRef = useRef<AbortController[]>([]);
  const observersRef = useRef<(IntersectionObserver | MutationObserver | ResizeObserver)[]>([]);

  // Create managed timeout
  const createTimeout = useCallback((callback: () => void, delay: number): NodeJS.Timeout => {
    const timeoutId = setTimeout(callback, delay);
    timeoutsRef.current.push(timeoutId);
    return timeoutId;
  }, []);

  // Create managed interval
  const createInterval = useCallback((callback: () => void, delay: number): NodeJS.Timeout => {
    const intervalId = setInterval(callback, delay);
    intervalsRef.current.push(intervalId);
    return intervalId;
  }, []);

  // Create managed AbortController
  const createAbortController = useCallback((): AbortController => {
    const controller = new AbortController();
    abortControllersRef.current.push(controller);
    return controller;
  }, []);

  // Create managed observer
  const createIntersectionObserver = useCallback((
    callback: IntersectionObserverCallback, 
    options?: IntersectionObserverInit
  ): IntersectionObserver => {
    const observer = new IntersectionObserver(callback, options);
    observersRef.current.push(observer);
    return observer;
  }, []);

  // Cleanup specific timeout
  const clearManagedTimeout = useCallback((timeoutId: NodeJS.Timeout) => {
    clearTimeout(timeoutId);
    timeoutsRef.current = timeoutsRef.current.filter(id => id !== timeoutId);
  }, []);

  // Cleanup specific interval
  const clearManagedInterval = useCallback((intervalId: NodeJS.Timeout) => {
    clearInterval(intervalId);
    intervalsRef.current = intervalsRef.current.filter(id => id !== intervalId);
  }, []);

  // Manual cleanup function
  const cleanup = useCallback(() => {
    // Clear timeouts
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];

    // Clear intervals
    intervalsRef.current.forEach(clearInterval);
    intervalsRef.current = [];

    // Abort controllers
    abortControllersRef.current.forEach(controller => controller.abort());
    abortControllersRef.current = [];

    // Disconnect observers
    observersRef.current.forEach(observer => observer.disconnect());
    observersRef.current = [];
  }, []);

  // Automatic cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    createTimeout,
    createInterval,
    createAbortController,
    createIntersectionObserver,
    clearManagedTimeout,
    clearManagedInterval,
    cleanup
  };
}

/**
 * Hook for lazy loading images with intersection observer
 */
export function useLazyLoad() {
  const { createIntersectionObserver } = useMemoryOptimization();
  const elementsRef = useRef<Set<Element>>(new Set());
  
  const observeElement = useCallback((element: Element) => {
    if (!element || elementsRef.current.has(element)) return;
    
    const observer = createIntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          observer.unobserve(img);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '50px'
    });
    
    observer.observe(element);
    elementsRef.current.add(element);
  }, [createIntersectionObserver]);

  return { observeElement };
}

/**
 * Hook for performance monitoring
 */
export function usePerformanceMonitor(componentName: string) {
  const renderStartRef = useRef<number>(Date.now());
  const mountTimeRef = useRef<number | null>(null);
  
  useEffect(() => {
    // Component mounted
    mountTimeRef.current = Date.now() - renderStartRef.current;
    console.log(`[Performance] ${componentName} mounted in ${mountTimeRef.current}ms`);
    
    return () => {
      // Component unmounting
      const lifespan = Date.now() - (mountTimeRef.current ? renderStartRef.current + mountTimeRef.current : renderStartRef.current);
      console.log(`[Performance] ${componentName} unmounted after ${lifespan}ms lifespan`);
    };
  }, [componentName]);

  // Log render time
  useEffect(() => {
    const renderTime = Date.now() - renderStartRef.current;
    if (renderTime > 100) { // Only log slow renders
      console.warn(`[Performance] ${componentName} slow render: ${renderTime}ms`);
    }
    renderStartRef.current = Date.now();
  });

  return {
    markRenderStart: () => { renderStartRef.current = Date.now(); },
    getMountTime: () => mountTimeRef.current,
  };
}