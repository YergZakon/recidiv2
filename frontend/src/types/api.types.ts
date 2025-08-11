// Основные типы для API

// Уровни риска
export type RiskLevel = 'critical' | 'high' | 'medium' | 'low';

// Паттерны поведения
export type BehaviorPattern = 
  | 'mixed_unstable' 
  | 'chronic_criminal' 
  | 'escalating' 
  | 'deescalating' 
  | 'single';

// Типы преступлений
export type CrimeType = 
  | 'Мошенничество'
  | 'Кража'
  | 'Убийство'
  | 'Вымогательство'
  | 'Грабеж'
  | 'Разбой'
  | 'Изнасилование';

// Интерфейс для данных о лице
export interface Person {
  id: number;
  iin: string;
  full_name: string;
  birth_date: string;
  age: number;
  gender: 'M' | 'F';
  region: string;
  city?: string;
  address?: string;
  phone?: string;
  email?: string;
  created_at: string;
  updated_at?: string;
}

// Интерфейс для нарушения
export interface Violation {
  id: number;
  person_id: number;
  violation_date: string;
  violation_type: string;
  article: string;
  description?: string;
  severity: 'minor' | 'moderate' | 'serious' | 'severe';
  location?: string;
}

// Интерфейс для расчета риска
export interface RiskCalculation {
  person_id: number;
  risk_score: number;
  risk_level: RiskLevel;
  pattern: BehaviorPattern;
  components: RiskComponents;
  recommendations: string[];
  calculated_at: string;
  confidence: number;
}

// Компоненты риск-балла
export interface RiskComponents {
  history_score: number;
  time_score: number;
  pattern_score: number;
  age_score: number;
  social_score: number;
  escalation_score: number;
}

// Прогноз преступления
export interface CrimeForecast {
  crime_type: CrimeType;
  probability: number;
  days_until: number;
  date_predicted: string;
  confidence: number;
  preventability: number;
  risk_level: RiskLevel;
}

// Временная линия прогнозов
export interface ForecastTimeline {
  person_id: number;
  forecasts: CrimeForecast[];
  timeline_start: string;
  timeline_end: string;
  highest_risk_crime: CrimeType;
  intervention_needed: boolean;
  priority_level: 'urgent' | 'high' | 'medium' | 'low';
}

// План вмешательства
export interface InterventionPlan {
  person_id: number;
  risk_level: RiskLevel;
  programs: InterventionProgram[];
  start_date: string;
  end_date: string;
  total_duration_days: number;
  expected_risk_reduction: number;
}

// Программа вмешательства
export interface InterventionProgram {
  id: string;
  name: string;
  description: string;
  type: 'psychological' | 'social' | 'educational' | 'employment' | 'medical';
  duration_days: number;
  intensity: 'low' | 'medium' | 'high';
  effectiveness: number;
}

// Статистика системы
export interface SystemStatistics {
  total_violations: number;
  total_recidivists: number;
  preventable_percent: number;
  patterns_distribution: PatternDistribution;
  crime_statistics: CrimeStatistics;
  regional_statistics: RegionalStatistics[];
}

// Распределение паттернов
export interface PatternDistribution {
  mixed_unstable: number;
  chronic_criminal: number;
  escalating: number;
  deescalating: number;
  single: number;
}

// Статистика преступлений
export interface CrimeStatistics {
  by_type: Record<CrimeType, number>;
  by_severity: Record<string, number>;
  trends: CrimeTrend[];
}

// Тренд преступности
export interface CrimeTrend {
  period: string;
  count: number;
  change_percent: number;
}

// Региональная статистика
export interface RegionalStatistics {
  region: string;
  total_persons: number;
  high_risk_count: number;
  critical_risk_count: number;
  average_risk_score: number;
  status: 'safe' | 'caution' | 'warning' | 'critical';
}

// Запрос для расчета риска (по данным из backend/app/api/endpoints/persons.py)
export interface RiskCalculationRequest {
  full_name: string;
  birth_date: string;
  gender: 'M' | 'F';
  violations_count: number;
  criminal_count: number;
  admin_count: number;
  last_violation_date?: string;
  pattern?: BehaviorPattern;
}

// Ответ с расчетом риска
export interface RiskCalculationResponse {
  calculation: RiskCalculation;
  person: Person;
  forecasts?: CrimeForecast[];
  intervention_plan?: InterventionPlan;
}

// Запрос для поиска по ИИН
export interface PersonSearchRequest {
  iin: string;
}

// Ответ поиска по ИИН
export interface PersonSearchResponse {
  person: Person;
  violations: Violation[];
  risk_calculation?: RiskCalculation;
  forecast_timeline?: ForecastTimeline;
}

// Параметры для списка лиц
export interface PersonListParams {
  page?: number;
  limit?: number;
  risk_level?: RiskLevel;
  pattern?: BehaviorPattern;
  region?: string;
  sort_by?: 'risk_score' | 'name' | 'age' | 'violations_count';
  sort_order?: 'asc' | 'desc';
  search?: string;
}

// Ответ списка лиц
export interface PersonListResponse {
  items: PersonWithRisk[];
  total: number;
  page: number;
  pages: number;
  limit: number;
}

// Лицо с расчетом риска
export interface PersonWithRisk extends Person {
  risk_score: number;
  risk_level: RiskLevel;
  violations_count: number;
  last_violation_date?: string;
  pattern?: BehaviorPattern;
}

// Ошибка API
export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}