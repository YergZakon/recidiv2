import React from 'react';
import clsx from 'clsx';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  fullScreen?: boolean;
  text?: string;
  className?: string;
}

const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  fullScreen = false,
  text,
  className
}) => {
  const sizes = {
    sm: 'h-6 w-6',
    md: 'h-10 w-10',
    lg: 'h-16 w-16',
    xl: 'h-24 w-24'
  };

  const spinner = (
    <div className="flex flex-col items-center justify-center">
      <div className={clsx('relative', sizes[size])}>
        <div className="absolute inset-0 rounded-full border-4 border-gray-200"></div>
        <div className={clsx(
          'absolute inset-0 rounded-full border-4 border-crime-red border-t-transparent animate-spin',
          sizes[size]
        )}></div>
      </div>
      {text && (
        <p className="mt-4 text-gray-600 text-sm font-medium">{text}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
        {spinner}
      </div>
    );
  }

  return (
    <div className={clsx('flex items-center justify-center p-8', className)}>
      {spinner}
    </div>
  );
};

export default Loading;