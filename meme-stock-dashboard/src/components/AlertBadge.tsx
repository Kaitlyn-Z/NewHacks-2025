import React from 'react';
import { AlertBadgeProps } from '@/types';

const AlertBadge: React.FC<AlertBadgeProps> = ({ priority }) => {
  const getBadgeStyles = () => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getIcon = () => {
    switch (priority) {
      case 'high':
        return '🔥';
      case 'medium':
        return '⚡';
      case 'low':
        return '📈';
      default:
        return '📊';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeStyles()}`}>
      <span className="mr-1">{getIcon()}</span>
      {priority.toUpperCase()}
    </span>
  );
};

export default AlertBadge;
