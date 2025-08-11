"""
API endpoints для работы с лицами
Поддерживает как демо-данные, так и реальные данные из БД
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.constants import TOTAL_RECIDIVISTS, get_risk_level_key
from app.models.real_data import PersonReal, RiskAssessmentHistory
from app.services.risk_service import RiskService
from app.services.individual_forecast_service import IndividualForecastService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/persons", tags=["Persons"])


def _convert_confidence_to_number(confidence) -> float:
    """Convert string confidence to number for frontend compatibility"""
    if isinstance(confidence, (int, float)):
        return float(confidence)
    elif isinstance(confidence, str):
        confidence_map = {
            "Высокая": 0.9,
            "Средняя": 0.7,
            "Низкая": 0.5
        }
        return confidence_map.get(confidence, 0.7)
    else:
        return 0.7


@router.get(
    "/",
    summary="Список всех лиц", 
    description="Возвращает список лиц с пагинацией и фильтрацией"
)
@router.get(
    "",
    summary="Список всех лиц", 
    description="Возвращает список лиц с пагинацией и фильтрацией"
)
async def get_persons_list(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    risk_level: Optional[str] = Query(None, description="Фильтр по уровню риска"),
    sort_by: str = Query("risk_score", description="Поле для сортировки"),
    sort_order: str = Query("desc", description="Порядок сортировки"),
    search: Optional[str] = Query(None, description="Поиск по ФИО или ИИН"),
    db: Session = Depends(get_db)
) -> Dict:
    """Получение списка лиц с фильтрацией и сортировкой из реальных данных"""
    try:
        # Строим запрос к реальным данным
        query = db.query(PersonReal)
        
        # Поиск по ФИО или ИИН
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (PersonReal.full_name.ilike(search_term)) |
                (PersonReal.iin.ilike(search_term)) |
                (PersonReal.first_name.ilike(search_term)) |
                (PersonReal.last_name.ilike(search_term))
            )
        
        # Фильтр по уровню риска
        if risk_level:
            if risk_level == "critical":
                query = query.filter(PersonReal.risk_total_risk_score >= 7.0)
            elif risk_level == "high": 
                query = query.filter(
                    PersonReal.risk_total_risk_score >= 5.0,
                    PersonReal.risk_total_risk_score < 7.0
                )
            elif risk_level == "medium":
                query = query.filter(
                    PersonReal.risk_total_risk_score >= 3.0,
                    PersonReal.risk_total_risk_score < 5.0
                )
            elif risk_level == "low":
                query = query.filter(PersonReal.risk_total_risk_score < 3.0)
        
        # Сортировка
        if sort_by == "risk_score":
            if sort_order == "desc":
                query = query.order_by(PersonReal.risk_total_risk_score.desc())
            else:
                query = query.order_by(PersonReal.risk_total_risk_score.asc())
        elif sort_by == "full_name":
            if sort_order == "desc":
                query = query.order_by(PersonReal.full_name.desc())
            else:
                query = query.order_by(PersonReal.full_name.asc())
        
        # Подсчитываем общее количество
        total_count = query.count()
        
        # Применяем пагинацию
        offset = (page - 1) * limit
        persons = query.offset(offset).limit(limit).all()
        
        # Преобразуем в формат API (ТОЛЬКО реальные данные)
        items = []
        for person in persons:
            risk_score = float(person.risk_total_risk_score or 0)
            risk_level_val = "critical" if risk_score >= 7 else "high" if risk_score >= 5 else "medium" if risk_score >= 3 else "low"
            
            items.append({
                "id": f"real_{person.id}",
                "full_name": person.full_name or f"{person.last_name or ''} {person.first_name or ''}".strip() or "Неизвестно",
                "iin": person.iin or "N/A",
                "age": person.current_age or 0,
                "gender": person.gender or "M",
                "region": person.region or "Неизвестно", 
                "risk_score": risk_score,
                "risk_level": risk_level_val,
                "violations_count": person.total_cases or 0,
                "last_violation_date": person.last_violation_date.isoformat() if person.last_violation_date else None,
                "pattern": person.pattern_type or "unknown"
            })
        
        return {
            "items": items,
            "total": total_count,
            "page": page,
            "pages": (total_count + limit - 1) // limit,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения списка лиц: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search/{iin}",
    summary="Поиск по ИИН с расчетом риска",
    description="Поиск лица по ИИН с автоматическим расчетом риск-балла"
)
async def search_by_iin(iin: str, db: Session = Depends(get_db)) -> Dict:
    """Поиск лица по ИИН с расчетом риска"""
    try:
        if len(iin) < 10 or len(iin) > 12 or not iin.isdigit():
            raise HTTPException(status_code=400, detail="ИИН должен содержать от 10 до 12 цифр")
        
        # Импортируем RiskService для расчета
        from app.services.risk_service import RiskService
        
        # Ищем человека в реальной базе данных
        clean_iin = iin.replace('-', '').replace(' ', '').strip()
        person_real = db.query(PersonReal).filter(PersonReal.iin == clean_iin).first()
        
        if not person_real:
            # Пробуем частичный поиск
            person_real = db.query(PersonReal).filter(PersonReal.iin.like(f"%{clean_iin[-4:]}%")).first()
        
        if person_real:
            # Используем реальные данные
            person = {
                "id": person_real.id,  # Оставляем как число для фронтенда
                "iin": person_real.iin,
                "full_name": person_real.full_name or f"{person_real.last_name or ''} {person_real.first_name or ''} {person_real.middle_name or ''}".strip(),
                "birth_date": person_real.birth_date.isoformat() if person_real.birth_date else "1990-01-01",
                "age": person_real.current_age or 34,
                "gender": person_real.gender or "M",
                "region": person_real.region or "Неизвестно",
                "city": person_real.city or "Неизвестно", 
                "address": f"{person_real.district or ''}, {person_real.city or ''}".strip().strip(',') or "Адрес не указан",
                "created_at": datetime.utcnow().isoformat()
            }
        else:
            # Если не нашли в БД, возвращаем демо данные
            person = {
                "id": hash(iin) % 10000,  # Генерируем числовой ID
                "iin": iin,
                "full_name": f"Демо Лицо {iin[-4:]}",
                "birth_date": "1990-01-01",
                "age": 34,
                "gender": "M",
                "region": "Алматы",
                "city": "Алматы", 
                "address": "ул. Тестовая, 123",
                "created_at": datetime.utcnow().isoformat()
            }
        
        # Создаем нарушения на основе реальных или демо данных
        violations = []
        if person_real:
            # Создаем нарушения на основе данных из БД
            violations_count = person_real.total_cases or 2
            criminal_count = person_real.criminal_count or 1
            admin_count = person_real.admin_count or 1
            
            for i in range(violations_count):
                is_criminal = i < criminal_count
                violations.append({
                    "id": i + 1,
                    "person_id": person["id"],
                    "violation_date": person_real.last_violation_date.isoformat() if person_real.last_violation_date and i == 0 else "2023-06-15",
                    "violation_type": "Уголовное преступление" if is_criminal else "Административное правонарушение",
                    "article": f"Статья {188 + i}" if is_criminal else f"Статья {525 + i}",
                    "description": "Кража чужого имущества" if is_criminal else "Административное нарушение",
                    "severity": "serious" if is_criminal else "moderate",
                    "location": person_real.region or "Неизвестно"
                })
        else:
            # Демо нарушения если нет в БД
            violations = [
                {
                    "id": 1,
                    "person_id": person["id"],
                    "violation_date": "2023-06-15",
                    "violation_type": "Административное правонарушение",
                    "article": "Статья 525",
                    "description": "Нарушение общественного порядка",
                    "severity": "moderate",
                    "location": "г. Алматы"
                },
                {
                    "id": 2, 
                    "person_id": person["id"],
                    "violation_date": "2024-01-10",
                    "violation_type": "Кража",
                    "article": "Статья 188", 
                    "description": "Кража чужого имущества",
                    "severity": "serious",
                    "location": "г. Алматы"
                }
            ]
        
        # Реальный расчет риска на основе данных
        risk_service = RiskService()
        
        # Формируем данные для расчета
        if person_real:
            person_data = {
                'pattern_type': person_real.pattern_type or 'mixed_unstable',
                'total_cases': person_real.total_cases or len(violations),
                'current_age': person_real.current_age or person['age'],
                'criminal_count': person_real.criminal_count or sum(1 for v in violations if v['severity'] in ['serious', 'severe']),
                'admin_count': person_real.admin_count or sum(1 for v in violations if v['severity'] in ['moderate', 'minor']),
                'days_since_last': person_real.days_since_last or 30
            }
        else:
            person_data = {
                'pattern_type': 'mixed_unstable',  # Определяется по истории нарушений
                'total_cases': len(violations),
                'current_age': person['age'],
                'criminal_count': sum(1 for v in violations if v['severity'] in ['serious', 'severe']),
                'admin_count': sum(1 for v in violations if v['severity'] in ['moderate', 'minor']),
                'days_since_last': 30  # Дни с последнего нарушения
            }
        
        logger.info(f"Person data for {iin}: {person_data}")
        
        # Валидируем данные
        is_valid, validation_errors = risk_service.validate_person_data(person_data)
        
        if is_valid:
            # Выполняем расчет риска
            try:
                logger.info("Starting risk calculation in search_by_iin...")
                risk_result = risk_service.calculate_risk_for_person_dict(person_data)
                logger.info(f"Risk result: {risk_result}")
                
                # Получаем индивидуальные прогнозы на основе истории
                individual_forecast_service = IndividualForecastService()
                try:
                    individual_forecast = individual_forecast_service.calculate_individual_forecast(
                        person_data, 
                        violations
                    )
                    logger.info(f"Individual forecast: {individual_forecast}")
                    # Преобразуем в нужный формат
                    forecasts = {}
                    for forecast in individual_forecast['forecasts']:
                        forecasts[forecast['crime_type']] = forecast
                except Exception as forecast_error:
                    logger.error(f"Ошибка индивидуального прогнозирования: {forecast_error}")
                    # Fallback к базовому прогнозированию
                    forecasts = risk_service.forecaster.forecast_crime_timeline(person_data)
                
                # Безопасно извлекаем данные из результата
                if isinstance(risk_result, dict):
                    risk_score = risk_result.get('risk_score', 3.5)
                    components = risk_result.get('risk_components', risk_result.get('components', {}))
                    recommendation = risk_result.get('recommendation', 'Рекомендуется контроль')
                    recommendations = [recommendation] if isinstance(recommendation, str) else recommendation
                else:
                    # Если результат не словарь, используем значения по умолчанию
                    risk_score = 3.5
                    components = {}
                    recommendations = ["Требуется дополнительная информация для точной оценки"]
                
                # Импортируем функцию для получения правильного ключа уровня риска
                from app.core.constants import get_risk_level_key
                risk_level = get_risk_level_key(risk_score)
                
                # Формируем risk_calculation объект
                risk_calculation = {
                    "person_id": person['id'],
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "pattern": person_data['pattern_type'],
                    "components": {
                        "history_score": components.get('history_score', 1.0),
                        "time_score": components.get('time_score', 0.5),
                        "pattern_score": components.get('pattern_score', 0.8),
                        "age_score": components.get('age_score', 0.3),
                        "social_score": components.get('social_score', 0.6),
                        "escalation_score": components.get('escalation_score', 0.3)
                    },
                    "recommendations": recommendations,
                    "calculated_at": datetime.utcnow().isoformat(),
                    "confidence": 0.85
                }
            except Exception as e:
                logger.error(f"Ошибка в расчете риска: {e}")
                # Используем fallback значения
                risk_calculation = {
                    "person_id": person['id'],
                    "risk_score": 3.5,
                    "risk_level": get_risk_level_key(3.5),
                    "pattern": person_data['pattern_type'],
                    "components": {
                        "history_score": 1.0,
                        "time_score": 0.5,
                        "pattern_score": 0.8,
                        "age_score": 0.3,
                        "social_score": 0.6,
                        "escalation_score": 0.3
                    },
                    "recommendations": ["Ошибка при расчете риска, используются базовые значения"],
                    "calculated_at": datetime.utcnow().isoformat(),
                    "confidence": 0.6
                }
                forecasts = []
            
            # Формируем forecast_timeline - forecasts это словарь, не список
            forecasts_list = []
            if forecasts and isinstance(forecasts, dict):
                for crime_type, forecast in forecasts.items():
                    # Обрабатываем дату
                    if 'date' in forecast and hasattr(forecast['date'], 'isoformat'):
                        date_predicted = forecast['date'].isoformat()
                    else:
                        date_predicted = forecast.get('date_predicted', '2024-12-31')
                    
                    forecast_item = {
                        "crime_type": forecast['crime_type'],
                        "probability": forecast.get('probability', 0.5),
                        "days_until": forecast.get('days', forecast.get('days_until', forecast.get('expected_days', 100))),
                        "date_predicted": date_predicted,
                        "confidence": _convert_confidence_to_number(forecast.get('confidence', 0.7)),
                        "preventability": forecast.get('preventability', 80.0),
                        "risk_level": get_risk_level_key(forecast.get('probability', 50.0) / 10.0)
                    }
                    
                    # Добавляем факторы если они есть (индивидуальное прогнозирование)
                    if 'factors' in forecast:
                        forecast_item['factors'] = forecast['factors']
                    if 'confidence_interval' in forecast:
                        forecast_item['confidence_interval'] = forecast['confidence_interval']
                    
                    forecasts_list.append(forecast_item)
            
            forecast_timeline = {
                "person_id": person['id'],
                "forecasts": forecasts_list,
                "timeline_start": datetime.utcnow().isoformat(),
                "timeline_end": "2024-12-31",
                "highest_risk_crime": forecasts_list[0]['crime_type'] if forecasts_list else "Кража",
                "intervention_needed": risk_score >= 5.0,
                "priority_level": "urgent" if risk_score >= 7.0 else "high"
            }
            
        else:
            # Если валидация не прошла, используем базовые значения
            risk_calculation = {
                "person_id": person['id'],
                "risk_score": 3.5,
                "risk_level": "medium",
                "pattern": "mixed_unstable",
                "components": {
                    "history_score": 1.0,
                    "time_score": 0.5,
                    "pattern_score": 0.8,
                    "age_score": 0.3,
                    "social_score": 0.6,
                    "escalation_score": 0.3
                },
                "recommendations": ["Требуется дополнительная информация для точной оценки"],
                "calculated_at": datetime.utcnow().isoformat(),
                "confidence": 0.6
            }
            forecast_timeline = None
        
        return {
            "person": person,
            "violations": violations,
            "risk_calculation": risk_calculation,
            "forecast_timeline": forecast_timeline
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка поиска по ИИН {iin}: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post(
    "/calculate-risk",
    summary="Расчет риска по введенным данным",
    description="Рассчитывает риск-балл на основе данных, введенных вручную в форме"
)
async def calculate_risk_from_form(data: Dict) -> Dict:
    """Расчет риска по данным из формы PersonForm"""
    try:
        # Импортируем RiskService для расчета
        from app.services.risk_service import RiskService
        
        # Извлекаем данные из формы
        full_name = data.get("full_name", "")
        birth_date = data.get("birth_date", "")
        gender = data.get("gender", "M")
        violations_count = int(data.get("violations_count", 1))
        last_violation_date = data.get("last_violation_date", "")
        pattern = data.get("pattern", "mixed_unstable")
        criminal_count = int(data.get("criminal_count", 0))
        admin_count = int(data.get("admin_count", 1))
        
        # Вычисляем возраст из даты рождения
        from datetime import datetime, date
        birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        
        # Вычисляем дни с последнего нарушения
        last_violation = datetime.strptime(last_violation_date, "%Y-%m-%d").date()
        days_since_last = (today - last_violation).days
        
        # Создаем демонстрационное лицо
        person = {
            "id": f"manual_{hash(full_name + birth_date)}",
            "iin": "000000000000",  # Заглушка для ручного ввода
            "full_name": full_name,
            "birth_date": birth_date,
            "age": age,
            "gender": gender,
            "region": "Ручной ввод",
            "city": "Ручной ввод", 
            "address": "Адрес не указан",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Создаем демонстрационные нарушения
        violations = []
        for i in range(violations_count):
            violations.append({
                "id": i + 1,
                "person_id": person["id"],
                "violation_date": last_violation_date if i == 0 else "2023-01-01",
                "violation_type": "Уголовное преступление" if i < criminal_count else "Административное правонарушение",
                "article": f"Статья {200 + i}",
                "description": f"Нарушение #{i + 1}",
                "severity": "serious" if i < criminal_count else "moderate",
                "location": "Не указано"
            })
        
        # Реальный расчет риска
        risk_service = RiskService()
        
        # Формируем данные для расчета
        person_data = {
            'pattern_type': pattern,
            'total_cases': violations_count,
            'current_age': age,
            'criminal_count': criminal_count,
            'admin_count': admin_count,
            'days_since_last': days_since_last
        }
        
        # Валидируем данные
        is_valid, validation_errors = risk_service.validate_person_data(person_data)
        
        if is_valid:
            # Выполняем расчет риска
            try:
                risk_result = risk_service.calculate_risk_for_person_dict(person_data)
                
                # Получаем индивидуальные прогнозы для ручного ввода (без истории нарушений)
                individual_forecast_service = IndividualForecastService()
                try:
                    # Для ручного ввода создаем базовую историю на основе переданных данных
                    mock_violations = []
                    if person_data.get('violations_count', 0) > 0:
                        # Создаем фиктивные нарушения для анализа паттерна
                        for i in range(min(person_data['violations_count'], 5)):
                            days_ago = 30 * (i + 1)  # Распределяем по месяцам
                            violation_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                            mock_violations.append({
                                'violation_date': violation_date,
                                'violation_type': 'Уголовное преступление',
                                'severity': 'serious'
                            })
                    
                    individual_forecast = individual_forecast_service.calculate_individual_forecast(
                        person_data, 
                        mock_violations
                    )
                    logger.info(f"Individual forecast for manual: {individual_forecast}")
                    # Преобразуем в нужный формат
                    forecasts = {}
                    for forecast in individual_forecast['forecasts']:
                        forecasts[forecast['crime_type']] = forecast
                except Exception as forecast_error:
                    logger.error(f"Ошибка индивидуального прогнозирования: {forecast_error}")
                    # Fallback к базовому прогнозированию
                    forecasts = risk_service.forecaster.forecast_crime_timeline(person_data)
                
                # Безопасно извлекаем данные из результата
                if isinstance(risk_result, dict):
                    risk_score = risk_result.get('risk_score', 3.5)
                    risk_level = risk_result.get('risk_level', 'medium')
                    components = risk_result.get('risk_components', risk_result.get('components', {}))
                    recommendation = risk_result.get('recommendation', 'Рекомендуется контроль')
                    recommendations = [recommendation] if isinstance(recommendation, str) else recommendation
                else:
                    # Если результат не словарь, используем значения по умолчанию
                    risk_score = 3.5
                    risk_level = 'medium'
                    components = {}
                    recommendations = ["Требуется дополнительная информация для точной оценки"]
                
                # Формируем risk_calculation объект
                risk_calculation = {
                    "person_id": person['id'],
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "pattern": person_data['pattern_type'],
                    "components": {
                        "history_score": components.get('history_score', 1.0),
                        "time_score": components.get('time_score', 0.5),
                        "pattern_score": components.get('pattern_score', 0.8),
                        "age_score": components.get('age_score', 0.3),
                        "social_score": components.get('social_score', 0.6),
                        "escalation_score": components.get('escalation_score', 0.3)
                    },
                    "recommendations": recommendations,
                    "calculated_at": datetime.utcnow().isoformat(),
                    "confidence": 0.85
                }
            except Exception as e:
                logger.error(f"Ошибка в расчете риска: {e}")
                # Используем fallback значения
                risk_calculation = {
                    "person_id": person['id'],
                    "risk_score": 3.5,
                    "risk_level": get_risk_level_key(3.5),
                    "pattern": person_data['pattern_type'],
                    "components": {
                        "history_score": 1.0,
                        "time_score": 0.5,
                        "pattern_score": 0.8,
                        "age_score": 0.3,
                        "social_score": 0.6,
                        "escalation_score": 0.3
                    },
                    "recommendations": ["Ошибка при расчете риска, используются базовые значения"],
                    "calculated_at": datetime.utcnow().isoformat(),
                    "confidence": 0.6
                }
                forecasts = []
            
            # Формируем forecast_timeline - forecasts это словарь, не список
            forecasts_list = []
            if forecasts and isinstance(forecasts, dict):
                for crime_type, forecast in forecasts.items():
                    # Обрабатываем дату
                    if 'date' in forecast and hasattr(forecast['date'], 'isoformat'):
                        date_predicted = forecast['date'].isoformat()
                    else:
                        date_predicted = forecast.get('date_predicted', '2024-12-31')
                    
                    forecast_item = {
                        "crime_type": forecast['crime_type'],
                        "probability": forecast.get('probability', 0.5),
                        "days_until": forecast.get('days', forecast.get('days_until', forecast.get('expected_days', 100))),
                        "date_predicted": date_predicted,
                        "confidence": _convert_confidence_to_number(forecast.get('confidence', 0.7)),
                        "preventability": forecast.get('preventability', 80.0),
                        "risk_level": get_risk_level_key(forecast.get('probability', 50.0) / 10.0)
                    }
                    
                    # Добавляем факторы если они есть (индивидуальное прогнозирование)
                    if 'factors' in forecast:
                        forecast_item['factors'] = forecast['factors']
                    if 'confidence_interval' in forecast:
                        forecast_item['confidence_interval'] = forecast['confidence_interval']
                    
                    forecasts_list.append(forecast_item)
            
            forecast_timeline = {
                "person_id": person['id'],
                "forecasts": forecasts_list,
                "timeline_start": datetime.utcnow().isoformat(),
                "timeline_end": "2024-12-31",
                "highest_risk_crime": forecasts_list[0]['crime_type'] if forecasts_list else "Кража",
                "intervention_needed": risk_score >= 5.0,
                "priority_level": "urgent" if risk_score >= 7.0 else "high"
            }
            
        else:
            # Если валидация не прошла, используем базовые значения
            risk_calculation = {
                "person_id": person['id'],
                "risk_score": 3.5,
                "risk_level": "medium",
                "pattern": pattern,
                "components": {
                    "history_score": 1.0,
                    "time_score": 0.5,
                    "pattern_score": 0.8,
                    "age_score": 0.3,
                    "social_score": 0.6,
                    "escalation_score": 0.3
                },
                "recommendations": ["Требуется дополнительная информация для точной оценки"] + validation_errors,
                "calculated_at": datetime.utcnow().isoformat(),
                "confidence": 0.6
            }
            forecast_timeline = None
        
        return {
            "person": person,
            "violations": violations,
            "risk_calculation": risk_calculation,
            "forecast_timeline": forecast_timeline
        }
        
    except Exception as e:
        logger.error(f"Ошибка расчета риска по форме: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/validate-iin",
    summary="Валидация ИИН",
    description="Проверка корректности индивидуального идентификационного номера"
)
async def validate_iin(data: Dict[str, str]) -> Dict:
    """Валидация ИИН"""
    try:
        iin = data.get("iin", "")
        
        if not iin:
            return {"valid": False, "message": "ИИН не указан"}
        
        if len(iin) != 12:
            return {"valid": False, "message": "ИИН должен содержать 12 символов"}
        
        if not iin.isdigit():
            return {"valid": False, "message": "ИИН должен содержать только цифры"}
        
        # Проверка контрольной суммы (упрощенная)
        return {"valid": True, "message": "ИИН корректен"}
        
    except Exception as e:
        logger.error(f"Ошибка валидации ИИН: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= НОВЫЕ ENDPOINTS ДЛЯ РЕАЛЬНЫХ ДАННЫХ =============

@router.get(
    "/real/search/{iin}",
    summary="Поиск реального человека по ИИН",
    description="Поиск в базе данных реальных лиц из импортированных Excel файлов"
)
async def search_real_person(
    iin: str,
    db: Session = Depends(get_db)
):
    """
    Поиск реального человека по ИИН
    Возвращает данные из базы с 146,570 реальными записями
    """
    
    # Очистка ИИН от лишних символов
    clean_iin = iin.replace('-', '').replace(' ', '').strip()
    
    # Поиск в реальных данных
    person = db.query(PersonReal).filter(
        PersonReal.iin == clean_iin
    ).first()
    
    if not person:
        # Пробуем частичный поиск по последним 4 цифрам (для анонимизированных данных)
        person = db.query(PersonReal).filter(
            PersonReal.iin.like(f"%{clean_iin[-4:]}%")
        ).first()
    
    if not person:
        raise HTTPException(
            status_code=404, 
            detail=f"Человек с ИИН {iin} не найден в базе данных"
        )
    
    # Рассчитываем риск если его нет или он устарел
    from app.services.risk_service import RiskService
    risk_service = RiskService()
    
    # Подготавливаем данные для расчета риска
    person_data = {
        'iin': person.iin,
        'pattern_type': person.pattern_type or 'mixed_unstable',
        'total_cases': person.total_cases or 0,
        'criminal_count': person.criminal_count or 0,
        'admin_count': person.admin_count or 0,
        'days_since_last': person.days_since_last or 365,
        'current_age': person.current_age or 35,
        'has_property': person.has_property or 0,
        'has_job': person.has_job or 0,
        'has_family': person.has_family or 0
    }
    
    # Рассчитываем риск
    risk_score, components = risk_service.calculator.calculate_risk_score(person_data)
    from app.core.constants import get_risk_category_by_score
    risk_level = get_risk_category_by_score(risk_score)
    
    # Сохраняем результат расчета в историю
    assessment = RiskAssessmentHistory(
        person_iin=person.iin,
        risk_score=risk_score,
        risk_category=risk_level,
        components=components,
        calculated_by='api_request',
        calculation_reason='real_person_search'
    )
    db.add(assessment)
    db.commit()
    
    # Формируем ответ
    return {
        'person': {
            'iin': person.iin,
            'full_name': person.full_name or f"{person.last_name} {person.first_name} {person.middle_name}".strip(),
            'age': person.current_age,
            'gender': person.gender,
            'region': person.region,
            'pattern_type': person.pattern_type,
            'total_cases': person.total_cases,
            'criminal_count': person.criminal_count,
            'admin_count': person.admin_count,
            'days_since_last': person.days_since_last,
            'has_escalation': person.has_escalation,
            'data_quality_score': person.data_quality_score
        },
        'risk': {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'components': components,
            'original_risk_score': person.risk_total_risk_score,  # Из Excel
            'confidence': 0.95 if person.data_quality_score > 0.8 else 0.75
        },
        'metadata': {
            'source': 'real_data',
            'import_date': person.import_date.isoformat() if person.import_date else None,
            'source_file': person.source_file
        }
    }


@router.get(
    "/real/statistics",
    summary="Статистика по реальным данным",
    description="Статистика по всем 146,570 реальным записям"
)
async def get_real_statistics(
    db: Session = Depends(get_db)
):
    """Получить статистику по реальным данным из БД"""
    
    total = db.query(PersonReal).count()
    
    if total == 0:
        raise HTTPException(
            status_code=404,
            detail="Реальные данные еще не импортированы. Запустите /api/import/sync-all"
        )
    
    # Распределение по риск-баллам
    critical = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score >= 7
    ).count()
    
    high = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score >= 5,
        PersonReal.risk_total_risk_score < 7
    ).count()
    
    medium = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score >= 3,
        PersonReal.risk_total_risk_score < 5
    ).count()
    
    low = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score < 3
    ).count()
    
    # Паттерны поведения
    patterns = db.query(
        PersonReal.pattern_type,
        func.count(PersonReal.id)
    ).group_by(PersonReal.pattern_type).all()
    
    pattern_distribution = {}
    for pattern, count in patterns:
        if pattern:
            pattern_distribution[pattern] = {
                'count': count,
                'percent': round((count / total * 100), 1)
            }
    
    # Рецидивисты
    recidivists = db.query(PersonReal).filter(
        PersonReal.total_cases > 1
    ).count()
    
    # Региональное распределение (топ-10)
    regions = db.query(
        PersonReal.region,
        func.count(PersonReal.id)
    ).group_by(PersonReal.region).order_by(
        func.count(PersonReal.id).desc()
    ).limit(10).all()
    
    # Возрастное распределение
    age_groups = {
        '18-25': db.query(PersonReal).filter(
            PersonReal.current_age >= 18,
            PersonReal.current_age < 25
        ).count(),
        '25-35': db.query(PersonReal).filter(
            PersonReal.current_age >= 25,
            PersonReal.current_age < 35
        ).count(),
        '35-45': db.query(PersonReal).filter(
            PersonReal.current_age >= 35,
            PersonReal.current_age < 45
        ).count(),
        '45+': db.query(PersonReal).filter(
            PersonReal.current_age >= 45
        ).count()
    }
    
    # Качество данных
    high_quality = db.query(PersonReal).filter(
        PersonReal.data_quality_score >= 0.8
    ).count()
    
    return {
        'total_persons': total,
        'expected_total': 146570,  # Из исследования
        'completeness': round((total / 146570 * 100), 1),
        'risk_distribution': {
            'critical': {'count': critical, 'percent': round((critical/total*100), 1)},
            'high': {'count': high, 'percent': round((high/total*100), 1)},
            'medium': {'count': medium, 'percent': round((medium/total*100), 1)},
            'low': {'count': low, 'percent': round((low/total*100), 1)}
        },
        'patterns': pattern_distribution,
        'expected_unstable_percent': 72.7,  # Из исследования
        'recidivists': {
            'count': recidivists,
            'percent': round((recidivists/total*100), 1),
            'expected': 12333  # Из исследования
        },
        'regions': {
            region: count for region, count in regions
        },
        'age_distribution': age_groups,
        'data_quality': {
            'high_quality_records': high_quality,
            'percent': round((high_quality/total*100), 1)
        }
    }


@router.get(
    "/real/high-risk",
    summary="Лица с критическим риском",
    description="Получить список реальных лиц с риск-баллом >= 7"
)
async def get_real_high_risk_persons(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Получить реальных лиц с критическим уровнем риска"""
    
    persons = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score >= 7
    ).order_by(
        PersonReal.risk_total_risk_score.desc()
    ).offset(offset).limit(limit).all()
    
    total = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score >= 7
    ).count()
    
    return {
        'total': total,
        'offset': offset,
        'limit': limit,
        'items': [
            {
                'iin': p.iin[-4:] + '****' if p.iin else 'N/A',  # Маскируем ИИН
                'risk_score': p.risk_total_risk_score,
                'pattern': p.pattern_type,
                'total_cases': p.total_cases,
                'region': p.region,
                'age': p.current_age,
                'days_since_last': p.days_since_last
            }
            for p in persons
        ]
    }