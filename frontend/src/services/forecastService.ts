import apiClient from './api';
import {
  ForecastTimeline,
  CrimeForecast,
  CrimeType,
  Person
} from '../types/api.types';

interface ForecastRequest {
  person_id?: number;
  iin?: string;
  crime_types?: CrimeType[];
  horizon_days?: number;
}

interface PriorityCrimesRequest {
  person_id: number;
  top_n?: number;
}

interface CalendarData {
  person_id: number;
  start_date: string;
  end_date: string;
}

interface CalendarResponse {
  dates: Array<{
    date: string;
    risk_level: number;
    events: string[];
  }>;
}

class ForecastService {
  // Получение полной временной линии прогнозов
  async getTimeline(request: ForecastRequest): Promise<ForecastTimeline> {
    return apiClient.post<ForecastTimeline>('/forecasts/timeline', request);
  }

  // Получение приоритетных преступлений для предотвращения
  async getPriorityCrimes(request: PriorityCrimesRequest): Promise<CrimeForecast[]> {
    return apiClient.post<CrimeForecast[]>('/forecasts/priority-crimes', request);
  }

  // Получение персональной временной шкалы
  async getPersonalTimeline(personId: number): Promise<ForecastTimeline> {
    return apiClient.get<ForecastTimeline>(`/timelines/personal/${personId}`);
  }

  // Получение календарных данных для визуализации
  async getCalendarData(request: CalendarData): Promise<CalendarResponse> {
    return apiClient.post<CalendarResponse>('/timelines/calendar', request);
  }

  // Расчет вероятности конкретного преступления
  async calculateProbability(
    personId: number,
    crimeType: CrimeType
  ): Promise<{ probability: number; confidence: number }> {
    return apiClient.post('/forecasts/probability', {
      person_id: personId,
      crime_type: crimeType
    });
  }

  // Получение сравнительного анализа рисков
  async getComparativeAnalysis(personIds: number[]): Promise<any> {
    return apiClient.post('/forecasts/comparative', {
      person_ids: personIds
    });
  }

  // Экспорт прогнозов в Excel
  async exportForecasts(
    personId: number,
    format: 'excel' | 'csv' = 'excel'
  ): Promise<Blob> {
    // Временная заглушка для экспорта
    return new Blob(['export data'], { type: 'application/octet-stream' });
  }
}

export const forecastService = new ForecastService();
export default forecastService;