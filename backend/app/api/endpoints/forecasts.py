"""
API endpoints для прогнозирования преступлений

ОСНОВАНО НА: Портированном CrimeForecaster из services/risk_service.py
КРИТИЧНО: Использует ТОЛЬКО портированную логику прогнозирования

Временные окна основаны на анализе 146,570 правонарушений
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import traceback

from app.services.risk_service import RiskService
from app.schemas.risk import (
    RiskCalculationRequest,
    CrimeForecastResponse,
    CrimeForecastItem
)
from app.core.constants import CRIME_TIME_WINDOWS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/forecasts", tags=["Crime Forecasting"])


def get_risk_service() -> RiskService:
    """Dependency для получения RiskService"""
    return RiskService()


@router.post(
    "/timeline",
    response_model=CrimeForecastResponse,
    summary="Прогноз временных окон преступлений",
    description="Прогнозирует временные окна до различных типов преступлений используя портированный алгоритм"
)
async def get_crime_timeline(
    request: RiskCalculationRequest,
    limit: int = Query(8, ge=1, le=20, description="Количество прогнозов (по умолчанию все 8)"),
    service: RiskService = Depends(get_risk_service)
) -> CrimeForecastResponse:
    """
    Создает прогноз временных окон до различных преступлений
    
    Использует ПОРТИРОВАННЫЙ CrimeForecaster из services/risk_service.py
    Базируется на средних временных окнах из исследования 146,570 нарушений
    
    Args:
        request: Данные лица для прогнозирования
        limit: Максимальное количество прогнозов в ответе
        service: Сервис расчета рисков и прогнозов
        
    Returns:
        CrimeForecastResponse: Список прогнозов, отсортированных по времени
        
    Raises:
        HTTPException: При ошибках валидации или прогнозирования
    """
    try:
        logger.info(f"Прогнозирование для паттерна: {request.pattern_type}")
        
        # Конвертируем запрос в формат калькулятора
        person_dict = request.to_calculator_dict()
        
        # Валидируем данные
        is_valid, validation_errors = service.validate_person_data(person_dict)
        if not is_valid:
            logger.warning(f"Ошибки валидации для прогноза: {validation_errors}")
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Ошибки валидации данных для прогнозирования",
                    "errors": validation_errors
                }
            )
        
        # ИСПОЛЬЗУЕМ ПОРТИРОВАННЫЙ FORECASTER
        forecaster = service.forecaster
        forecasts_raw = forecaster.forecast_crime_timeline(person_dict)
        
        # Конвертируем в формат API
        forecast_items = []
        for crime_type, forecast in forecasts_raw.items():
            try:
                item = CrimeForecastItem(
                    crime_type=forecast['crime_type'],
                    days=forecast['days'],
                    date=forecast['date'],
                    probability=forecast['probability'],
                    confidence=forecast['confidence'],
                    risk_level=forecast['risk_level'],
                    ci_lower=forecast['ci_lower'],
                    ci_upper=forecast['ci_upper']
                )
                forecast_items.append(item)
            except Exception as e:
                logger.warning(f"Ошибка форматирования прогноза для {crime_type}: {e}")
                continue
        
        # Сортируем по дням (самые близкие первыми) и ограничиваем
        forecast_items.sort(key=lambda x: x.days)
        limited_forecasts = forecast_items[:limit]
        
        response = CrimeForecastResponse(
            forecasts=limited_forecasts,
            person_iin=request.iin,
            total_forecasts=len(limited_forecasts),
            calculated_at=datetime.utcnow()
        )
        
        logger.info(f"Прогноз завершен. Создано {len(limited_forecasts)} прогнозов")
        if limited_forecasts:
            logger.info(f"Ближайший риск: {limited_forecasts[0].crime_type} через {limited_forecasts[0].days} дней")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при прогнозировании: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка прогнозирования: {str(e)}"
        )


@router.post(
    "/priority-crimes",
    summary="Приоритетные преступления",
    description="Возвращает топ-5 наиболее вероятных преступлений с высокой степенью уверенности"
)
async def get_priority_crimes(
    request: RiskCalculationRequest,
    min_probability: float = Query(50.0, ge=5.0, le=95.0, description="Минимальная вероятность"),
    service: RiskService = Depends(get_risk_service)
) -> Dict:
    """
    Определяет приоритетные преступления для профилактики
    
    Args:
        request: Данные лица
        min_probability: Минимальная вероятность для включения в список
        service: Сервис прогнозирования
        
    Returns:
        Dict: Список приоритетных преступлений с метаданными
    """
    try:
        logger.info(f"Поиск приоритетных преступлений для паттерна: {request.pattern_type}")
        
        person_dict = request.to_calculator_dict()
        
        # Получаем все прогнозы
        forecaster = service.forecaster
        all_forecasts = forecaster.forecast_crime_timeline(person_dict)
        
        # Фильтруем по минимальной вероятности
        priority_crimes = []
        for crime_type, forecast in all_forecasts.items():
            if forecast['probability'] >= min_probability:
                priority_crimes.append({
                    "crime_type": crime_type,
                    "days": forecast['days'],
                    "probability": forecast['probability'],
                    "confidence": forecast['confidence'],
                    "risk_level": forecast['risk_level'],
                    "prevention_window": max(1, forecast['days'] - 30),  # Окно для профилактики
                    "urgency": "Высокая" if forecast['days'] < 90 else "Средняя" if forecast['days'] < 180 else "Низкая"
                })
        
        # Сортируем по убыванию вероятности
        priority_crimes.sort(key=lambda x: x['probability'], reverse=True)
        
        # Берем топ-5
        top_crimes = priority_crimes[:5]
        
        response = {
            "priority_crimes": top_crimes,
            "total_found": len(priority_crimes),
            "total_analyzed": len(all_forecasts),
            "min_probability_threshold": min_probability,
            "person_iin": request.iin,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Найдено {len(priority_crimes)} приоритетных преступлений")
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка определения приоритетных преступлений: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка определения приоритетных преступлений: {str(e)}"
        )


@router.post(
    "/prevention-calendar",
    summary="Календарь профилактических мероприятий",
    description="Создает календарь рекомендуемых профилактических мероприятий на основе прогнозов"
)
async def get_prevention_calendar(
    request: RiskCalculationRequest,
    months_ahead: int = Query(6, ge=1, le=12, description="Количество месяцев вперед"),
    service: RiskService = Depends(get_risk_service)
) -> Dict:
    """
    Создает календарь профилактических мероприятий
    
    Args:
        request: Данные лица
        months_ahead: Период планирования в месяцах
        service: Сервис прогнозирования
        
    Returns:
        Dict: Календарь с рекомендациями по месяцам
    """
    try:
        logger.info(f"Создание календаря профилактики для паттерна: {request.pattern_type}")
        
        person_dict = request.to_calculator_dict()
        
        # Получаем прогнозы
        forecaster = service.forecaster
        forecasts = forecaster.forecast_crime_timeline(person_dict)
        
        # Создаем календарь по месяцам
        calendar = {}
        current_date = datetime.now()
        
        for month_offset in range(months_ahead):
            month_date = current_date + timedelta(days=30 * month_offset)
            month_key = month_date.strftime("%Y-%m")
            month_name = month_date.strftime("%B %Y")
            
            # Определяем риски для этого месяца
            month_risks = []
            month_start_days = 30 * month_offset
            month_end_days = 30 * (month_offset + 1)
            
            for crime_type, forecast in forecasts.items():
                if month_start_days <= forecast['days'] <= month_end_days:
                    month_risks.append({
                        "crime_type": crime_type,
                        "days": forecast['days'],
                        "probability": forecast['probability'],
                        "confidence": forecast['confidence']
                    })
            
            # Генерируем рекомендации
            recommendations = []
            if month_risks:
                # Сортируем по вероятности
                month_risks.sort(key=lambda x: x['probability'], reverse=True)
                
                for risk in month_risks:
                    if risk['probability'] > 60:
                        recommendations.append(f"Усиленный контроль - риск {risk['crime_type']}")
                    elif risk['probability'] > 40:
                        recommendations.append(f"Профилактическая работа - возможен {risk['crime_type']}")
            
            if not recommendations:
                recommendations.append("Стандартный мониторинг")
            
            calendar[month_key] = {
                "month_name": month_name,
                "risks": month_risks,
                "recommendations": recommendations,
                "risk_level": "Высокий" if any(r['probability'] > 70 for r in month_risks) 
                             else "Средний" if any(r['probability'] > 40 for r in month_risks)
                             else "Низкий"
            }
        
        response = {
            "calendar": calendar,
            "person_iin": request.iin,
            "planning_period_months": months_ahead,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Календарь профилактики создан на {months_ahead} месяцев")
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка создания календаря профилактики: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка создания календаря: {str(e)}"
        )


@router.get(
    "/base-windows",
    summary="Базовые временные окна",
    description="Возвращает базовые временные окна из исследования 146,570 нарушений"
)
async def get_base_time_windows() -> Dict:
    """
    Возвращает базовые временные окна для каждого типа преступления
    
    Returns:
        Dict: Средние дни до преступлений из исследования
    """
    try:
        return {
            "base_windows": CRIME_TIME_WINDOWS,
            "description": "Средние дни до преступления на основе анализа 146,570 нарушений",
            "source": "Исследование системы раннего предупреждения преступлений",
            "total_analyzed": 146570
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения базовых окон: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения данных: {str(e)}"
        )


@router.get(
    "/health",
    summary="Проверка работоспособности прогнозирования",
    description="Проверяет доступность сервиса прогнозирования преступлений"
)
async def forecasting_health_check(
    service: RiskService = Depends(get_risk_service)
) -> Dict:
    """
    Проверка работоспособности сервиса прогнозирования
    
    Returns:
        Dict: Статус сервиса прогнозирования
    """
    try:
        # Проверяем что forecaster инициализирован
        forecaster = service.forecaster
        
        # Тестовый прогноз
        test_data = {
            'pattern_type': 'mixed_unstable',
            'total_cases': 1,
            'current_age': 25
        }
        
        test_forecasts = forecaster.forecast_crime_timeline(test_data)
        
        return {
            "status": "healthy",
            "forecaster": "operational", 
            "base_windows_loaded": len(CRIME_TIME_WINDOWS) == 8,
            "test_forecasts_generated": len(test_forecasts),
            "available_crime_types": list(CRIME_TIME_WINDOWS.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки прогнозирования: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }