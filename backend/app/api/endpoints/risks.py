"""
API endpoints для расчета рисков преступности

ОСНОВАНО НА: Портированном RiskCalculator из services/risk_service.py
КРИТИЧНО: Использует ТОЛЬКО портированную логику, НЕ создает новых расчетов

Анализ базируется на 146,570 правонарушениях и 12,333 рецидивистах
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import traceback

from app.core.database import get_db

from app.services.risk_service import RiskService, quick_risk_assessment
from app.schemas.risk import (
    RiskCalculationRequest,
    RiskCalculationResponse, 
    RiskComponentsResponse,
    QuickAssessmentResponse,
    ValidationErrorResponse,
    RiskStatisticsResponse,
    BatchRiskRequest,
    BatchRiskResponse
)
from app.core.constants import (
    TOTAL_VIOLATIONS_ANALYZED, 
    TOTAL_RECIDIVISTS,
    PREVENTABLE_CRIMES_PERCENT,
    PATTERN_DISTRIBUTION
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/risks", tags=["Risk Assessment"])


def get_risk_service() -> RiskService:
    """Dependency для получения RiskService"""
    return RiskService()


@router.post(
    "/calculate", 
    response_model=RiskCalculationResponse,
    summary="Расчет риска рецидива",
    description="Рассчитывает риск-балл (0-10) используя портированный алгоритм из utils/risk_calculator.py"
)
async def calculate_risk(
    request: RiskCalculationRequest,
    service: RiskService = Depends(get_risk_service)
) -> RiskCalculationResponse:
    """
    Основной endpoint для расчета риска
    
    Использует ПОРТИРОВАННЫЙ RiskCalculator из services/risk_service.py
    Гарантирует идентичность расчетов с Streamlit версией
    
    Args:
        request: Данные лица для анализа риска
        service: Сервис расчета рисков
        
    Returns:
        RiskCalculationResponse: Полный результат анализа риска
        
    Raises:
        HTTPException: При ошибках валидации или расчета
    """
    try:
        logger.info(f"Начинаем расчет риска для паттерна: {request.pattern_type}")
        
        # Валидируем данные через RiskService
        person_dict = request.to_calculator_dict()
        is_valid, validation_errors = service.validate_person_data(person_dict)
        
        if not is_valid:
            logger.warning(f"Ошибки валидации: {validation_errors}")
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Ошибки валидации входных данных",
                    "errors": validation_errors
                }
            )
        
        # ИСПОЛЬЗУЕМ ПОРТИРОВАННЫЙ КАЛЬКУЛЯТОР
        result = service.calculate_risk_for_person_dict(person_dict)
        
        # Форматируем ответ согласно схеме
        components = RiskComponentsResponse(**result['risk_components'])
        
        # Извлекаем категорию без эмодзи
        risk_level = result['risk_level']
        risk_category = risk_level.split(' ', 1)[1] if ' ' in risk_level else risk_level
        
        response = RiskCalculationResponse(
            risk_score=result['risk_score'],
            risk_level=risk_level,
            risk_category=risk_category,
            recommendation=result['recommendation'],
            components=components,
            person_data=result['person_data'],
            calculated_at=datetime.fromisoformat(result['calculated_at'].replace('Z', '+00:00'))
        )
        
        logger.info(f"Расчет завершен. Риск-балл: {response.risk_score:.3f} ({response.risk_level})")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при расчете риска: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка при расчете риска: {str(e)}"
        )


@router.post(
    "/quick-assessment",
    response_model=QuickAssessmentResponse,
    summary="Быстрая оценка риска",
    description="Упрощенная оценка риска с определением наиболее вероятного преступления"
)
async def quick_assessment(
    request: RiskCalculationRequest,
    service: RiskService = Depends(get_risk_service)
) -> QuickAssessmentResponse:
    """
    Быстрая оценка риска с прогнозом наиболее вероятного преступления
    
    Args:
        request: Данные лица для анализа
        service: Сервис расчета рисков
        
    Returns:
        QuickAssessmentResponse: Быстрый результат с основными показателями
    """
    try:
        logger.info(f"Быстрая оценка для паттерна: {request.pattern_type}")
        
        person_dict = request.to_calculator_dict()
        
        # Используем портированную функцию quick_risk_assessment
        quick_result = quick_risk_assessment(person_dict)
        
        # Форматируем most_likely_crime если есть
        most_likely_crime = None
        if quick_result.get('most_likely_crime'):
            mlc = quick_result['most_likely_crime']
            most_likely_crime = {
                "crime_type": mlc['crime_type'],
                "days": mlc['days'],
                "date": mlc['date'],
                "probability": mlc['probability'],
                "confidence": mlc['confidence'],
                "risk_level": mlc['risk_level'],
                "ci_lower": mlc['ci_lower'],
                "ci_upper": mlc['ci_upper']
            }
        
        components = RiskComponentsResponse(**quick_result['components'])
        
        response = QuickAssessmentResponse(
            risk_score=quick_result['risk_score'],
            risk_level=quick_result['risk_level'],
            recommendation=quick_result['recommendation'],
            components=components,
            most_likely_crime=most_likely_crime,
            calculated_at=datetime.utcnow()
        )
        
        logger.info(f"Быстрая оценка завершена. Риск: {response.risk_score:.3f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка быстрой оценки: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка быстрой оценки: {str(e)}"
        )


@router.post(
    "/batch-calculate",
    response_model=BatchRiskResponse,
    summary="Пакетный расчет рисков",
    description="Расчет рисков для множества лиц одновременно (до 100 за раз)"
)
async def batch_calculate_risks(
    request: BatchRiskRequest,
    background_tasks: BackgroundTasks,
    service: RiskService = Depends(get_risk_service)
) -> BatchRiskResponse:
    """
    Пакетный расчет рисков для оптимизации производительности
    
    Args:
        request: Список лиц для расчета
        background_tasks: Фоновые задачи FastAPI
        service: Сервис расчета рисков
        
    Returns:
        BatchRiskResponse: Результаты всех расчетов
    """
    try:
        logger.info(f"Начинаем пакетный расчет для {len(request.persons)} лиц")
        
        results = []
        errors = []
        
        # Конвертируем все запросы в формат калькулятора
        persons_data = []
        for i, person_request in enumerate(request.persons):
            try:
                person_dict = person_request.to_calculator_dict()
                persons_data.append(person_dict)
            except Exception as e:
                errors.append({
                    "index": str(i),
                    "error": f"Ошибка валидации: {str(e)}"
                })
                persons_data.append(None)
        
        # Используем пакетный метод RiskService  
        batch_results = service.calculate_risk_batch(
            [pd for pd in persons_data if pd is not None]
        )
        
        # Форматируем результаты
        for i, batch_result in enumerate(batch_results):
            if 'error' in batch_result:
                errors.append({
                    "index": str(i),
                    "error": batch_result['error']
                })
                continue
                
            try:
                components = RiskComponentsResponse(**batch_result['risk_components'])
                
                risk_level = batch_result['risk_level']
                risk_category = risk_level.split(' ', 1)[1] if ' ' in risk_level else risk_level
                
                result = RiskCalculationResponse(
                    risk_score=batch_result['risk_score'],
                    risk_level=risk_level,
                    risk_category=risk_category,
                    recommendation=batch_result['recommendation'],
                    components=components,
                    person_data=batch_result['person_data'],
                    calculated_at=datetime.fromisoformat(batch_result['calculated_at'].replace('Z', '+00:00'))
                )
                
                results.append(result)
                
            except Exception as e:
                errors.append({
                    "index": str(i),
                    "error": f"Ошибка форматирования: {str(e)}"
                })
        
        response = BatchRiskResponse(
            results=results,
            total_processed=len(results),
            errors=errors,
            calculated_at=datetime.utcnow()
        )
        
        logger.info(f"Пакетный расчет завершен. Обработано: {len(results)}, ошибок: {len(errors)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка пакетного расчета: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка пакетного расчета: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=RiskStatisticsResponse,
    summary="Статистика по рискам",
    description="Общая статистика из исследования 146,570 нарушений"
)
async def get_risk_statistics(
    service: RiskService = Depends(get_risk_service)
) -> RiskStatisticsResponse:
    """
    Возвращает статистику из проведенного исследования
    
    Returns:
        RiskStatisticsResponse: Статистические данные из анализа
    """
    try:
        # Получаем статистику из сервиса (использует константы)
        stats = service.get_risk_statistics()
        
        response = RiskStatisticsResponse(
            total_analyzed=stats['total_analyzed'],
            total_recidivists=stats['total_recidivists'],
            preventable_crimes_percent=stats['preventable_percent'],
            risk_distribution={
                "critical": 1856,  # 15% от рецидивистов
                "high": 3083,      # 25% 
                "medium": 4316,    # 35%
                "low": 3078        # 25%
            },
            pattern_distribution=stats['pattern_distribution']
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения статистики: {str(e)}"
        )


@router.get(
    "/health",
    summary="Проверка работоспособности",
    description="Проверяет доступность сервиса расчета рисков"
)
async def health_check(
    service: RiskService = Depends(get_risk_service)
) -> Dict:
    """
    Проверка работоспособности сервиса расчета рисков
    
    Returns:
        Dict: Статус сервиса и основные параметры
    """
    try:
        # Проверяем что сервис инициализировался корректно
        test_data = {
            'pattern_type': 'mixed_unstable',
            'total_cases': 1,
            'current_age': 25
        }
        
        # Пробуем выполнить расчет
        is_valid, _ = service.validate_person_data(test_data)
        
        return {
            "status": "healthy",
            "risk_service": "operational",
            "validation": "working" if is_valid else "issues",
            "constants_loaded": True,
            "total_analyzed": TOTAL_VIOLATIONS_ANALYZED,
            "total_recidivists": TOTAL_RECIDIVISTS,
            "preventable_percent": PREVENTABLE_CRIMES_PERCENT,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get(
    "/high-risk",
    summary="Лица высокого риска",
    description="Возвращает список лиц с высоким уровнем риска"
)
async def get_high_risk_persons(
    limit: int = 50,
    service: RiskService = Depends(get_risk_service),
    db: Session = Depends(get_db)
) -> Dict:
    """Получение списка лиц высокого риска из реальных данных"""
    try:
        from app.models.real_data import PersonReal
        
        # Получаем реальных людей с высоким риском (5-7)
        high_persons = db.query(PersonReal).filter(
            PersonReal.risk_total_risk_score >= 5.0,
            PersonReal.risk_total_risk_score < 7.0
        ).order_by(
            PersonReal.risk_total_risk_score.desc()
        ).limit(limit).all()
        
        high_risk_persons = []
        for person in high_persons:
            high_risk_persons.append({
                "id": f"real_{person.id}",
                "full_name": person.full_name or f"{person.last_name} {person.first_name}",
                "iin": person.iin,
                "age": person.current_age,
                "gender": "M",  # TODO: получить из данных если есть
                "region": person.region or "Неизвестно",
                "risk_score": float(person.risk_total_risk_score or 0),
                "risk_level": "high",
                "violations_count": person.total_cases or 0,
                "last_violation_date": person.last_violation_date.isoformat() if person.last_violation_date else None,
                "pattern": person.pattern_type or "unknown"
            })
        
        return {
            "items": high_risk_persons,
            "total": len(high_risk_persons),
            "page": 1,
            "pages": 1,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Ошибка получения лиц высокого риска: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/critical", 
    summary="Лица критического риска",
    description="Возвращает список лиц с критическим уровнем риска"
)
async def get_critical_risk_persons(
    limit: int = 20,
    service: RiskService = Depends(get_risk_service),
    db: Session = Depends(get_db)
) -> Dict:
    """Получение списка лиц критического риска из реальных данных"""
    try:
        from app.models.real_data import PersonReal
        
        # Получаем реальных людей с критическим риском (7+)
        critical_persons = db.query(PersonReal).filter(
            PersonReal.risk_total_risk_score >= 7.0
        ).order_by(
            PersonReal.risk_total_risk_score.desc()
        ).limit(limit).all()
        
        critical_risk_persons = []
        for person in critical_persons:
            critical_risk_persons.append({
                "id": f"real_{person.id}",
                "full_name": person.full_name or f"{person.last_name} {person.first_name}",
                "iin": person.iin,
                "age": person.current_age,
                "gender": "M",  # TODO: получить из данных если есть
                "region": person.region or "Неизвестно",
                "risk_score": float(person.risk_total_risk_score or 0),
                "risk_level": "critical",
                "violations_count": person.total_cases or 0,
                "last_violation_date": person.last_violation_date.isoformat() if person.last_violation_date else None,
                "pattern": person.pattern_type or "unknown"
            })
        
        return {
            "items": critical_risk_persons,
            "total": len(critical_risk_persons),
            "page": 1,
            "pages": 1,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Ошибка получения лиц критического риска: {e}")
        raise HTTPException(status_code=500, detail=str(e))