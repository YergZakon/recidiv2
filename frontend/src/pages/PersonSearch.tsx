import React, { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { searchByIIN, clearSearchResults, setCurrentPerson, setCurrentViolations } from '../store/slices/personSlice';
import { calculateRisk, setCurrentCalculation } from '../store/slices/riskSlice';
import { setCurrentTimeline } from '../store/slices/forecastSlice';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import Badge from '../components/common/Badge';
import RiskGauge from '../components/charts/RiskGauge';
import PersonForm from '../components/forms/PersonForm';
import { MagnifyingGlassIcon, UserIcon, CalendarIcon, ExclamationTriangleIcon, DocumentTextIcon, IdentificationIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, Area, AreaChart } from 'recharts';
import axios from 'axios';
import NotificationService from '../services/notificationService';
import { BehaviorPattern } from '../types/api.types';

const PersonSearch: React.FC = () => {
  const dispatch = useAppDispatch();
  const [iin, setIin] = useState('');
  const [activeTab, setActiveTab] = useState<'risk' | 'forecast' | 'violations'>('risk');
  const [searchMode, setSearchMode] = useState<'iin' | 'manual'>('iin');
  const [manualRiskLoading, setManualRiskLoading] = useState(false);
  
  const { currentPerson, currentViolations, searchResults, searchLoading, error: personError } = useAppSelector(state => state.person);
  const { currentCalculation, loading: riskLoading } = useAppSelector(state => state.risk);
  const { currentTimeline, interventionPlan, loading: forecastLoading } = useAppSelector(state => state.forecast);

  // Автоматически заполняем ИИН из URL параметров и выполняем поиск
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const iinParam = urlParams.get('iin');
    
    if (iinParam && iinParam.length === 12) {
      setIin(iinParam);
      // Автоматически запускаем поиск
      setTimeout(() => {
        handleSearchByIin(iinParam);
      }, 100);
    }
  }, []);

  const handleSearchByIin = async (searchIin?: string) => {
    const targetIin = searchIin || iin;
    if (!targetIin || targetIin.length !== 12) {
      toast.error('ИИН должен содержать 12 цифр');
      return;
    }

    try {
      const searchResult = await dispatch(searchByIIN(targetIin)).unwrap();
      
      if (searchResult.person) {
        // Запускаем расчет риска с данными найденного лица
        const personData = {
          full_name: searchResult.person.full_name,
          birth_date: searchResult.person.birth_date,
          gender: searchResult.person.gender,
          pattern: 'mixed_unstable' as BehaviorPattern,
          violations_count: searchResult.violations.length,
          criminal_count: searchResult.violations.filter(v => v.violation_type.includes('Уголовное')).length,
          admin_count: searchResult.violations.filter(v => v.violation_type.includes('Административное')).length,
          last_violation_date: searchResult.violations.length > 0 ? 
            [...searchResult.violations].sort((a, b) => new Date(b.violation_date).getTime() - new Date(a.violation_date).getTime())[0].violation_date : 
            undefined
        };
        const riskResult = await dispatch(calculateRisk(personData)).unwrap();
        
        // Создаем уведомления на основе результата расчета риска
        const notificationService = NotificationService.getInstance();
        if (riskResult && riskResult.calculation) {
          const { risk_score, risk_level } = riskResult.calculation;
          const region = searchResult.person.region;
          
          notificationService.processRiskCalculation(
            targetIin, 
            risk_score, 
            risk_level, 
            region,
            false
          );
        }
        
        // Устанавливаем прогнозы из searchResult в store
        if (searchResult.forecast_timeline) {
          dispatch(setCurrentTimeline(searchResult.forecast_timeline));
        }
        
        // Устанавливаем расчет риска если он есть в searchResult
        if (searchResult.risk_calculation) {
          dispatch(setCurrentCalculation(searchResult.risk_calculation));
        }
        
        toast.success('Лицо найдено, данные загружены');
      }
    } catch (error) {
      console.error('Search error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Ошибка поиска по ИИН';
      toast.error(errorMessage);
    }
  };

  const handleSearch = async () => {
    await handleSearchByIin();
  };

  const handleClear = () => {
    setIin('');
    dispatch(clearSearchResults());
  };

  const handleManualRiskCalculation = async (personData: any) => {
    setManualRiskLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8001/api/persons/calculate-risk', personData);
      const result = response.data;
      
      // Update store with manual calculation results
      dispatch(clearSearchResults());
      
      // Dispatch real actions to set person and calculation data
      dispatch(setCurrentPerson(result.person));
      dispatch(setCurrentViolations(result.violations));
      dispatch(setCurrentCalculation(result.risk_calculation ?? result.calculation));
      
      // Set forecast timeline if available
      if (result.forecast_timeline) {
        dispatch(setCurrentTimeline(result.forecast_timeline));
      }
      
      // Создаем уведомления на основе результата расчета риска
      const notificationService = NotificationService.getInstance();
      if (result.risk_calculation) {
        const { risk_score, risk_level } = result.risk_calculation;
        const region = result.person.region || 'Ручной ввод';
        const personIIN = result.person.iin || '000000000000';
        
        notificationService.processRiskCalculation(
          personIIN, 
          risk_score, 
          risk_level, 
          region,
          false // hasEscalation - можно добавить логику определения эскалации
        );
      }
      
      toast.success('Риск успешно рассчитан');
      setActiveTab('risk');
      
    } catch (error: any) {
      console.error('Error calculating manual risk:', error);
      
      let errorMessage = 'Ошибка при расчете риска';
      
      // Handle FastAPI validation errors
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          // Pydantic validation errors
          errorMessage = detail.map((err: any) => err.msg).join(', ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
    } finally {
      setManualRiskLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU');
  };

  const getRiskComponentsData = () => {
    if (!currentCalculation?.components) return [];
    
    const components = currentCalculation.components;
    return [
      { name: 'История', value: components.history_score, max: 2.0 },
      { name: 'Время', value: components.time_score, max: 1.5 },
      { name: 'Паттерн', value: components.pattern_score, max: 2.5 },
      { name: 'Возраст', value: components.age_score, max: 1.0 },
      { name: 'Социальные', value: components.social_score, max: 1.5 },
      { name: 'Эскалация', value: components.escalation_score, max: 1.5 }
    ];
  };

  const getForecastData = () => {
    if (!currentTimeline?.forecasts) return [];
    
    return currentTimeline.forecasts.map(f => ({
      crime: f.crime_type,
      probability: f.probability,
      days: f.days_until,
      preventability: f.preventability,
      risk: f.risk_level
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Поиск лица и расчет риска</h1>
        <p className="mt-1 text-sm text-gray-500">
          Найдите лицо по ИИН или введите данные вручную для расчета риска рецидива
        </p>
      </div>

      {/* Mode Switcher */}
      <Card>
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setSearchMode('iin')}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                searchMode === 'iin'
                  ? 'border-crime-red text-crime-red'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <IdentificationIcon className="h-5 w-5" />
              <span>Поиск по ИИН</span>
            </button>
            <button
              onClick={() => setSearchMode('manual')}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                searchMode === 'manual'
                  ? 'border-crime-red text-crime-red'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <DocumentTextIcon className="h-5 w-5" />
              <span>Ручной ввод</span>
            </button>
          </nav>
        </div>

        {/* Search by IIN */}
        {searchMode === 'iin' && (
          <div className="space-y-4">
            <div className="flex gap-4">
              <Input
                placeholder="Введите 12-значный ИИН"
                value={iin}
                onChange={(e) => setIin(e.target.value.replace(/\D/g, ''))}
                maxLength={12}
                leftIcon={<MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />}
                fullWidth
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button
                onClick={handleSearch}
                loading={searchLoading || riskLoading}
                disabled={!iin || iin.length !== 12}
              >
                Поиск
              </Button>
              {currentPerson && (
                <Button variant="outline" onClick={handleClear}>
                  Очистить
                </Button>
              )}
            </div>
          </div>
        )}

        {/* Manual Data Entry */}
        {searchMode === 'manual' && (
          <PersonForm 
            onSubmit={handleManualRiskCalculation}
            loading={manualRiskLoading}
          />
        )}
      </Card>

      {/* Loading State */}
      {(searchLoading || riskLoading || manualRiskLoading) && (
        <Loading text={manualRiskLoading ? "Расчет риска..." : "Поиск и расчет риска..."} />
      )}

      {/* Results */}
      {currentPerson && (
        <>
          {/* Person Info and Risk Score */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Person Information */}
            <Card className="lg:col-span-2">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                    <UserIcon className="h-8 w-8 text-gray-500" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">{currentPerson.full_name}</h2>
                    <p className="text-sm text-gray-500">ИИН: {currentPerson.iin}</p>
                    
                    <div className="mt-3 space-y-1">
                      <div className="flex items-center text-sm">
                        <span className="text-gray-500 w-24">Возраст:</span>
                        <span className="font-medium">{currentPerson.age} лет</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="text-gray-500 w-24">Пол:</span>
                        <span className="font-medium">{currentPerson.gender === 'M' ? 'Мужской' : 'Женский'}</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="text-gray-500 w-24">Регион:</span>
                        <span className="font-medium">{currentPerson.region}</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="text-gray-500 w-24">Нарушений:</span>
                        <span className="font-medium">{currentViolations.length}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col items-end space-y-2">
                  {currentCalculation ? (
                    <>
                      <Badge riskLevel={currentCalculation.risk_level} size="lg">
                        {currentCalculation.risk_level === 'critical' && 'Критический'}
                        {currentCalculation.risk_level === 'high' && 'Высокий'}
                        {currentCalculation.risk_level === 'medium' && 'Средний'}
                        {currentCalculation.risk_level === 'low' && 'Низкий'}
                      </Badge>
                      <span className="text-sm text-gray-500">
                        Паттерн: {currentCalculation.pattern}
                      </span>
                    </>
                  ) : (
                    <span className="text-sm text-gray-500">
                      Риск не рассчитан
                    </span>
                  )}
                </div>
              </div>
            </Card>

            {/* Risk Gauge */}
            <Card className="flex items-center justify-center">
              {currentCalculation ? (
                <RiskGauge value={currentCalculation.risk_score} size="md" />
              ) : (
                <span className="text-sm text-gray-500">Риск еще не рассчитан</span>
              )}
            </Card>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('risk')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'risk'
                    ? 'border-crime-red text-crime-red'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Компоненты риска
              </button>
              <button
                onClick={() => setActiveTab('forecast')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'forecast'
                    ? 'border-crime-red text-crime-red'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Прогнозы
              </button>
              <button
                onClick={() => setActiveTab('violations')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'violations'
                    ? 'border-crime-red text-crime-red'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                История нарушений
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div>
            {activeTab === 'risk' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card title="Детализация риск-балла">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={getRiskComponentsData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#e74c3c" />
                      <Bar dataKey="max" fill="#e5e7eb" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>

                <Card title="Рекомендации">
                  <div className="space-y-3">
                    {currentCalculation?.recommendations?.map((rec, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <ExclamationTriangleIcon className="h-5 w-5 text-amber-500 mt-0.5" />
                        <p className="text-sm text-gray-700">{rec}</p>
                      </div>
                    ))}
                  </div>
                  
                  {interventionPlan && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">План вмешательства</h4>
                      <p className="text-sm text-blue-700">
                        Рекомендуется {interventionPlan.programs.length} программ на {interventionPlan.total_duration_days} дней
                      </p>
                      <p className="text-sm text-blue-600 mt-1">
                        Ожидаемое снижение риска: {interventionPlan.expected_risk_reduction}%
                      </p>
                    </div>
                  )}
                </Card>
              </div>
            )}

            {activeTab === 'forecast' && (
              <Card title="Прогноз временных окон преступлений">
                {forecastLoading ? (
                  <Loading />
                ) : currentTimeline ? (
                  <div>
                    <ResponsiveContainer width="100%" height={400}>
                      <BarChart data={getForecastData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="crime" angle={-45} textAnchor="end" height={100} />
                        <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                        <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                        <Tooltip />
                        <Legend />
                        <Bar yAxisId="left" dataKey="probability" fill="#e74c3c" name="Вероятность %" />
                        <Bar yAxisId="left" dataKey="preventability" fill="#2ecc71" name="Предотвратимость %" />
                        <Bar yAxisId="right" dataKey="days" fill="#3498db" name="Дней до преступления" />
                      </BarChart>
                    </ResponsiveContainer>
                    
                    <div className="mt-4 p-4 bg-red-50 rounded-lg">
                      <p className="text-sm font-medium text-red-900">
                        Наибольший риск: {currentTimeline.highest_risk_crime}
                      </p>
                      <p className="text-sm text-red-700 mt-1">
                        Приоритет вмешательства: {
                          currentTimeline.priority_level === 'urgent' ? 'Срочный' :
                          currentTimeline.priority_level === 'high' ? 'Высокий' :
                          currentTimeline.priority_level === 'medium' ? 'Средний' : 'Низкий'
                        }
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500">Нет данных для прогнозирования</p>
                )}
              </Card>
            )}

            {activeTab === 'violations' && (
              <Card title="История нарушений">
                {currentViolations.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Дата
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Тип нарушения
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Статья
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Тяжесть
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {currentViolations.map((violation) => (
                          <tr key={violation.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              <CalendarIcon className="inline h-4 w-4 mr-1 text-gray-400" />
                              {formatDate(violation.violation_date)}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {violation.violation_type}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {violation.article}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge 
                                variant={
                                  violation.severity === 'severe' ? 'danger' :
                                  violation.severity === 'serious' ? 'warning' :
                                  violation.severity === 'moderate' ? 'info' : 'default'
                                }
                              >
                                {violation.severity === 'severe' ? 'Тяжкое' :
                                 violation.severity === 'serious' ? 'Серьезное' :
                                 violation.severity === 'moderate' ? 'Среднее' : 'Легкое'}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-gray-500">Нарушения не найдены</p>
                )}
              </Card>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default PersonSearch;