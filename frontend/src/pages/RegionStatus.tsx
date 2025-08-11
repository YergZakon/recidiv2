import React, { useState, useEffect } from 'react';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ComposedChart,
  Area,
  AreaChart
} from 'recharts';
import {
  MapPinIcon,
  ExclamationTriangleIcon,
  UserGroupIcon,
  ChartBarIcon,
  ShieldExclamationIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline';

interface RegionData {
  id: string;
  name: string;
  total_persons: number;
  high_risk_count: number;
  critical_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  average_risk_score: number;
  status: 'safe' | 'caution' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
  recent_incidents: number;
  prevention_rate: number;
  population: number;
  crime_density: number;
}

interface RegionTrend {
  month: string;
  total_crimes: number;
  prevented: number;
  high_risk: number;
  critical_risk: number;
}

const RegionStatus: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'risk' | 'population' | 'incidents'>('risk');
  const [loading, setLoading] = useState(true);

  // Mock regional data based on Kazakhstan regions
  const regionData: RegionData[] = [
    {
      id: 'almaty_city',
      name: 'г. Алматы',
      total_persons: 3456,
      high_risk_count: 892,
      critical_risk_count: 234,
      medium_risk_count: 1567,
      low_risk_count: 763,
      average_risk_score: 6.2,
      status: 'critical',
      trend: 'up',
      recent_incidents: 45,
      prevention_rate: 78.5,
      population: 2000000,
      crime_density: 1.73
    },
    {
      id: 'astana',
      name: 'г. Астана',
      total_persons: 2834,
      high_risk_count: 567,
      critical_risk_count: 145,
      medium_risk_count: 1345,
      low_risk_count: 777,
      average_risk_score: 5.8,
      status: 'warning',
      trend: 'stable',
      recent_incidents: 32,
      prevention_rate: 82.3,
      population: 1350000,
      crime_density: 2.10
    },
    {
      id: 'almaty_region',
      name: 'Алматинская область',
      total_persons: 1956,
      high_risk_count: 345,
      critical_risk_count: 78,
      medium_risk_count: 892,
      low_risk_count: 641,
      average_risk_score: 4.9,
      status: 'caution',
      trend: 'down',
      recent_incidents: 23,
      prevention_rate: 85.7,
      population: 2036000,
      crime_density: 0.96
    },
    {
      id: 'shymkent',
      name: 'г. Шымкент',
      total_persons: 1678,
      high_risk_count: 289,
      critical_risk_count: 67,
      medium_risk_count: 756,
      low_risk_count: 566,
      average_risk_score: 5.1,
      status: 'caution',
      trend: 'stable',
      recent_incidents: 19,
      prevention_rate: 79.2,
      population: 1002000,
      crime_density: 1.67
    },
    {
      id: 'karaganda',
      name: 'Карагандинская область',
      total_persons: 1234,
      high_risk_count: 198,
      critical_risk_count: 45,
      medium_risk_count: 567,
      low_risk_count: 424,
      average_risk_score: 4.6,
      status: 'caution',
      trend: 'down',
      recent_incidents: 14,
      prevention_rate: 87.1,
      population: 1365000,
      crime_density: 0.90
    },
    {
      id: 'atyrau',
      name: 'Атырауская область',
      total_persons: 892,
      high_risk_count: 134,
      critical_risk_count: 28,
      medium_risk_count: 345,
      low_risk_count: 385,
      average_risk_score: 4.2,
      status: 'safe',
      trend: 'stable',
      recent_incidents: 8,
      prevention_rate: 91.3,
      population: 669000,
      crime_density: 1.33
    }
  ];

  // Mock trend data
  const regionTrends: RegionTrend[] = [
    { month: 'Авг 24', total_crimes: 156, prevented: 134, high_risk: 89, critical_risk: 23 },
    { month: 'Сен 24', total_crimes: 142, prevented: 128, high_risk: 76, critical_risk: 19 },
    { month: 'Окт 24', total_crimes: 167, prevented: 142, high_risk: 94, critical_risk: 28 },
    { month: 'Ноя 24', total_crimes: 134, prevented: 119, high_risk: 67, critical_risk: 15 },
    { month: 'Дек 24', total_crimes: 178, prevented: 153, high_risk: 103, critical_risk: 31 },
    { month: 'Янв 25', total_crimes: 145, prevented: 128, high_risk: 82, critical_risk: 21 }
  ];

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  const getSortedRegions = () => {
    return [...regionData].sort((a, b) => {
      switch (sortBy) {
        case 'risk':
          return b.average_risk_score - a.average_risk_score;
        case 'population':
          return b.total_persons - a.total_persons;
        case 'incidents':
          return b.recent_incidents - a.recent_incidents;
        default:
          return 0;
      }
    });
  };

  const getStatusColor = (status: RegionData['status']) => {
    switch (status) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'caution': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'safe': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status: RegionData['status']) => {
    switch (status) {
      case 'critical': return 'Критический';
      case 'warning': return 'Предупреждение';
      case 'caution': return 'Осторожность';
      case 'safe': return 'Безопасно';
      default: return 'Неизвестно';
    }
  };

  const getTrendIcon = (trend: RegionData['trend']) => {
    switch (trend) {
      case 'up': return <ArrowTrendingUpIcon className="h-4 w-4 text-red-500" />;
      case 'down': return <ArrowTrendingDownIcon className="h-4 w-4 text-green-500" />;
      default: return <div className="h-4 w-4 bg-gray-400 rounded-full" />;
    }
  };

  const getTotalStats = () => {
    const totals = regionData.reduce((acc, region) => ({
      total_persons: acc.total_persons + region.total_persons,
      critical: acc.critical + region.critical_risk_count,
      high: acc.high + region.high_risk_count,
      recent_incidents: acc.recent_incidents + region.recent_incidents
    }), { total_persons: 0, critical: 0, high: 0, recent_incidents: 0 });

    return {
      ...totals,
      avg_prevention: regionData.reduce((sum, r) => sum + r.prevention_rate, 0) / regionData.length
    };
  };

  const stats = getTotalStats();
  const selectedRegionData = selectedRegion ? regionData.find(r => r.id === selectedRegion) : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Статус регионов</h1>
          <p className="mt-1 text-sm text-gray-500">
            Мониторинг криминальной обстановки по регионам Казахстана
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            size="sm"
            variant={sortBy === 'risk' ? 'primary' : 'outline'}
            onClick={() => setSortBy('risk')}
          >
            По риску
          </Button>
          <Button
            size="sm"
            variant={sortBy === 'population' ? 'primary' : 'outline'}
            onClick={() => setSortBy('population')}
          >
            По количеству
          </Button>
          <Button
            size="sm"
            variant={sortBy === 'incidents' ? 'primary' : 'outline'}
            onClick={() => setSortBy('incidents')}
          >
            По инцидентам
          </Button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <UserGroupIcon className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-500">Всего лиц</p>
              <p className="text-2xl font-semibold">{stats.total_persons.toLocaleString()}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-500">Критический риск</p>
              <p className="text-2xl font-semibold text-red-600">{stats.critical}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <ShieldExclamationIcon className="h-8 w-8 text-yellow-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-500">Высокий риск</p>
              <p className="text-2xl font-semibold text-yellow-600">{stats.high}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-500">Предотвращение</p>
              <p className="text-2xl font-semibold text-green-600">{stats.avg_prevention.toFixed(1)}%</p>
            </div>
          </div>
        </Card>
      </div>

      {loading ? (
        <Loading text="Загрузка региональной статистики..." />
      ) : (
        <>
          {/* Regional Overview */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* Region List */}
            <Card title="Статус регионов">
              <div className="space-y-4">
                {getSortedRegions().map((region) => (
                  <div
                    key={region.id}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      selectedRegion === region.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedRegion(selectedRegion === region.id ? null : region.id)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900">{region.name}</h3>
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(region.trend)}
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(region.status)}`}>
                          {getStatusText(region.status)}
                        </span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Всего лиц:</span>
                        <span className="ml-1 font-medium">{region.total_persons.toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Риск-балл:</span>
                        <span className="ml-1 font-medium">{region.average_risk_score.toFixed(1)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Критических:</span>
                        <span className="ml-1 font-medium text-red-600">{region.critical_risk_count}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Предотвращение:</span>
                        <span className="ml-1 font-medium text-green-600">{region.prevention_rate}%</span>
                      </div>
                    </div>

                    {/* Risk Distribution Bar */}
                    <div className="mt-3">
                      <div className="w-full bg-gray-200 rounded-full h-3 flex overflow-hidden">
                        <div
                          className="bg-red-500"
                          style={{ width: `${(region.critical_risk_count / region.total_persons) * 100}%` }}
                        />
                        <div
                          className="bg-yellow-500"
                          style={{ width: `${(region.high_risk_count / region.total_persons) * 100}%` }}
                        />
                        <div
                          className="bg-orange-400"
                          style={{ width: `${(region.medium_risk_count / region.total_persons) * 100}%` }}
                        />
                        <div
                          className="bg-green-500"
                          style={{ width: `${(region.low_risk_count / region.total_persons) * 100}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Критический</span>
                        <span>Высокий</span>
                        <span>Средний</span>
                        <span>Низкий</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Risk Distribution Chart */}
            <Card title="Распределение рисков по регионам">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={getSortedRegions()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="critical_risk_count" stackId="a" fill="#dc2626" name="Критический" />
                  <Bar dataKey="high_risk_count" stackId="a" fill="#ea580c" name="Высокий" />
                  <Bar dataKey="medium_risk_count" stackId="a" fill="#f59e0b" name="Средний" />
                  <Bar dataKey="low_risk_count" stackId="a" fill="#16a34a" name="Низкий" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Regional Trends */}
          <Card title="Динамика по всем регионам">
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={regionTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="total_crimes" fill="#fee2e2" stroke="#ef4444" name="Всего преступлений" />
                <Line type="monotone" dataKey="prevented" stroke="#22c55e" strokeWidth={3} name="Предотвращено" />
                <Bar dataKey="critical_risk" fill="#dc2626" name="Критический риск" />
              </ComposedChart>
            </ResponsiveContainer>
          </Card>

          {/* Selected Region Details */}
          {selectedRegionData && (
            <Card title={`Детальная информация: ${selectedRegionData.name}`}>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <MapPinIcon className="h-6 w-6 text-blue-600 mr-2" />
                    <div>
                      <p className="text-sm text-blue-600">Плотность преступности</p>
                      <p className="text-lg font-semibold">{selectedRegionData.crime_density}</p>
                      <p className="text-xs text-blue-500">на 1000 жителей</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <ShieldExclamationIcon className="h-6 w-6 text-green-600 mr-2" />
                    <div>
                      <p className="text-sm text-green-600">Эффективность</p>
                      <p className="text-lg font-semibold">{selectedRegionData.prevention_rate}%</p>
                      <p className="text-xs text-green-500">предотвращения</p>
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mr-2" />
                    <div>
                      <p className="text-sm text-yellow-600">Недавние инциденты</p>
                      <p className="text-lg font-semibold">{selectedRegionData.recent_incidents}</p>
                      <p className="text-xs text-yellow-500">за месяц</p>
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <UserGroupIcon className="h-6 w-6 text-purple-600 mr-2" />
                    <div>
                      <p className="text-sm text-purple-600">Население</p>
                      <p className="text-lg font-semibold">{(selectedRegionData.population / 1000000).toFixed(1)}М</p>
                      <p className="text-xs text-purple-500">жителей</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={() => setSelectedRegion(null)}
                >
                  Закрыть детали
                </Button>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default RegionStatus;