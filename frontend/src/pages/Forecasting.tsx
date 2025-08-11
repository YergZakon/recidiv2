import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  ChartBarIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface CrimeWindow {
  crime_type: string;
  avg_days: number;
  preventability: number;
  cases_count: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

interface MonthlyForecast {
  month: string;
  expected_crimes: number;
  preventable_crimes: number;
  interventions_needed: number;
}

const Forecasting: React.FC = () => {
  const [timeWindow, setTimeWindow] = useState<'30' | '90' | '180' | '365'>('90');
  const [loading, setLoading] = useState(true);

  // Mock data based on system constants
  const crimeWindows: CrimeWindow[] = [
    { crime_type: 'Убийство', avg_days: 143, preventability: 97.0, cases_count: 45, risk_level: 'critical' },
    { crime_type: 'Кража', avg_days: 146, preventability: 87.3, cases_count: 1234, risk_level: 'high' },
    { crime_type: 'Мошенничество', avg_days: 109, preventability: 82.3, cases_count: 567, risk_level: 'high' },
    { crime_type: 'Грабеж', avg_days: 148, preventability: 60.2, cases_count: 234, risk_level: 'medium' },
    { crime_type: 'Разбой', avg_days: 150, preventability: 20.2, cases_count: 123, risk_level: 'critical' },
    { crime_type: 'Изнасилование', avg_days: 157, preventability: 65.6, cases_count: 89, risk_level: 'critical' },
    { crime_type: 'Вымогательство', avg_days: 144, preventability: 100.0, cases_count: 67, risk_level: 'medium' },
    { crime_type: 'Наркотики', avg_days: 23, preventability: 45.0, cases_count: 345, risk_level: 'medium' }
  ];

  const monthlyForecasts: MonthlyForecast[] = [
    { month: 'Янв 2025', expected_crimes: 45, preventable_crimes: 41, interventions_needed: 12 },
    { month: 'Фев 2025', expected_crimes: 52, preventable_crimes: 47, interventions_needed: 15 },
    { month: 'Мар 2025', expected_crimes: 38, preventable_crimes: 35, interventions_needed: 9 },
    { month: 'Апр 2025', expected_crimes: 61, preventable_crimes: 54, interventions_needed: 18 },
    { month: 'Май 2025', expected_crimes: 43, preventable_crimes: 39, interventions_needed: 11 },
    { month: 'Июн 2025', expected_crimes: 56, preventable_crimes: 51, interventions_needed: 16 }
  ];

  const riskDistribution = [
    { name: 'Критический', value: 25, count: 1856, color: '#dc2626' },
    { name: 'Высокий', value: 35, count: 3083, color: '#ea580c' },
    { name: 'Средний', value: 30, count: 4316, color: '#ca8a04' },
    { name: 'Низкий', value: 10, count: 3078, color: '#16a34a' }
  ];

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, [timeWindow]);

  const getFilteredData = () => {
    const days = parseInt(timeWindow);
    return crimeWindows.filter(crime => crime.avg_days <= days);
  };

  const getTotalStats = () => {
    const filtered = getFilteredData();
    return {
      totalCrimes: filtered.reduce((sum, crime) => sum + crime.cases_count, 0),
      avgPreventability: filtered.reduce((sum, crime) => sum + crime.preventability, 0) / filtered.length,
      criticalCrimes: filtered.filter(crime => crime.risk_level === 'critical').length
    };
  };

  const stats = getTotalStats();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Прогнозирование преступлений</h1>
          <p className="mt-1 text-sm text-gray-500">
            Временные окна и прогнозы на основе анализа 146,570 нарушений
          </p>
        </div>
        <div className="flex space-x-2">
          {(['30', '90', '180', '365'] as const).map((days) => (
            <Button
              key={days}
              size="sm"
              variant={timeWindow === days ? 'primary' : 'outline'}
              onClick={() => setTimeWindow(days)}
            >
              {days === '365' ? '1 год' : `${days} дней`}
            </Button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Всего случаев</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.totalCrimes.toLocaleString()}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ShieldCheckIcon className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Предотвратимость</p>
              <p className="text-2xl font-semibold text-green-600">
                {stats.avgPreventability.toFixed(1)}%
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Критические</p>
              <p className="text-2xl font-semibold text-red-600">
                {stats.criticalCrimes}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-orange-500" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Период</p>
              <p className="text-2xl font-semibold text-gray-900">
                {timeWindow === '365' ? '1 год' : `${timeWindow}д`}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {loading ? (
        <Loading text="Загрузка прогнозов..." />
      ) : (
        <>
          {/* Crime Windows Chart */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <Card title="Временные окна преступлений">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={getFilteredData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="crime_type" 
                    angle={-45}
                    textAnchor="end"
                    height={100}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip 
                    labelStyle={{ color: '#374151' }}
                    formatter={(value: any, name: string) => {
                      if (name === 'avg_days') return [`${value} дней`, 'Среднее время'];
                      if (name === 'preventability') return [`${value}%`, 'Предотвратимость'];
                      return [value, name];
                    }}
                  />
                  <Legend />
                  <Bar dataKey="avg_days" fill="#3b82f6" name="Среднее время (дни)" />
                  <Bar dataKey="preventability" fill="#10b981" name="Предотвратимость %" />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Распределение по уровням риска">
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={riskDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="count"
                    label={({ name, value, count }) => `${name}: ${count}`}
                  >
                    {riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: any) => [value.toLocaleString(), 'Количество лиц']}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Monthly Forecast */}
          <Card title="Помесячный прогноз">
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={monthlyForecasts}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="expected_crimes" 
                  stackId="1" 
                  stroke="#ef4444" 
                  fill="#fee2e2" 
                  name="Ожидаемые преступления"
                />
                <Area 
                  type="monotone" 
                  dataKey="preventable_crimes" 
                  stackId="2" 
                  stroke="#22c55e" 
                  fill="#dcfce7" 
                  name="Предотвратимые"
                />
                <Area 
                  type="monotone" 
                  dataKey="interventions_needed" 
                  stackId="3" 
                  stroke="#f59e0b" 
                  fill="#fef3c7" 
                  name="Требуют вмешательства"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          {/* Crime Types Detailed Table */}
          <Card title="Детальная статистика по типам преступлений">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Тип преступления
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Среднее время
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Предотвратимость
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Случаев в анализе
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Уровень риска
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {getFilteredData().map((crime, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900">
                            {crime.crime_type}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <CalendarIcon className="h-4 w-4 text-gray-400" />
                          <span className="text-sm text-gray-900">{crime.avg_days} дней</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className="bg-green-500 h-2 rounded-full"
                              style={{ width: `${crime.preventability}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-gray-900">
                            {crime.preventability}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {crime.cases_count.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge riskLevel={crime.risk_level}>
                          {crime.risk_level === 'critical' && 'Критический'}
                          {crime.risk_level === 'high' && 'Высокий'}
                          {crime.risk_level === 'medium' && 'Средний'}
                          {crime.risk_level === 'low' && 'Низкий'}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  );
};

export default Forecasting;