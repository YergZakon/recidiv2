import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchPersonsList, setFilters } from '../store/slices/personSlice';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Loading from '../components/common/Loading';
import Badge from '../components/common/Badge';
import VirtualizedList from '../components/common/VirtualizedList';
import useDebounce from '../hooks/useDebounce';
import { usePerformanceMonitor } from '../hooks/useMemoryOptimization';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon, 
  ArrowDownTrayIcon,
  UserIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';
import { RiskLevel } from '../types/api.types';

const PersonList: React.FC = () => {
  const dispatch = useAppDispatch();
  const { personsList, totalPersons, currentPage, totalPages, filters, loading } = useAppSelector(state => state.person);
  usePerformanceMonitor('PersonList');
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<RiskLevel | ''>('');
  const [showFilters, setShowFilters] = useState(false);
  
  // Debounce search term to reduce API calls
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  useEffect(() => {
    dispatch(fetchPersonsList(filters));
  }, [dispatch, filters]);

  // Auto-search when debounced term changes
  useEffect(() => {
    if (debouncedSearchTerm !== filters.search) {
      dispatch(setFilters({
        ...filters,
        search: debouncedSearchTerm,
        page: 1
      }));
    }
  }, [debouncedSearchTerm, filters.search, dispatch]); // Add dependency on current search to prevent loops

  const handlePageChange = useCallback((page: number) => {
    dispatch(setFilters({ ...filters, page }));
  }, [dispatch, filters]);

  const handleRiskLevelFilter = useCallback((riskLevel: RiskLevel | '') => {
    setSelectedRiskLevel(riskLevel);
    dispatch(setFilters({ 
      ...filters, 
      page: 1, 
      risk_level: riskLevel || undefined 
    }));
  }, [dispatch, filters]);

  const handleSortChange = useCallback((sortBy: string, sortOrder: 'asc' | 'desc') => {
    dispatch(setFilters({ 
      ...filters, 
      sort_by: sortBy as any,
      sort_order: sortOrder,
      page: 1
    }));
  }, [dispatch, filters]);

  const handleSearch = useCallback(() => {
    dispatch(setFilters({
      ...filters,
      search: debouncedSearchTerm,
      page: 1
    }));
  }, [dispatch, filters, debouncedSearchTerm]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  }, [handleSearch]);

  const handlePersonDetails = useCallback((personId: string) => {
    // Navigate to person details or open modal
    window.location.href = `/search?iin=${personId}`;
  }, []);

  const formatDate = useCallback((dateString?: string) => {
    if (!dateString) return 'Нет данных';
    return new Date(dateString).toLocaleDateString('ru-RU');
  }, []);

  const getRiskLevelText = useCallback((level: RiskLevel) => {
    switch (level) {
      case 'critical': return 'Критический';
      case 'high': return 'Высокий';
      case 'medium': return 'Средний';
      case 'low': return 'Низкий';
      default: return 'Неизвестно';
    }
  }, []);

  const handleExport = useCallback(() => {
    // Export functionality
    const csvContent = "data:text/csv;charset=utf-8," 
      + "ФИО,ИИН,Возраст,Пол,Риск-балл,Уровень риска,Нарушений,Последнее нарушение,Регион\n"
      + personsList.map(p => 
          `"${p.full_name}","${p.iin}",${p.age},"${p.gender === 'M' ? 'М' : 'Ж'}",${p.risk_score.toFixed(2)},"${getRiskLevelText(p.risk_level)}",${p.violations_count},"${formatDate(p.last_violation_date)}","${p.region}"`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `persons_list_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, [personsList, formatDate, getRiskLevelText]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Списки лиц риска</h1>
          <p className="mt-1 text-sm text-gray-500">
            Всего лиц: {totalPersons.toLocaleString('ru-RU')}
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" size="sm" onClick={handleExport}>
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Экспорт
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
          >
            <AdjustmentsHorizontalIcon className="h-4 w-4 mr-2" />
            Фильтры
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <div className="space-y-4">
          <div className="flex gap-4">
            <Input
              placeholder="Поиск по ФИО или ИИН..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />}
              fullWidth
              onKeyPress={handleKeyPress}
            />
            <Button variant="secondary" onClick={handleSearch}>
              Поиск
            </Button>
          </div>

          {showFilters && (
            <div className="pt-4 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Уровень риска
                  </label>
                  <select
                    value={selectedRiskLevel}
                    onChange={(e) => handleRiskLevelFilter(e.target.value as RiskLevel | '')}
                    className="w-full rounded-lg border-gray-300 shadow-sm focus:border-crime-blue focus:ring focus:ring-crime-blue focus:ring-opacity-50"
                  >
                    <option value="">Все уровни</option>
                    <option value="critical">Критический</option>
                    <option value="high">Высокий</option>
                    <option value="medium">Средний</option>
                    <option value="low">Низкий</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Сортировка
                  </label>
                  <select
                    value={`${filters.sort_by}-${filters.sort_order}`}
                    onChange={(e) => {
                      const [sortBy, sortOrder] = e.target.value.split('-');
                      handleSortChange(sortBy, sortOrder as 'asc' | 'desc');
                    }}
                    className="w-full rounded-lg border-gray-300 shadow-sm focus:border-crime-blue focus:ring focus:ring-crime-blue focus:ring-opacity-50"
                  >
                    <option value="risk_score-desc">Риск (по убыванию)</option>
                    <option value="risk_score-asc">Риск (по возрастанию)</option>
                    <option value="name-asc">ФИО (А-Я)</option>
                    <option value="name-desc">ФИО (Я-А)</option>
                    <option value="age-desc">Возраст (по убыванию)</option>
                    <option value="age-asc">Возраст (по возрастанию)</option>
                    <option value="violations_count-desc">Нарушений (больше)</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Risk Level Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-red-50 border-red-200" onClick={() => handleRiskLevelFilter('critical')} hoverable>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-900">
              {personsList.filter(p => p.risk_level === 'critical').length}
            </div>
            <div className="text-sm text-red-600 font-medium">Критический риск</div>
          </div>
        </Card>
        <Card className="bg-amber-50 border-amber-200" onClick={() => handleRiskLevelFilter('high')} hoverable>
          <div className="text-center">
            <div className="text-2xl font-bold text-amber-900">
              {personsList.filter(p => p.risk_level === 'high').length}
            </div>
            <div className="text-sm text-amber-600 font-medium">Высокий риск</div>
          </div>
        </Card>
        <Card className="bg-orange-50 border-orange-200" onClick={() => handleRiskLevelFilter('medium')} hoverable>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-900">
              {personsList.filter(p => p.risk_level === 'medium').length}
            </div>
            <div className="text-sm text-orange-600 font-medium">Средний риск</div>
          </div>
        </Card>
        <Card className="bg-green-50 border-green-200" onClick={() => handleRiskLevelFilter('low')} hoverable>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-900">
              {personsList.filter(p => p.risk_level === 'low').length}
            </div>
            <div className="text-sm text-green-600 font-medium">Низкий риск</div>
          </div>
        </Card>
      </div>

      {/* Persons Table */}
      <Card>
        {loading ? (
          <Loading />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Лицо
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Риск-балл
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Возраст
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Нарушений
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Последнее нарушение
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Регион
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Действия
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {personsList.map((person) => (
                    <tr key={person.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                              <UserIcon className="h-6 w-6 text-gray-500" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {person.full_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {person.iin}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <Badge riskLevel={person.risk_level}>
                            {person.risk_score.toFixed(1)}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {getRiskLevelText(person.risk_level)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {person.age} лет
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {person.violations_count}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(person.last_violation_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {person.region}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handlePersonDetails(person.iin)}
                        >
                          Подробно
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-3 bg-gray-50 border-t border-gray-200">
                <div className="flex-1 flex justify-between sm:hidden">
                  <Button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    variant="outline"
                    size="sm"
                  >
                    Назад
                  </Button>
                  <Button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    variant="outline"
                    size="sm"
                  >
                    Вперед
                  </Button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Показано с <span className="font-medium">{(currentPage - 1) * filters.limit! + 1}</span> по{' '}
                      <span className="font-medium">
                        {Math.min(currentPage * filters.limit!, totalPersons)}
                      </span>{' '}
                      из <span className="font-medium">{totalPersons}</span> результатов
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      <Button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        variant="outline"
                        size="sm"
                        className="rounded-r-none"
                      >
                        Назад
                      </Button>
                      {[...Array(totalPages)].map((_, i) => {
                        const page = i + 1;
                        if (
                          page === 1 ||
                          page === totalPages ||
                          (page >= currentPage - 2 && page <= currentPage + 2)
                        ) {
                          return (
                            <Button
                              key={page}
                              onClick={() => handlePageChange(page)}
                              variant={page === currentPage ? 'primary' : 'outline'}
                              size="sm"
                              className="rounded-none"
                            >
                              {page}
                            </Button>
                          );
                        } else if (page === currentPage - 3 || page === currentPage + 3) {
                          return (
                            <span key={page} className="px-3 py-1 text-gray-500">
                              ...
                            </span>
                          );
                        }
                        return null;
                      })}
                      <Button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        variant="outline"
                        size="sm"
                        className="rounded-l-none"
                      >
                        Вперед
                      </Button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
};

export default PersonList;