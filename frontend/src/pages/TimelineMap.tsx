import React, { useState, useEffect } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Loading from '../components/common/Loading';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
  LineChart,
  Line,
  Legend
} from 'recharts';
import {
  MapIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CalendarIcon,
  ChartBarIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';

interface CrimeTimeWindow {
  id: string;
  crime_type: string;
  avg_days: number;
  min_days: number;
  max_days: number;
  preventability: number;
  cases_analyzed: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  color: string;
  interventions_possible: number;
}

interface TimelineEvent {
  day: number;
  crime_type: string;
  probability: number;
  intervention_effectiveness: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

const TimelineMap: React.FC = () => {
  const [selectedCrime, setSelectedCrime] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'30' | '90' | '180' | '365'>('180');
  const [loading, setLoading] = useState(true);
  const [showInterventions, setShowInterventions] = useState(true);

  // Данные временных окон на основе системных констант
  const crimeTimeWindows: CrimeTimeWindow[] = [
    {
      id: 'murder',
      crime_type: 'Убийство',
      avg_days: 143,
      min_days: 90,
      max_days: 200,
      preventability: 97.0,
      cases_analyzed: 45,
      risk_level: 'critical',
      color: '#dc2626',
      interventions_possible: 5
    },
    {
      id: 'theft',
      crime_type: 'Кража',
      avg_days: 146,
      min_days: 30,
      max_days: 120,
      preventability: 87.3,
      cases_analyzed: 1234,
      risk_level: 'high',
      color: '#ea580c',
      interventions_possible: 8
    },
    {
      id: 'fraud',
      crime_type: 'Мошенничество',
      avg_days: 109,
      min_days: 45,
      max_days: 150,
      preventability: 82.3,
      cases_analyzed: 567,
      risk_level: 'high',
      color: '#d97706',
      interventions_possible: 6
    },
    {
      id: 'robbery',
      crime_type: 'Грабеж',
      avg_days: 148,
      min_days: 15,
      max_days: 90,
      preventability: 60.2,
      cases_analyzed: 234,
      risk_level: 'medium',
      color: '#ca8a04',
      interventions_possible: 4
    },
    {
      id: 'assault_robbery',
      crime_type: 'Разбой',
      avg_days: 150,
      min_days: 20,
      max_days: 120,
      preventability: 20.2,
      cases_analyzed: 123,
      risk_level: 'critical',
      color: '#dc2626',
      interventions_possible: 3
    },
    {
      id: 'rape',
      crime_type: 'Изнасилование',
      avg_days: 157,
      min_days: 100,
      max_days: 250,
      preventability: 65.6,
      cases_analyzed: 89,
      risk_level: 'critical',
      color: '#7c2d12',
      interventions_possible: 4
    },
    {
      id: 'extortion',
      crime_type: 'Вымогательство',
      avg_days: 144,
      min_days: 10,
      max_days: 70,
      preventability: 100.0,
      cases_analyzed: 67,
      risk_level: 'medium',
      color: '#059669',
      interventions_possible: 7
    },
    {
      id: 'drugs',
      crime_type: 'Наркотики',
      avg_days: 23,
      min_days: 7,
      max_days: 45,
      preventability: 45.0,
      cases_analyzed: 345,
      risk_level: 'medium',
      color: '#7c3aed',
      interventions_possible: 5
    }
  ];

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, [timeRange]);

  const getFilteredData = () => {
    const maxDays = parseInt(timeRange);
    return crimeTimeWindows.filter(crime => crime.avg_days <= maxDays);
  };

  const getScatterData = () => {
    return getFilteredData().map(crime => ({
      x: crime.avg_days,
      y: crime.preventability,
      size: Math.log(crime.cases_analyzed) * 20,
      crime_type: crime.crime_type,
      color: crime.color,
      risk_level: crime.risk_level,
      cases_analyzed: crime.cases_analyzed,
      interventions_possible: crime.interventions_possible
    }));
  };

  const getTimelineData = () => {
    const maxDays = parseInt(timeRange);
    const selectedWindow = selectedCrime ? 
      crimeTimeWindows.find(crime => crime.id === selectedCrime) : null;
    
    if (!selectedWindow) return [];

    const timeline: TimelineEvent[] = [];
    for (let day = 1; day <= Math.min(selectedWindow.max_days, maxDays); day += 5) {
      const normalizedDay = (day - selectedWindow.min_days) / (selectedWindow.max_days - selectedWindow.min_days);
      const probability = Math.max(0, Math.min(100, 
        50 + 30 * Math.sin((normalizedDay - 0.5) * Math.PI)
      ));
      
      timeline.push({
        day,
        crime_type: selectedWindow.crime_type,
        probability,
        intervention_effectiveness: selectedWindow.preventability * (probability / 100),
        risk_level: selectedWindow.risk_level
      });
    }
    return timeline;
  };

  const getStats = () => {
    const filtered = getFilteredData();
    return {
      totalCrimes: filtered.reduce((sum, crime) => sum + crime.cases_analyzed, 0),
      avgPreventability: filtered.reduce((sum, crime) => sum + crime.preventability, 0) / filtered.length,
      avgWindow: filtered.reduce((sum, crime) => sum + crime.avg_days, 0) / filtered.length,
      totalInterventions: filtered.reduce((sum, crime) => sum + crime.interventions_possible, 0)
    };
  };

  const stats = getStats();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Карта временных окон</h1>
          <p className="mt-1 text-sm text-gray-500">
            Интерактивная визуализация временных окон и точек вмешательства
          </p>
        </div>
        <div className="flex space-x-2">
          {(['30', '90', '180', '365'] as const).map((days) => (
            <Button
              key={days}
              size="sm"
              variant={timeRange === days ? 'primary' : 'outline'}
              onClick={() => {
                setTimeRange(days);
                setLoading(true);
              }}
            >
              {days === '365' ? '1 год' : `${days}д`}
            </Button>
          ))}
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-blue-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-500">Всего случаев</p>
              <p className="text-2xl font-semibold">{stats.totalCrimes.toLocaleString()}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-orange-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-500">Среднее окно</p>
              <p className="text-2xl font-semibold">{stats.avgWindow.toFixed(0)} дней</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-green-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-500">Предотвратимость</p>
              <p className="text-2xl font-semibold">{stats.avgPreventability.toFixed(1)}%</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center">
            <MapIcon className="h-8 w-8 text-purple-500 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-500">Точек вмешательства</p>
              <p className="text-2xl font-semibold">{stats.totalInterventions}</p>
            </div>
          </div>
        </Card>
      </div>

      {loading ? (
        <Loading text="Построение карты временных окон..." />
      ) : (
        <>
          {/* Main Scatter Plot */}
          <Card title="Карта временных окон vs. Предотвратимость">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={showInterventions}
                    onChange={(e) => setShowInterventions(e.target.checked)}
                    className="mr-2"
                  />
                  <span className="text-sm">Показать точки вмешательства</span>
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <AdjustmentsHorizontalIcon className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-500">
                  Размер пузыря = количество случаев
                </span>
              </div>
            </div>
            
            <ResponsiveContainer width="100%" height={500}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  type="number" 
                  dataKey="x" 
                  name="Дни" 
                  domain={[0, parseInt(timeRange)]}
                  label={{ value: 'Среднее время до преступления (дни)', position: 'insideBottom', offset: -10 }}
                />
                <YAxis 
                  type="number" 
                  dataKey="y" 
                  name="Предотвратимость" 
                  domain={[0, 100]}
                  label={{ value: 'Предотвратимость (%)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-white p-3 border rounded-lg shadow-lg">
                          <p className="font-medium">{data.crime_type}</p>
                          <p className="text-sm">Среднее время: {data.x} дней</p>
                          <p className="text-sm">Предотвратимость: {data.y.toFixed(1)}%</p>
                          <p className="text-sm">Случаев: {data.cases_analyzed}</p>
                          <p className="text-sm">Точек вмешательства: {data.interventions_possible}</p>
                          <Badge riskLevel={data.risk_level} size="sm" className="mt-1">
                            {data.risk_level === 'critical' ? 'Критический' :
                             data.risk_level === 'high' ? 'Высокий' :
                             data.risk_level === 'medium' ? 'Средний' : 'Низкий'}
                          </Badge>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter 
                  data={getScatterData()} 
                  onClick={(data) => {
                    const crime = crimeTimeWindows.find(c => c.crime_type === data.crime_type);
                    setSelectedCrime(crime?.id || null);
                  }}
                >
                  {getScatterData().map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color}
                      stroke={selectedCrime && crimeTimeWindows.find(c => c.id === selectedCrime)?.crime_type === entry.crime_type ? '#000' : 'none'}
                      strokeWidth={2}
                      style={{ cursor: 'pointer' }}
                    />
                  ))}
                </Scatter>
                
                {showInterventions && (
                  <>
                    <ReferenceLine x={30} stroke="#22c55e" strokeDasharray="5 5" label="Раннее вмешательство" />
                    <ReferenceLine x={90} stroke="#f59e0b" strokeDasharray="5 5" label="Стандартное вмешательство" />
                    <ReferenceLine y={80} stroke="#3b82f6" strokeDasharray="5 5" label="Высокая предотвратимость" />
                  </>
                )}
              </ScatterChart>
            </ResponsiveContainer>
          </Card>

          {/* Selected Crime Timeline */}
          {selectedCrime && (
            <Card title={`Временная шкала: ${crimeTimeWindows.find(c => c.id === selectedCrime)?.crime_type}`}>
              <div className="mb-4">
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={() => setSelectedCrime(null)}
                >
                  Закрыть детализацию
                </Button>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={getTimelineData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="day" 
                    label={{ value: 'Дни', position: 'insideBottom', offset: -10 }}
                  />
                  <YAxis 
                    label={{ value: 'Вероятность/Эффективность (%)', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="probability" 
                    stroke="#ef4444" 
                    strokeWidth={3}
                    name="Вероятность преступления" 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="intervention_effectiveness" 
                    stroke="#22c55e" 
                    strokeWidth={2}
                    name="Эффективность вмешательства" 
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          )}

          {/* Crime Types Grid */}
          <Card title="Детали временных окон">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {getFilteredData().map((crime) => (
                <div
                  key={crime.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    selectedCrime === crime.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedCrime(selectedCrime === crime.id ? null : crime.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-sm">{crime.crime_type}</h4>
                    <Badge riskLevel={crime.risk_level} size="sm">
                      {crime.risk_level === 'critical' ? 'Критический' :
                       crime.risk_level === 'high' ? 'Высокий' :
                       crime.risk_level === 'medium' ? 'Средний' : 'Низкий'}
                    </Badge>
                  </div>
                  
                  <div className="space-y-1 text-xs text-gray-600">
                    <div className="flex justify-between">
                      <span>Среднее время:</span>
                      <span className="font-medium">{crime.avg_days}д</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Диапазон:</span>
                      <span className="font-medium">{crime.min_days}-{crime.max_days}д</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Предотвратимость:</span>
                      <span className="font-medium">{crime.preventability}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Случаев:</span>
                      <span className="font-medium">{crime.cases_analyzed}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Вмешательств:</span>
                      <span className="font-medium">{crime.interventions_possible}</span>
                    </div>
                  </div>
                  
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full"
                        style={{ 
                          width: `${crime.preventability}%`,
                          backgroundColor: crime.color
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
};

export default TimelineMap;