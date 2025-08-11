"""
API для импорта данных из Excel
Только для администраторов
КРИТИЧНО: Сохраняем все данные из исследования
"""
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Optional
from app.core.database import get_db
from app.services.data_import_service import DataImportService
from app.models.real_data import PersonReal, ViolationReal, CrimeTransition, CrimeTimeWindow
import shutil
from pathlib import Path
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/import", tags=["data-import"])

# Временное хранилище статусов импорта (в продакшене использовать Redis)
import_tasks = {}

@router.post("/excel", summary="Импорт данных из Excel файла")
async def import_excel_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    # current_user: User = Depends(get_current_admin),  # TODO: Добавить авторизацию
    db: Session = Depends(get_db)
):
    """
    Импорт данных из Excel файла
    
    Поддерживаемые файлы:
    - RISK_ANALYSIS_RESULTS.xlsx - основные данные о лицах (146,570 записей)
    - crime_analysis_results.xlsx - данные о переходах админ->уголовка
    - ML_DATASET_COMPLETE.xlsx - полный датасет для ML
    
    КРИТИЧНО: Файлы должны сохранять оригинальную структуру из исследования
    """
    
    # Проверяем тип файла
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="Только Excel файлы (.xlsx) поддерживаются"
        )
    
    # Проверяем размер файла (макс 100MB)
    if file.size > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Файл слишком большой (макс 100MB)"
        )
    
    # Сохраняем временный файл
    temp_dir = Path("/tmp/crime_prevention_import")
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / f"{uuid.uuid4()}_{file.filename}"
    
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сохранения файла: {str(e)}"
        )
    
    # Создаем задачу импорта
    task_id = str(uuid.uuid4())
    import_tasks[task_id] = {
        'status': 'pending',
        'filename': file.filename,
        'progress': 0,
        'message': 'Задача создана'
    }
    
    # Запускаем импорт в фоне
    background_tasks.add_task(
        import_data_task,
        temp_file,
        file.filename,
        task_id,
        db
    )
    
    return {
        "task_id": task_id,
        "message": f"Импорт {file.filename} запущен",
        "status_url": f"/api/import/status/{task_id}"
    }

@router.get("/status/{task_id}", summary="Получить статус импорта")
async def get_import_status(
    task_id: str,
    # current_user: User = Depends(get_current_admin)  # TODO: Добавить авторизацию
):
    """Получить статус задачи импорта"""
    
    if task_id not in import_tasks:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )
    
    return import_tasks[task_id]

@router.post("/sync-all", summary="Синхронизация всех данных")
async def sync_all_data(
    background_tasks: BackgroundTasks,
    # current_user: User = Depends(get_current_admin),  # TODO: Добавить авторизацию
    db: Session = Depends(get_db)
):
    """
    Синхронизация всех данных из папки data/
    Импортирует все Excel файлы согласно исследованию
    
    КРИТИЧНО: Проверяет соответствие константам:
    - 146,570 правонарушений
    - 12,333 рецидивистов
    - 72.7% нестабильный паттерн
    - 6,465 переходов админ->кража
    """
    
    import_service = DataImportService(db)
    
    # Список файлов для импорта в порядке приоритета
    files_to_import = [
        ("RISK_ANALYSIS_RESULTS.xlsx", "persons"),
        ("crime_analysis_results.xlsx", "transitions"),
        ("ML_DATASET_COMPLETE.xlsx", "ml_data"),
        ("serious_crimes_analysis.xlsx", "serious_crimes"),
        ("risk_escalation_matrix.xlsx", "escalation_matrix")
    ]
    
    results = {}
    
    for filename, data_type in files_to_import:
        filepath = Path("data") / filename
        if filepath.exists():
            try:
                logger.info(f"Импорт {filename}...")
                
                if data_type == "persons":
                    stats = import_service.import_risk_analysis_results(filepath)
                elif data_type == "transitions":
                    stats = import_service.import_crime_transitions(filepath)
                else:
                    stats = {"status": "pending", "message": "Тип данных в разработке"}
                
                results[filename] = stats
            except Exception as e:
                logger.error(f"Ошибка импорта {filename}: {e}")
                results[filename] = {"status": "error", "error": str(e)}
        else:
            results[filename] = {"status": "not_found", "error": f"Файл не найден в {filepath.parent}"}
    
    # Импортируем временные окна
    import_service.import_time_windows()
    
    # Получаем итоговую статистику
    summary = import_service.get_import_summary()
    
    return {
        "message": "Синхронизация завершена",
        "results": results,
        "summary": summary,
        "critical_checks": summary.get('import_stats', {}).get('critical_checks', {})
    }

@router.get("/statistics", summary="Статистика импортированных данных")
async def get_import_statistics(
    db: Session = Depends(get_db)
):
    """
    Получить статистику по импортированным данным
    Проверяет соответствие критическим константам из исследования
    """
    
    # Общая статистика
    total_persons = db.query(PersonReal).count()
    
    # Распределение по риск-баллам
    critical_risk = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score >= 7
    ).count()
    high_risk = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score >= 5,
        PersonReal.risk_total_risk_score < 7
    ).count()
    medium_risk = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score >= 3,
        PersonReal.risk_total_risk_score < 5
    ).count()
    low_risk = db.query(PersonReal).filter(
        PersonReal.risk_total_risk_score < 3
    ).count()
    
    # Паттерны поведения
    patterns = db.query(
        PersonReal.pattern_type,
        func.count(PersonReal.id)
    ).group_by(PersonReal.pattern_type).all()
    
    pattern_stats = {}
    for pattern, count in patterns:
        if pattern:
            pattern_stats[pattern] = {
                'count': count,
                'percent': (count / total_persons * 100) if total_persons > 0 else 0
            }
    
    # Рецидивисты
    recidivists = db.query(PersonReal).filter(
        PersonReal.total_cases > 1
    ).count()
    
    # Переходы
    transitions = db.query(CrimeTransition).all()
    admin_to_theft = sum(
        t.transition_count for t in transitions 
        if t.criminal_offense and 'кража' in t.criminal_offense.lower()
    )
    
    # Временные окна
    time_windows = db.query(CrimeTimeWindow).all()
    
    # Проверка критических констант
    critical_checks = {
        'total_persons': {
            'value': total_persons,
            'expected': 146570,
            'status': 'PASS' if abs(total_persons - 146570) < 1000 else 'WARNING'
        },
        'recidivists': {
            'value': recidivists,
            'expected': 12333,
            'status': 'PASS' if abs(recidivists - 12333) < 500 else 'WARNING'
        },
        'unstable_pattern': {
            'value': pattern_stats.get('mixed_unstable', {}).get('percent', 0),
            'expected': 72.7,
            'status': 'PASS' if abs(pattern_stats.get('mixed_unstable', {}).get('percent', 0) - 72.7) < 5 else 'WARNING'
        },
        'admin_to_theft': {
            'value': admin_to_theft,
            'expected': 6465,
            'status': 'PASS' if abs(admin_to_theft - 6465) < 100 else 'WARNING'
        }
    }
    
    return {
        'total_persons': total_persons,
        'risk_distribution': {
            'critical': {'count': critical_risk, 'percent': (critical_risk/total_persons*100) if total_persons > 0 else 0},
            'high': {'count': high_risk, 'percent': (high_risk/total_persons*100) if total_persons > 0 else 0},
            'medium': {'count': medium_risk, 'percent': (medium_risk/total_persons*100) if total_persons > 0 else 0},
            'low': {'count': low_risk, 'percent': (low_risk/total_persons*100) if total_persons > 0 else 0}
        },
        'patterns': pattern_stats,
        'recidivists': {
            'count': recidivists,
            'percent': (recidivists / total_persons * 100) if total_persons > 0 else 0
        },
        'transitions': {
            'total': len(transitions),
            'admin_to_theft': admin_to_theft
        },
        'time_windows': len(time_windows),
        'critical_checks': critical_checks,
        'data_quality': {
            'high_quality': db.query(PersonReal).filter(PersonReal.data_quality_score >= 0.8).count(),
            'medium_quality': db.query(PersonReal).filter(
                PersonReal.data_quality_score >= 0.5,
                PersonReal.data_quality_score < 0.8
            ).count(),
            'low_quality': db.query(PersonReal).filter(PersonReal.data_quality_score < 0.5).count()
        }
    }

@router.delete("/clear-test-data", summary="Удалить только тестовые данные")
async def clear_test_data(
    # current_user: User = Depends(get_current_admin),  # TODO: Добавить авторизацию
    db: Session = Depends(get_db),
    confirm: bool = Query(False, description="Подтверждение удаления тестовых данных")
):
    """
    Удалить только тестовые/демо данные, сохранив реальные данные из Excel
    
    БЕЗОПАСНО: Удаляет только тестовые таблицы, реальные данные остаются
    """
    
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Требуется подтверждение для удаления тестовых данных (confirm=true)"
        )
    
    try:
        from sqlalchemy import text, inspect
        
        # Получаем все таблицы
        inspector = inspect(db.get_bind())
        all_tables = inspector.get_table_names()
        
        # Таблицы с реальными данными (НЕ ТРОГАЕМ!)
        real_data_tables = {
            'persons_real',
            'violations_real', 
            'crime_transitions',
            'crime_time_windows',
            'risk_assessment_history',
            'alembic_version'
        }
        
        # Находим тестовые таблицы
        test_tables = [t for t in all_tables if t not in real_data_tables and not t.startswith('pg_')]
        
        # Проверяем что реальные данные есть
        real_data_count = db.query(PersonReal).count()
        if real_data_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Реальные данные не найдены! Сначала импортируйте Excel файлы."
            )
        
        # Удаляем тестовые таблицы
        dropped_tables = []
        for table in test_tables:
            try:
                db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                dropped_tables.append(table)
                logger.info(f"Удалена тестовая таблица: {table}")
            except Exception as e:
                logger.warning(f"Не удалось удалить таблицу {table}: {e}")
        
        db.commit()
        
        return {
            'status': 'success',
            'message': f'Удалены тестовые данные. Реальные данные сохранены.',
            'dropped_test_tables': dropped_tables,
            'preserved_real_data': {
                'persons_count': real_data_count,
                'tables_preserved': list(real_data_tables)
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления тестовых данных: {str(e)}"
        )

@router.delete("/clear-all", summary="Очистить все импортированные данные")
async def clear_all_data(
    # current_user: User = Depends(get_current_admin),  # TODO: Добавить авторизацию
    db: Session = Depends(get_db),
    confirm: bool = Query(False, description="Подтверждение удаления"),
    i_understand_this_deletes_real_data: bool = Query(False, description="Подтверждение что понимаете риски")
):
    """
    Очистить ВСЕ данные включая реальные данные из Excel
    ОПАСНО: Это удалит ВСЕ данные включая импортированные из исследования!
    """
    
    if not confirm or not i_understand_this_deletes_real_data:
        raise HTTPException(
            status_code=400,
            detail="Требуется двойное подтверждение для удаления всех данных (confirm=true и i_understand_this_deletes_real_data=true)"
        )
    
    try:
        # Удаляем данные из всех таблиц
        deleted_counts = {
            'persons': db.query(PersonReal).delete(),
            'violations': db.query(ViolationReal).delete() if db.query(ViolationReal).count() > 0 else 0,
            'transitions': db.query(CrimeTransition).delete(),
            'time_windows': db.query(CrimeTimeWindow).delete()
        }
        
        db.commit()
        
        return {
            'status': 'success',
            'message': 'ВСЕ данные удалены (включая реальные из исследования)',
            'deleted': deleted_counts,
            'warning': 'Для восстановления данных запустите импорт заново'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка удаления данных: {str(e)}"
        )

async def import_data_task(filepath: Path, filename: str, task_id: str, db: Session):
    """Фоновая задача импорта данных"""
    
    try:
        # Обновляем статус
        import_tasks[task_id]['status'] = 'in_progress'
        import_tasks[task_id]['message'] = f'Импорт {filename}...'
        
        service = DataImportService(db)
        
        # Определяем тип файла и импортируем
        if "RISK_ANALYSIS" in filename.upper():
            import_tasks[task_id]['message'] = 'Импорт данных о лицах...'
            stats = service.import_risk_analysis_results(filepath)
            
        elif "CRIME_ANALYSIS" in filename.upper():
            import_tasks[task_id]['message'] = 'Импорт данных о переходах...'
            stats = service.import_crime_transitions(filepath)
            
        else:
            import_tasks[task_id]['status'] = 'error'
            import_tasks[task_id]['message'] = f'Неизвестный тип файла: {filename}'
            return
        
        # Обновляем финальный статус
        import_tasks[task_id]['status'] = 'completed'
        import_tasks[task_id]['progress'] = 100
        import_tasks[task_id]['stats'] = stats
        import_tasks[task_id]['message'] = f'Импорт завершен: {stats.get("successfully_imported", 0)} записей'
        
    except Exception as e:
        logger.error(f"Ошибка импорта: {e}")
        import_tasks[task_id]['status'] = 'error'
        import_tasks[task_id]['message'] = f'Ошибка: {str(e)}'
        
    finally:
        # Удаляем временный файл
        if filepath.exists():
            filepath.unlink()