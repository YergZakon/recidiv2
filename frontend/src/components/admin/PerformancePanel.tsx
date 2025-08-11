import React, { useState, useEffect } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import CacheService from '../../services/cacheService';
import ApiService from '../../services/apiService';
import {
  ChartBarIcon,
  TrashIcon,
  ClockIcon,
  CpuChipIcon,
  ServerStackIcon
} from '@heroicons/react/24/outline';

const PerformancePanel: React.FC = () => {
  const [cacheStats, setCacheStats] = useState({ size: 0, keys: [] });
  const [memoryUsage, setMemoryUsage] = useState<any>(null);
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  const updateStats = () => {
    const apiService = ApiService.getInstance();
    const stats = apiService.getCacheStats();
    setCacheStats(stats);

    // Get memory usage if available
    if ('memory' in performance) {
      setMemoryUsage((performance as any).memory);
    }
  };

  useEffect(() => {
    updateStats();
    
    // Update stats every 5 seconds
    const interval = setInterval(updateStats, 5000);
    setRefreshInterval(interval);

    return () => {
      if (interval) clearInterval(interval);
    };
  }, []);

  const handleClearCache = () => {
    const apiService = ApiService.getInstance();
    apiService.clearCache();
    updateStats();
  };

  const handlePreloadData = async () => {
    const apiService = ApiService.getInstance();
    await apiService.preloadCommonData();
    updateStats();
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900">Панель производительности</h2>
        <div className="space-x-2">
          <Button
            size="sm"
            variant="outline"
            onClick={updateStats}
          >
            <ClockIcon className="h-4 w-4 mr-1" />
            Обновить
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handlePreloadData}
          >
            <ServerStackIcon className="h-4 w-4 mr-1" />
            Предзагрузить данные
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleClearCache}
          >
            <TrashIcon className="h-4 w-4 mr-1" />
            Очистить кеш
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Cache Statistics */}
        <Card title="Кеш-статистика">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Записей в кеше:</span>
              <span className="font-semibold">{cacheStats.size}</span>
            </div>
            
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Активные ключи:</h4>
              <div className="max-h-32 overflow-y-auto text-xs text-gray-600 space-y-1">
                {cacheStats.keys.length > 0 ? (
                  cacheStats.keys.map((key, index) => (
                    <div key={index} className="bg-gray-100 px-2 py-1 rounded">
                      {key}
                    </div>
                  ))
                ) : (
                  <div className="text-gray-400 italic">Кеш пуст</div>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* Memory Usage */}
        <Card title="Использование памяти">
          <div className="space-y-4">
            {memoryUsage ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Используемая память:</span>
                  <span className="font-semibold">{formatBytes(memoryUsage.usedJSHeapSize)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Общий размер кучи:</span>
                  <span className="font-semibold">{formatBytes(memoryUsage.totalJSHeapSize)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Лимит кучи:</span>
                  <span className="font-semibold">{formatBytes(memoryUsage.jsHeapSizeLimit)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{
                      width: `${(memoryUsage.usedJSHeapSize / memoryUsage.jsHeapSizeLimit) * 100}%`
                    }}
                  />
                </div>
              </>
            ) : (
              <div className="text-gray-400 italic">
                Информация о памяти недоступна в этом браузере
              </div>
            )}
          </div>
        </Card>

        {/* Performance Tips */}
        <Card title="Рекомендации по производительности">
          <div className="space-y-3 text-sm">
            <div className="flex items-start space-x-2">
              <ChartBarIcon className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span>Кеш автоматически очищается от устаревших данных</span>
            </div>
            <div className="flex items-start space-x-2">
              <CpuChipIcon className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
              <span>Поиск использует debouncing для уменьшения нагрузки</span>
            </div>
            <div className="flex items-start space-x-2">
              <ServerStackIcon className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
              <span>Диаграммы мемоизированы для быстрого рендеринга</span>
            </div>
            
            {cacheStats.size > 50 && (
              <div className="p-2 bg-yellow-50 border border-yellow-200 rounded text-yellow-800">
                Кеш содержит много записей. Рассмотрите очистку для освобождения памяти.
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Performance Metrics Over Time */}
      <Card title="Метрики производительности">
        <div className="text-sm text-gray-600">
          <p>Метрики производительности отображаются в консоли браузера:</p>
          <ul className="mt-2 space-y-1 ml-4">
            <li>• API-вызовы с временем выполнения</li>
            <li>• Время монтирования компонентов</li>
            <li>• Предупреждения о медленном рендеринге</li>
          </ul>
          <p className="mt-3 text-xs text-gray-500">
            Откройте Developer Tools (F12) → Console для просмотра подробных логов.
          </p>
        </div>
      </Card>
    </div>
  );
};

export default PerformancePanel;