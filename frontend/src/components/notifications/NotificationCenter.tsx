import React, { useState, useEffect } from 'react';
import { 
  BellIcon, 
  ExclamationTriangleIcon,
  ShieldExclamationIcon,
  XMarkIcon,
  CheckCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { BellIcon as BellSolidIcon } from '@heroicons/react/24/solid';
import Button from '../common/Button';
import Badge from '../common/Badge';
import NotificationService from '../../services/notificationService';

export interface Notification {
  id: string;
  type: 'critical' | 'warning' | 'info' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionRequired: boolean;
  relatedPersonIIN?: string;
  region?: string;
}

interface NotificationCenterProps {
  className?: string;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({ className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<'all' | 'unread' | 'critical'>('all');

  // Connect to notification service
  useEffect(() => {
    const notificationService = NotificationService.getInstance();
    
    // Subscribe to notifications
    const unsubscribe = notificationService.subscribe((newNotifications) => {
      setNotifications(newNotifications);
    });
    
    // Start demo mode (for testing)
    notificationService.startDemo();
    
    return unsubscribe;
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;
  const criticalCount = notifications.filter(n => n.type === 'critical' && !n.read).length;

  const getFilteredNotifications = () => {
    switch (filter) {
      case 'unread':
        return notifications.filter(n => !n.read);
      case 'critical':
        return notifications.filter(n => n.type === 'critical');
      default:
        return notifications;
    }
  };

  const markAsRead = (id: string) => {
    const notificationService = NotificationService.getInstance();
    notificationService.markAsRead(id);
  };

  const markAllAsRead = () => {
    const notificationService = NotificationService.getInstance();
    notificationService.markAllAsRead();
  };

  const removeNotification = (id: string) => {
    const notificationService = NotificationService.getInstance();
    notificationService.removeNotification(id);
  };

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'critical':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ShieldExclamationIcon className="h-5 w-5 text-yellow-500" />;
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  const getTypeColor = (type: Notification['type']) => {
    switch (type) {
      case 'critical':
        return 'border-l-red-500 bg-red-50';
      case 'warning':
        return 'border-l-yellow-500 bg-yellow-50';
      case 'success':
        return 'border-l-green-500 bg-green-50';
      default:
        return 'border-l-blue-500 bg-blue-50';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now.getTime() - time.getTime();
    
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days > 0) {
      return `${days} дн. назад`;
    } else if (hours > 0) {
      return `${hours} ч. назад`;
    } else if (minutes > 0) {
      return `${minutes} мин. назад`;
    } else {
      return 'Только что';
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg"
      >
        {unreadCount > 0 ? (
          <BellSolidIcon className="h-6 w-6" />
        ) : (
          <BellIcon className="h-6 w-6" />
        )}
        
        {/* Notification Badge */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full min-w-[1.25rem] h-5">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        
        {/* Critical indicator */}
        {criticalCount > 0 && (
          <span className="absolute -top-2 -right-2 inline-block w-3 h-3 bg-red-500 rounded-full animate-pulse" />
        )}
      </button>

      {/* Notification Panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40 bg-black bg-opacity-25"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Panel */}
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border z-50 max-h-96 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-medium">Уведомления</h3>
                {unreadCount > 0 && (
                  <Badge variant="info" size="sm">
                    {unreadCount} новых
                  </Badge>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Прочитать все
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Filters */}
            <div className="flex p-2 border-b space-x-1">
              {['all', 'unread', 'critical'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f as typeof filter)}
                  className={`px-3 py-1 rounded text-sm ${
                    filter === f
                      ? 'bg-blue-100 text-blue-800'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {f === 'all' && 'Все'}
                  {f === 'unread' && 'Новые'}
                  {f === 'critical' && 'Критические'}
                </button>
              ))}
            </div>

            {/* Notifications List */}
            <div className="max-h-80 overflow-y-auto">
              {getFilteredNotifications().length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <BellIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Нет уведомлений</p>
                </div>
              ) : (
                getFilteredNotifications().map((notification) => (
                  <div
                    key={notification.id}
                    className={`border-l-4 p-4 border-b last:border-b-0 ${getTypeColor(notification.type)} ${
                      !notification.read ? 'font-medium' : ''
                    }`}
                    onClick={() => !notification.read && markAsRead(notification.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        {getIcon(notification.type)}
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-gray-900 truncate">
                            {notification.title}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {notification.message}
                          </p>
                          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                            <span>{formatTimestamp(notification.timestamp)}</span>
                            {notification.region && (
                              <span>📍 {notification.region}</span>
                            )}
                          </div>
                          {notification.relatedPersonIIN && (
                            <div className="mt-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  // Navigate to person details
                                  window.location.href = `/search?iin=${notification.relatedPersonIIN}`;
                                }}
                              >
                                Перейти к лицу
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-2">
                        {!notification.read && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full" />
                        )}
                        {notification.actionRequired && (
                          <Badge variant="warning" size="sm">
                            Действие
                          </Badge>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            removeNotification(notification.id);
                          }}
                          className="p-1 hover:bg-gray-200 rounded text-gray-400 hover:text-gray-600"
                        >
                          <XMarkIcon className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationCenter;