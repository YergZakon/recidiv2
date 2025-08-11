/**
 * TypeScript типы для API интеграции
 * Соответствуют схемам Pydantic из backend/app/schemas/risk.py
 */

// Базовые типы
export type PatternType = 
  | 'mixed_unstable'     // 72.7% всех случаев
  | 'chronic_criminal'   // 13.6% - высокий риск  
  | 'escalating'         // 7% - опасная тенденция
  | 'deescalating'       // 5.7% - снижение риска
  | 'single'             // 1% - единичные случаи
  | 'unknown';           // Неизвестный паттерн

export type RiskLevel = 
  | '🔴 Критический'
  | '🟡 Высокий' 
  | '🟠 Средний'
  | '🟢 Низкий';

export type RiskCategory = 
  | 'Критический'
  | 'Высокий'
  | 'Средний' 
  | 'Низкий';

export type ConfidenceLevel = 
  | 'Высокая'
  | 'Средняя'
  | 'Низкая';

// Запрос на расчет риска
export interface RiskCalculationRequest {
  iin?: string;                    // ИИН человека (опционально)
  pattern_type: PatternType;       // Тип паттерна поведения
  total_cases: number;             // Общее количество дел
  criminal_count?: number;         // Количество уголовных дел
  admin_count?: number;            // Количество административных
  days_since_last?: number;        // Дней с последнего нарушения
  recidivism_rate?: number;        // Дел в год (скорость рецидива)
  current_age: number;             // Текущий возраст
  age_at_first_violation?: number; // Возраст при первом нарушении
  has_property?: 0 | 1;           // Наличие имущества
  has_job?: 0 | 1;                // Наличие работы
  has_family?: 0 | 1;             // Наличие семьи
  substance_abuse?: 0 | 1;        // Злоупотребление веществами
  has_escalation?: 0 | 1;         // Наличие эскалации
  admin_to_criminal?: number;      // Переходы от админ к уголовным
}

// Компоненты риска
export interface RiskComponents {
  pattern: number;     // Компонент паттерна поведения
  history: number;     // Компонент истории нарушений
  time: number;        // Временной компонент
  age: number;         // Возрастной компонент
  social: number;      // Социальный компонент
  escalation: number;  // Компонент эскалации
}

// Ответ с результатами расчета риска
export interface RiskCalculationResponse {
  risk_score: number;              // Риск-балл от 0 до 10
  risk_level: RiskLevel;           // Уровень риска с эмодзи
  risk_category: RiskCategory;     // Категория риска без эмодзи
  recommendation: string;          // Рекомендация по работе с лицом
  components: RiskComponents;      // Разбивка по компонентам
  person_data: Record<string, any>; // Входные данные для аудита
  calculated_at: string;           // Время расчета (ISO string)
}

// Прогноз преступления
export interface CrimeForecastItem {
  crime_type: string;              // Тип преступления
  days: number;                    // Дней до события (30-365)
  date: string;                    // Прогнозируемая дата (ISO string)
  probability: number;             // Вероятность в процентах (5-95)
  confidence: ConfidenceLevel;     // Уровень уверенности
  risk_level: string;              // Риск по временной шкале
  ci_lower: number;                // Нижняя граница доверительного интервала
  ci_upper: number;                // Верхняя граница доверительного интервала
}

// Ответ с прогнозами преступлений
export interface CrimeForecastResponse {
  forecasts: CrimeForecastItem[];  // Список прогнозов
  person_iin?: string;             // ИИН лица
  total_forecasts: number;         // Общее количество прогнозов
  calculated_at: string;           // Время расчета (ISO string)
}

// Быстрая оценка риска
export interface QuickAssessmentResponse {
  risk_score: number;              // Риск-балл от 0 до 10
  risk_level: RiskLevel;           // Уровень риска
  recommendation: string;          // Рекомендация
  components: RiskComponents;      // Компоненты риска
  most_likely_crime?: CrimeForecastItem; // Наиболее вероятное преступление
  calculated_at: string;           // Время расчета
}

// Статистика из исследования
export interface RiskStatisticsResponse {
  total_analyzed: number;          // Всего проанализировано нарушений (146570)
  total_recidivists: number;       // Всего рецидивистов (12333)
  preventable_crimes_percent: number; // Процент предотвратимых преступлений (97.0)
  risk_distribution: {
    critical: number;              // Критический риск (количество)
    high: number;                  // Высокий риск
    medium: number;                // Средний риск
    low: number;                   // Низкий риск
  };
  pattern_distribution: {
    mixed_unstable: number;        // Нестабильный паттерн (72.7%)
    chronic_criminal: number;      // Хронические преступники (13.6%)
    escalating: number;           // Эскалирующие (7.0%)
    deescalating: number;         // Деэскалирующие (5.7%)
    single: number;               // Единичные (1.0%)
  };
}

// Пакетный запрос
export interface BatchRiskRequest {
  persons: RiskCalculationRequest[]; // Список лиц для расчета (макс 100)
}

// Пакетный ответ
export interface BatchRiskResponse {
  results: RiskCalculationResponse[]; // Результаты расчетов
  total_processed: number;            // Всего обработано
  errors: Array<{
    index: string;                    // Индекс записи с ошибкой
    error: string;                    // Описание ошибки
  }>;
  calculated_at: string;              // Время расчета
}

// Приоритетные преступления
export interface PriorityCrime {
  crime_type: string;
  days: number;
  probability: number;
  confidence: ConfidenceLevel;
  risk_level: string;
  prevention_window: number;          // Окно для профилактики (дни)
  urgency: 'Высокая' | 'Средняя' | 'Низкая';
}

export interface PriorityCrimesResponse {
  priority_crimes: PriorityCrime[];
  total_found: number;
  total_analyzed: number;
  min_probability_threshold: number;
  person_iin?: string;
  calculated_at: string;
}

// Календарь профилактики
export interface PreventionCalendarMonth {
  month_name: string;                // Название месяца
  risks: Array<{
    crime_type: string;
    days: number;
    probability: number;
    confidence: ConfidenceLevel;
  }>;
  recommendations: string[];         // Рекомендации по профилактике
  risk_level: 'Высокий' | 'Средний' | 'Низкий';
}

export interface PreventionCalendarResponse {
  calendar: Record<string, PreventionCalendarMonth>; // Ключ: YYYY-MM
  person_iin?: string;
  planning_period_months: number;
  generated_at: string;
}

// Базовые временные окна
export interface BaseTimeWindowsResponse {
  base_windows: Record<string, number>; // Тип преступления -> дни
  description: string;
  source: string;
  total_analyzed: number;
}

// API ошибки
export interface ApiError {
  detail: string | {
    message: string;
    errors: string[];
  };
  status?: number;
}

// Health check ответ
export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  components: {
    constants_loaded: {
      status: string;
      total_analyzed: number;
      total_recidivists: number;
      weights_loaded: number;
      time_windows_loaded: number;
    };
    risk_calculation: {
      status: string;
      validation_working: boolean;
      test_calculation?: number;
    };
    crime_forecasting: {
      status: string;
      forecasts_generated: number;
      expected_forecasts: number;
    };
    api_endpoints: {
      risks_router: string;
      forecasts_router: string;
    };
  };
  performance: {
    test_calculation_completed: boolean;
    test_forecasting_completed: boolean;
  };
}

// Информация об API
export interface ApiInfoResponse {
  name: string;
  version: string;
  description: string;
  research_base: {
    total_analyzed: number;
    total_recidivists: number;
    preventable_percent: number;
  };
  endpoints: {
    risks: string;
    forecasts: string;
    docs: string;
    redoc: string;
  };
  status: string;
  timestamp: string;
}

// Утилитарные типы
export type LoadingState = 'idle' | 'loading' | 'succeeded' | 'failed';

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  loading: boolean;
  timestamp?: string;
}

// Конфигурация API
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
}

// Фильтры для таблиц
export interface TableFilters {
  risk_level?: RiskCategory[];
  pattern_type?: PatternType[];
  age_range?: [number, number];
  days_since_last?: number;
  search_query?: string;
}

// Пагинация
export interface PaginationParams {
  page: number;
  limit: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Экспорт данных
export interface ExportRequest {
  format: 'csv' | 'excel' | 'pdf';
  filters?: TableFilters;
  columns?: string[];
}

// Настройки пользователя
export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: 'ru' | 'en' | 'kz';
  notifications: boolean;
  default_filters: TableFilters;
}

// Уведомления
export interface NotificationItem {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}

// Метрики производительности
export interface PerformanceMetrics {
  api_response_time: number;       // ms
  render_time: number;             // ms
  bundle_size: number;             // bytes
  memory_usage: number;            // MB
}