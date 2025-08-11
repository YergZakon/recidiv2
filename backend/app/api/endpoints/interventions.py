"""
API endpoints для планов вмешательства
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/interventions", tags=["Interventions"])


@router.post(
    "/plan",
    summary="План вмешательства",
    description="Возвращает план профилактических мероприятий для лица"
)
async def get_intervention_plan(data: Dict) -> Dict:
    """Получение плана вмешательства для лица"""
    try:
        person_id = data.get("person_id")
        if not person_id:
            raise HTTPException(status_code=400, detail="person_id is required")
        
        # Простой план вмешательства на основе констант
        from app.core.constants import INTERVENTION_PROGRAMS
        
        # Возвращаем план для кражи как базовый (можно расширить)
        program_data = INTERVENTION_PROGRAMS.get('Кража', INTERVENTION_PROGRAMS['Кража'])
        
        start_date = datetime.now().date() + timedelta(days=1)
        end_date = start_date + timedelta(days=program_data['duration'])
        
        intervention_plan = {
            "person_id": person_id,
            "risk_level": "high",
            "programs": [
                {
                    "id": "program_1",
                    "name": program_data['programs'][0],
                    "description": f"Программа {program_data['programs'][0]}",
                    "type": "social",
                    "duration_days": program_data['duration'],
                    "intensity": program_data['urgency'],
                    "effectiveness": 85.0
                }
            ],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_duration_days": program_data['duration'],
            "expected_risk_reduction": 25.0
        }
        
        return intervention_plan
        
    except Exception as e:
        logger.error(f"Ошибка получения плана вмешательства: {e}")
        raise HTTPException(status_code=500, detail=str(e))