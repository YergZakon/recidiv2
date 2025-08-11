"""
API endpoints для общей статистики системы
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
from datetime import datetime
import logging

from app.core.constants import (
    TOTAL_VIOLATIONS_ANALYZED, 
    TOTAL_RECIDIVISTS,
    PREVENTABLE_CRIMES_PERCENT,
    PATTERN_DISTRIBUTION,
    CRIME_TIME_WINDOWS
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/statistics", tags=["Statistics"])


@router.get(
    "/summary",
    summary="Общая статистика системы",
    description="Возвращает основную статистику из исследования 146,570 нарушений"
)
async def get_system_statistics() -> Dict:
    """Получение общей статистики системы"""
    try:
        return {
            "total_violations": TOTAL_VIOLATIONS_ANALYZED,
            "total_recidivists": TOTAL_RECIDIVISTS,
            "preventable_percent": PREVENTABLE_CRIMES_PERCENT,
            "patterns_distribution": {
                "mixed_unstable": PATTERN_DISTRIBUTION.get('mixed_unstable', 72.7),
                "chronic_criminal": PATTERN_DISTRIBUTION.get('chronic_criminal', 13.6),
                "escalating": PATTERN_DISTRIBUTION.get('escalating', 7.0),
                "deescalating": PATTERN_DISTRIBUTION.get('deescalating', 5.7),
                "single": PATTERN_DISTRIBUTION.get('single', 1.0)
            },
            "crime_statistics": {
                "by_type": CRIME_TIME_WINDOWS,
                "avg_days_to_murder": CRIME_TIME_WINDOWS.get('Убийство', 143),
                "admin_to_theft_transitions": 6465
            },
            "regional_statistics": [
                {
                    "region": "Алматы",
                    "total_persons": 1234,
                    "high_risk_count": 156,
                    "critical_risk_count": 23,
                    "average_risk_score": 4.2,
                    "status": "caution"
                },
                {
                    "region": "Астана", 
                    "total_persons": 987,
                    "high_risk_count": 98,
                    "critical_risk_count": 15,
                    "average_risk_score": 3.8,
                    "status": "safe"
                },
                {
                    "region": "Шымкент",
                    "total_persons": 756,
                    "high_risk_count": 145,
                    "critical_risk_count": 34,
                    "average_risk_score": 5.1,
                    "status": "warning"
                }
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/patterns",
    summary="Распределение паттернов поведения",
    description="Детальное распределение поведенческих паттернов рецидивистов"
)
async def get_pattern_distribution() -> Dict:
    """Получение распределения паттернов поведения"""
    try:
        return {
            "total_analyzed": TOTAL_RECIDIVISTS,
            "patterns": {
                "mixed_unstable": {
                    "count": int(TOTAL_RECIDIVISTS * 0.727),
                    "percentage": 72.7,
                    "description": "Смешанный нестабильный паттерн",
                    "risk_level": "high"
                },
                "chronic_criminal": {
                    "count": int(TOTAL_RECIDIVISTS * 0.136), 
                    "percentage": 13.6,
                    "description": "Хронический преступный паттерн",
                    "risk_level": "critical"
                },
                "escalating": {
                    "count": int(TOTAL_RECIDIVISTS * 0.07),
                    "percentage": 7.0,
                    "description": "Эскалирующий паттерн",
                    "risk_level": "high"
                },
                "deescalating": {
                    "count": int(TOTAL_RECIDIVISTS * 0.057),
                    "percentage": 5.7,
                    "description": "Деэскалирующий паттерн", 
                    "risk_level": "medium"
                },
                "single": {
                    "count": int(TOTAL_RECIDIVISTS * 0.01),
                    "percentage": 1.0,
                    "description": "Единичные случаи",
                    "risk_level": "low"
                }
            },
            "transitions": {
                "admin_to_theft": 6465,
                "most_dangerous": "mixed_unstable"
            }
        }
    except Exception as e:
        logger.error(f"Ошибка получения паттернов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/crimes",
    summary="Статистика преступлений", 
    description="Временные окна и предотвратимость по типам преступлений"
)
async def get_crime_statistics() -> Dict:
    """Получение статистики по преступлениям"""
    try:
        return {
            "time_windows": CRIME_TIME_WINDOWS,
            "preventability": {
                "Мошенничество": 82.3,
                "Кража": 87.3,
                "Убийство": 97.0,
                "Вымогательство": 100.0,
                "Грабеж": 60.2,
                "Разбой": 20.2,
                "Изнасилование": 65.6
            },
            "severity": {
                "most_preventable": "Убийство",
                "least_preventable": "Разбой",
                "average_window": sum(CRIME_TIME_WINDOWS.values()) / len(CRIME_TIME_WINDOWS),
                "critical_window": min(CRIME_TIME_WINDOWS.values())
            }
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики преступлений: {e}")
        raise HTTPException(status_code=500, detail=str(e))