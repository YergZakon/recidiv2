import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  MapIcon, 
  ChartBarIcon, 
  UsersIcon, 
  MagnifyingGlassIcon,
  ClockIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import clsx from 'clsx';
import NotificationCenter from './notifications/NotificationCenter';

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<any>;
}

const navigation: NavItem[] = [
  { name: 'Главная', path: '/', icon: HomeIcon },
  { name: 'Поиск по ИИН', path: '/search', icon: MagnifyingGlassIcon },
  { name: 'Списки лиц риска', path: '/persons', icon: UsersIcon },
  { name: 'Временные прогнозы', path: '/forecasts', icon: ClockIcon },
  { name: 'Карта временных окон', path: '/timeline-map', icon: MapIcon },
  { name: 'Статус регионов', path: '/regions', icon: ChartBarIcon },
];

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-30">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-md text-gray-500 hover:text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-crime-red"
              >
                {sidebarOpen ? (
                  <XMarkIcon className="h-6 w-6" />
                ) : (
                  <Bars3Icon className="h-6 w-6" />
                )}
              </button>
              <div className="ml-4 flex items-center">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-crime-red rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-lg">СР</span>
                  </div>
                  <h1 className="ml-3 text-xl font-semibold text-gray-900">
                    Система раннего предупреждения
                  </h1>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <NotificationCenter />
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700">Администратор</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed left-0 top-16 bottom-0 bg-white border-r border-gray-200 transition-all duration-300 z-20',
          sidebarOpen ? 'w-64' : 'w-0 overflow-hidden'
        )}
      >
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={clsx(
                  'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                  active
                    ? 'bg-crime-red text-white'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <Icon className={clsx('h-5 w-5 mr-3', active ? 'text-white' : 'text-gray-400')} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Statistics Summary */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Всего нарушений:</span>
              <span className="font-semibold text-gray-900">146,570</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Рецидивистов:</span>
              <span className="font-semibold text-gray-900">12,333</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Предотвратимость:</span>
              <span className="font-semibold text-green-600">97.0%</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className={clsx(
        'pt-16 transition-all duration-300',
        sidebarOpen ? 'ml-64' : 'ml-0'
      )}>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;