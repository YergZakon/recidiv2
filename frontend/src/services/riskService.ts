import apiClient from './api';
import {
  RiskCalculationRequest,
  RiskCalculationResponse,
  PersonSearchRequest,
  PersonSearchResponse,
  PersonListParams,
  PersonListResponse,
  SystemStatistics,
  ForecastTimeline,
  InterventionPlan,
  CrimeForecast
} from '../types/api.types';

class RiskService {
  // Расчет риска для лица
  async calculateRisk(data: RiskCalculationRequest): Promise<RiskCalculationResponse> {
    return apiClient.post<RiskCalculationResponse>('/persons/calculate-risk', data);
  }

  // Быстрая оценка риска
  async quickAssessment(iin: string): Promise<RiskCalculationResponse> {
    return apiClient.post<RiskCalculationResponse>('/risks/quick-assessment', { iin });
  }

  // Поиск лица по ИИН
  async searchByIIN(iin: string): Promise<PersonSearchResponse> {
    return apiClient.get<PersonSearchResponse>(`/persons/search/${iin}`);
  }

  // Получение списка лиц с рисками
  async getPersonsList(params?: PersonListParams): Promise<PersonListResponse> {
    return apiClient.get<PersonListResponse>('/persons', params);
  }

  // Получение лиц высокого риска
  async getHighRiskPersons(limit: number = 50): Promise<PersonListResponse> {
    return apiClient.get<PersonListResponse>('/risks/high-risk', { limit });
  }

  // Получение лиц критического риска
  async getCriticalRiskPersons(limit: number = 20): Promise<PersonListResponse> {
    return apiClient.get<PersonListResponse>('/risks/critical', { limit });
  }

  // Получение статистики системы
  async getSystemStatistics(): Promise<SystemStatistics> {
    return apiClient.get<SystemStatistics>('/statistics/summary');
  }

  // Получение временной линии прогнозов
  async getForecastTimeline(personId: number): Promise<ForecastTimeline> {
    return apiClient.post<ForecastTimeline>('/forecasts/timeline', { person_id: personId });
  }

  // Получение прогноза для конкретного типа преступления
  async getSingleCrimeForecast(
    personId: number, 
    crimeType: string
  ): Promise<CrimeForecast> {
    return apiClient.post<CrimeForecast>('/forecasts/single', {
      person_id: personId,
      crime_type: crimeType
    });
  }

  // Получение плана вмешательства
  async getInterventionPlan(personId: number): Promise<InterventionPlan> {
    return apiClient.post<InterventionPlan>('/interventions/plan', {
      person_id: personId
    });
  }

  // Валидация ИИН
  async validateIIN(iin: string): Promise<{ valid: boolean; message?: string }> {
    return apiClient.post<{ valid: boolean; message?: string }>('/persons/validate-iin', { iin });
  }

  // Получение временных окон преступлений
  async getCrimeWindows(): Promise<Record<string, number>> {
    return apiClient.get<Record<string, number>>('/timelines/crime-windows');
  }

  // Получение уровней риска и их описаний
  async getRiskLevels(): Promise<any> {
    return apiClient.get('/risks/levels');
  }
}

export const riskService = new RiskService();
export default riskService;