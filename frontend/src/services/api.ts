import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8001/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          switch (error.response.status) {
            case 401:
              localStorage.removeItem('authToken');
              window.location.href = '/login';
              toast.error('Сессия истекла. Пожалуйста, войдите снова.');
              break;
            case 403:
              toast.error('У вас нет прав для выполнения этого действия');
              break;
            case 404:
              toast.error('Запрашиваемый ресурс не найден');
              break;
            case 500:
              toast.error('Произошла ошибка на сервере');
              break;
            default:
              let errorMessage = 'Произошла ошибка';
              const detail = (error.response.data as any)?.detail;
              
              if (Array.isArray(detail)) {
                // Handle Pydantic validation errors
                errorMessage = detail.map((err: any) => err.msg || err).join(', ');
              } else if (typeof detail === 'string') {
                errorMessage = detail;
              }
              
              toast.error(errorMessage);
          }
        } else if (error.request) {
          toast.error('Нет соединения с сервером');
        } else {
          toast.error('Произошла непредвиденная ошибка');
        }
        return Promise.reject(error);
      }
    );
  }

  // Generic request methods
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url);
    return response.data;
  }

  async patch<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.patch<T>(url, data);
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;