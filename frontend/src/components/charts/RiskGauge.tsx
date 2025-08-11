import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import clsx from 'clsx';

interface RiskGaugeProps {
  value: number; // 0-10
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const RiskGauge: React.FC<RiskGaugeProps> = ({
  value,
  size = 'md',
  showLabel = true,
  className
}) => {
  // Нормализуем значение от 0 до 100 для визуализации
  const normalizedValue = Math.min(Math.max(value, 0), 10) * 10;
  
  // Определяем цвет и уровень риска
  const getRiskInfo = () => {
    if (value >= 7) return { color: '#dc2626', level: 'Критический', textColor: 'text-red-600' };
    if (value >= 5) return { color: '#f59e0b', level: 'Высокий', textColor: 'text-amber-600' };
    if (value >= 3) return { color: '#f97316', level: 'Средний', textColor: 'text-orange-600' };
    return { color: '#059669', level: 'Низкий', textColor: 'text-green-600' };
  };

  const { color, level, textColor } = getRiskInfo();

  const data = [
    { value: normalizedValue },
    { value: 100 - normalizedValue }
  ];

  const sizes = {
    sm: { width: 120, height: 120, innerRadius: 35, outerRadius: 45 },
    md: { width: 180, height: 180, innerRadius: 55, outerRadius: 70 },
    lg: { width: 240, height: 240, innerRadius: 75, outerRadius: 95 }
  };

  const currentSize = sizes[size];

  return (
    <div className={clsx('flex flex-col items-center', className)}>
      <div className="relative">
        <ResponsiveContainer width={currentSize.width} height={currentSize.height}>
          <PieChart>
            <Pie
              data={data}
              cx={currentSize.width / 2}
              cy={currentSize.height / 2}
              startAngle={180}
              endAngle={0}
              innerRadius={currentSize.innerRadius}
              outerRadius={currentSize.outerRadius}
              dataKey="value"
            >
              <Cell fill={color} />
              <Cell fill="#e5e7eb" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={clsx(
            'font-bold',
            size === 'sm' && 'text-2xl',
            size === 'md' && 'text-3xl',
            size === 'lg' && 'text-4xl',
            textColor
          )}>
            {value.toFixed(1)}
          </span>
          {showLabel && (
            <span className={clsx(
              'text-gray-500',
              size === 'sm' && 'text-xs',
              size === 'md' && 'text-sm',
              size === 'lg' && 'text-base'
            )}>
              из 10
            </span>
          )}
        </div>
      </div>
      {showLabel && (
        <div className="mt-2 text-center">
          <p className={clsx(
            'font-semibold',
            textColor,
            size === 'sm' && 'text-sm',
            size === 'md' && 'text-base',
            size === 'lg' && 'text-lg'
          )}>
            {level}
          </p>
          <p className={clsx(
            'text-gray-500',
            size === 'sm' && 'text-xs',
            size === 'md' && 'text-sm',
            size === 'lg' && 'text-base'
          )}>
            Уровень риска
          </p>
        </div>
      )}
    </div>
  );
};

export default RiskGauge;