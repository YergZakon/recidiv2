import React, { memo, useMemo } from 'react';
import { ResponsiveContainer, BarChart, LineChart, PieChart, AreaChart } from 'recharts';
import { usePerformanceMonitor } from '../../hooks/useMemoryOptimization';

interface MemoizedChartProps {
  type: 'bar' | 'line' | 'pie' | 'area';
  data: any[];
  height?: number;
  width?: string;
  children: React.ReactNode;
  dependencies?: any[]; // Additional dependencies for memo optimization
}

/**
 * Memoized chart wrapper to prevent unnecessary re-renders
 * Only re-renders when data or dependencies change
 */
const MemoizedChart: React.FC<MemoizedChartProps> = memo(({
  type,
  data,
  height = 400,
  width = "100%",
  children,
  dependencies = []
}) => {
  usePerformanceMonitor(`MemoizedChart-${type}`);

  const ChartComponent = useMemo(() => {
    switch (type) {
      case 'bar':
        return BarChart;
      case 'line':
        return LineChart;
      case 'pie':
        return PieChart;
      case 'area':
        return AreaChart;
      default:
        return BarChart;
    }
  }, [type]);

  // Memoize chart configuration
  const chartConfig = useMemo(() => ({
    data,
    margin: { top: 20, right: 20, bottom: 60, left: 60 }
  }), [data]);

  return (
    <ResponsiveContainer width={width} height={height}>
      <ChartComponent {...chartConfig}>
        {children}
      </ChartComponent>
    </ResponsiveContainer>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function for better memoization
  const dataEqual = JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data);
  const typeEqual = prevProps.type === nextProps.type;
  const heightEqual = prevProps.height === nextProps.height;
  const widthEqual = prevProps.width === nextProps.width;
  const dependenciesEqual = JSON.stringify(prevProps.dependencies) === JSON.stringify(nextProps.dependencies);

  return dataEqual && typeEqual && heightEqual && widthEqual && dependenciesEqual;
});

MemoizedChart.displayName = 'MemoizedChart';

export default MemoizedChart;