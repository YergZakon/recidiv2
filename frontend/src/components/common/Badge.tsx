import React from 'react';
import clsx from 'clsx';
import { RiskLevel } from '../../types/api.types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  riskLevel?: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  riskLevel,
  size = 'md',
  className
}) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-amber-100 text-amber-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800'
  };

  const riskLevelColors = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-amber-100 text-amber-800',
    medium: 'bg-orange-100 text-orange-800',
    low: 'bg-green-100 text-green-800'
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-sm',
    lg: 'px-3 py-1 text-base'
  };

  const colorClass = riskLevel ? riskLevelColors[riskLevel] : variants[variant];

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full',
        colorClass,
        sizes[size],
        className
      )}
    >
      {riskLevel && (
        <span 
          className={clsx(
            'w-2 h-2 rounded-full mr-1.5',
            riskLevel === 'critical' && 'bg-red-500',
            riskLevel === 'high' && 'bg-amber-500',
            riskLevel === 'medium' && 'bg-orange-500',
            riskLevel === 'low' && 'bg-green-500'
          )}
        />
      )}
      {children}
    </span>
  );
};

export default Badge;