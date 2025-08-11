import React, { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchSystemStatistics } from '../store/slices/statisticsSlice';
import { fetchHighRiskPersons, fetchCriticalRiskPersons } from '../store/slices/riskSlice';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import Badge from '../components/common/Badge';
import PerformancePanel from '../components/admin/PerformancePanel';
import { 
  UsersIcon, 
  ExclamationTriangleIcon, 
  ShieldCheckIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  const { systemStats, loading: statsLoading } = useAppSelector(state => state.statistics);
  const { highRiskPersons, criticalRiskPersons } = useAppSelector(state => state.risk);
  const [showPerformancePanel, setShowPerformancePanel] = useState(false);

  useEffect(() => {
    dispatch(fetchSystemStatistics());
    dispatch(fetchHighRiskPersons(10));
    dispatch(fetchCriticalRiskPersons(5));
  }, [dispatch]);

  if (statsLoading || !systemStats) {
    return <Loading size="lg" text="Загрузка статистики..." />;
  }

  // Данные для круговой диаграммы паттернов
  const patternData = systemStats.patterns_distribution ? [
    { name: 'Смешанный нестабильный', value: systemStats.patterns_distribution.mixed_unstable, percent: 72.7, color: '#e74c3c' },
    { name: 'Хронический', value: systemStats.patterns_distribution.chronic_criminal, percent: 13.6, color: '#f39c12' },
    { name: 'Эскалирующий', value: systemStats.patterns_distribution.escalating, percent: 7.0, color: '#f97316' },
    { name: 'Деэскалирующий', value: systemStats.patterns_distribution.deescalating, percent: 5.7, color: '#3498db' },
    { name: 'Единичный', value: systemStats.patterns_distribution.single, percent: 1.0, color: '#2ecc71' }
  ] : [];

  // Данные для временных окон
  const crimeWindows = [
    { name: 'Мошенничество', days: 109, preventability: 82.3 },
    { name: 'Кража', days: 146, preventability: 87.3 },
    { name: 'Убийство', days: 143, preventability: 97.0 },
    { name: 'Вымогательство', days: 144, preventability: 100.0 },
    { name: 'Грабеж', days: 148, preventability: 60.2 },
    { name: 'Разбой', days: 150, preventability: 20.2 },
    { name: 'Изнасилование', days: 157, preventability: 65.6 }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Панель управления</h1>
        <p className="mt-1 text-sm text-gray-500">
          Система раннего предупреждения преступлений - общая статистика
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600">Всего нарушений</p>
              <p className="text-2xl font-bold text-blue-900">146,570</p>
              <p className="text-xs text-blue-600 mt-1">Проанализировано</p>
            </div>
            <ChartBarIcon className="h-10 w-10 text-blue-500" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-red-600">Рецидивистов</p>
              <p className="text-2xl font-bold text-red-900">12,333</p>
              <p className="text-xs text-red-600 mt-1">В базе данных</p>
            </div>
            <UsersIcon className="h-10 w-10 text-red-500" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600">Предотвратимость</p>
              <p className="text-2xl font-bold text-green-900">97.0%</p>
              <p className="text-xs text-green-600 mt-1">Преступлений</p>
            </div>
            <ShieldCheckIcon className="h-10 w-10 text-green-500" />
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-amber-600">Среднее окно</p>
              <p className="text-2xl font-bold text-amber-900">143 дня</p>
              <p className="text-xs text-amber-600 mt-1">До убийства</p>
            </div>
            <ClockIcon className="h-10 w-10 text-amber-500" />
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pattern Distribution */}
        <Card title="Распределение паттернов поведения" subtitle="Анализ 12,333 рецидивистов">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={patternData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.percent}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {patternData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Нестабильный паттерн:</span>
              <span className="font-semibold text-red-600">72.7% - Высокий риск</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Переходы админ → кража:</span>
              <span className="font-semibold">6,465 случаев</span>
            </div>
          </div>
        </Card>

        {/* Crime Windows */}
        <Card title="Временные окна преступлений" subtitle="Дни до совершения и предотвратимость">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={crimeWindows} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="days" fill="#3498db" name="Дни" />
              <Bar dataKey="preventability" fill="#2ecc71" name="Предотвратимость %" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* High Risk Persons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card 
          title="Лица критического риска" 
          subtitle="Требуют немедленного вмешательства"
        >
          {criticalRiskPersons.length > 0 ? (
            <div className="space-y-3">
              {criticalRiskPersons.slice(0, 5).map((person) => (
                <div key={person.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-red-200 rounded-full flex items-center justify-center">
                      <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{person.full_name}</p>
                      <p className="text-sm text-gray-500">ИИН: {person.iin}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge riskLevel="critical">
                      {person.risk_score.toFixed(1)}
                    </Badge>
                    <p className="text-xs text-gray-500 mt-1">
                      {person.violations_count} нарушений
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Нет данных</p>
          )}
          <Link 
            to="/persons?risk_level=critical" 
            className="mt-4 block text-center text-sm text-crime-red hover:underline"
          >
            Показать всех →
          </Link>
        </Card>

        <Card 
          title="Лица высокого риска" 
          subtitle="Требуют профилактической работы"
        >
          {highRiskPersons.length > 0 ? (
            <div className="space-y-3">
              {highRiskPersons.slice(0, 5).map((person) => (
                <div key={person.id} className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-amber-200 rounded-full flex items-center justify-center">
                      <ArrowTrendingUpIcon className="h-6 w-6 text-amber-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{person.full_name}</p>
                      <p className="text-sm text-gray-500">ИИН: {person.iin}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge riskLevel="high">
                      {person.risk_score.toFixed(1)}
                    </Badge>
                    <p className="text-xs text-gray-500 mt-1">
                      {person.violations_count} нарушений
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Нет данных</p>
          )}
          <Link 
            to="/persons?risk_level=high" 
            className="mt-4 block text-center text-sm text-crime-red hover:underline"
          >
            Показать всех →
          </Link>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card title="Быстрые действия">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link
            to="/search"
            className="p-4 text-center bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <MagnifyingGlassIcon className="h-8 w-8 mx-auto mb-2 text-gray-600" />
            <span className="text-sm font-medium text-gray-900">Поиск по ИИН</span>
          </Link>
          <Link
            to="/persons"
            className="p-4 text-center bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <UsersIcon className="h-8 w-8 mx-auto mb-2 text-gray-600" />
            <span className="text-sm font-medium text-gray-900">Списки лиц</span>
          </Link>
          <Link
            to="/forecasts"
            className="p-4 text-center bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ClockIcon className="h-8 w-8 mx-auto mb-2 text-gray-600" />
            <span className="text-sm font-medium text-gray-900">Прогнозы</span>
          </Link>
          <Link
            to="/timeline-map"
            className="p-4 text-center bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChartBarIcon className="h-8 w-8 mx-auto mb-2 text-gray-600" />
            <span className="text-sm font-medium text-gray-900">Временные окна</span>
          </Link>
        </div>
      </Card>

      {/* Performance Panel Toggle - Developer Mode */}
      <div className="text-center">
        <button
          onClick={() => setShowPerformancePanel(!showPerformancePanel)}
          className="text-xs text-gray-400 hover:text-gray-600 border-b border-dotted"
        >
          {showPerformancePanel ? 'Скрыть' : 'Показать'} панель производительности
        </button>
      </div>

      {/* Performance Panel */}
      {showPerformancePanel && (
        <PerformancePanel />
      )}
    </div>
  );
};

export default Dashboard;