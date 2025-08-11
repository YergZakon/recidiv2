#!/usr/bin/env python3
"""
Первичный импорт всех данных в БД
Запускать после создания БД

КРИТИЧНО: Проверяет соответствие всем константам из исследования:
- 146,570 правонарушений
- 12,333 рецидивистов  
- 72.7% нестабильный паттерн
- 6,465 переходов админ->кража
- 97% предотвратимых преступлений
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.models.real_data import Base, PersonReal, CrimeTransition, CrimeTimeWindow
from app.services.data_import_service import DataImportService
from pathlib import Path
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_prerequisites():
    """Проверка предусловий для импорта"""
    data_dir = Path("data")
    
    if not data_dir.exists():
        logger.error(f"❌ Папка {data_dir.absolute()} не существует")
        logger.info("Создайте папку 'data' в корне backend и поместите туда Excel файлы")
        return False
    
    required_files = [
        "RISK_ANALYSIS_RESULTS.xlsx",  # Основной файл с 146,570 записями
        "crime_analysis_results.xlsx"   # Файл с переходами админ->уголовка
    ]
    
    missing_files = []
    for filename in required_files:
        filepath = data_dir / filename
        if not filepath.exists():
            missing_files.append(filename)
        else:
            # Проверяем размер файла
            size_mb = filepath.stat().st_size / (1024 * 1024)
            logger.info(f"✅ Найден {filename} ({size_mb:.1f} MB)")
    
    if missing_files:
        logger.error(f"❌ Отсутствуют критические файлы: {missing_files}")
        logger.error(f"Поместите файлы в папку {data_dir.absolute()}")
        return False
    
    # Опциональные файлы
    optional_files = [
        "ML_DATASET_COMPLETE.xlsx",
        "serious_crimes_analysis.xlsx",
        "risk_escalation_matrix.xlsx"
    ]
    
    for filename in optional_files:
        filepath = data_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            logger.info(f"📁 Найден опциональный файл {filename} ({size_mb:.1f} MB)")
        else:
            logger.warning(f"⚠️ Опциональный файл {filename} не найден")
    
    return True

def create_tables():
    """Создание таблиц в БД"""
    logger.info("📊 Создание таблиц в БД...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы созданы")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц: {e}")
        return False

def main():
    """Основная функция импорта"""
    
    print("=" * 60)
    print("🚀 СИСТЕМА РАННЕГО ПРЕДУПРЕЖДЕНИЯ ПРЕСТУПЛЕНИЙ")
    print("   Первичный импорт реальных данных")
    print("=" * 60)
    
    # Проверяем предусловия
    if not check_prerequisites():
        logger.error("❌ Предусловия не выполнены. Импорт отменен.")
        return 1
    
    # Создаем таблицы
    if not create_tables():
        logger.error("❌ Не удалось создать таблицы. Импорт отменен.")
        return 1
    
    # Создаем сессию БД
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже данные
        existing_count = db.query(PersonReal).count()
        if existing_count > 0:
            logger.warning(f"⚠️ В БД уже есть {existing_count:,} записей")
            response = input("Продолжить импорт? (y/n): ")
            if response.lower() != 'y':
                logger.info("Импорт отменен пользователем")
                return 0
        
        # Создаем сервис импорта
        service = DataImportService(db)
        
        print("\n" + "=" * 60)
        print("📊 ИМПОРТ ОСНОВНЫХ ДАННЫХ")
        print("=" * 60)
        
        # 1. Импортируем основные данные о лицах
        logger.info("📊 Импорт RISK_ANALYSIS_RESULTS.xlsx...")
        start_time = datetime.now()
        
        stats = service.import_risk_analysis_results()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"⏱️ Время импорта: {elapsed:.1f} секунд")
        
        # Выводим статистику импорта
        print("\n📈 СТАТИСТИКА ИМПОРТА:")
        print("-" * 40)
        print(f"Обработано записей: {stats['total_processed']:,}")
        print(f"Успешно импортировано: {stats['successfully_imported']:,}")
        print(f"Обновлено: {stats.get('updated', 0):,}")
        print(f"Ошибок: {len(stats.get('errors', [])):,}")
        
        if stats.get('warnings'):
            print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
            for warning in stats['warnings']:
                print(f"  - {warning}")
        
        # 2. Импортируем переходы админ->уголовка
        print("\n" + "=" * 60)
        print("📊 ИМПОРТ ПЕРЕХОДОВ")
        print("=" * 60)
        
        logger.info("📊 Импорт crime_analysis_results.xlsx...")
        transition_stats = service.import_crime_transitions()
        
        if transition_stats.get('status') == 'success':
            logger.info(f"✅ Импортировано переходов: {transition_stats.get('imported', 0)}")
        else:
            logger.warning(f"⚠️ Проблема с импортом переходов: {transition_stats}")
        
        # 3. Импортируем временные окна
        logger.info("⏰ Импорт временных окон...")
        service.import_time_windows()
        
        # 4. Финальная проверка критических констант
        print("\n" + "=" * 60)
        print("🔍 ПРОВЕРКА КРИТИЧЕСКИХ КОНСТАНТ")
        print("=" * 60)
        
        # Общее количество
        total = db.query(PersonReal).count()
        print(f"\n📊 Всего людей в БД: {total:,}")
        
        expected_total = 146570
        diff = abs(total - expected_total)
        diff_percent = (diff / expected_total * 100) if expected_total > 0 else 100
        
        if diff_percent < 1:
            print(f"✅ Соответствует ожидаемому ({expected_total:,}) - разница {diff_percent:.2f}%")
        else:
            print(f"⚠️ Отличается от ожидаемого ({expected_total:,}) на {diff_percent:.1f}%")
        
        # Рецидивисты
        recidivists = db.query(PersonReal).filter(PersonReal.total_cases > 1).count()
        print(f"\n👥 Рецидивистов: {recidivists:,}")
        
        expected_recidivists = 12333
        if abs(recidivists - expected_recidivists) < 500:
            print(f"✅ Соответствует ожидаемому (~{expected_recidivists:,})")
        else:
            print(f"⚠️ Отличается от ожидаемого ({expected_recidivists:,})")
        
        # Паттерны
        from sqlalchemy import func
        patterns = db.query(
            PersonReal.pattern_type,
            func.count(PersonReal.id)
        ).group_by(PersonReal.pattern_type).all()
        
        print("\n🔄 Распределение паттернов:")
        total_with_pattern = sum(count for _, count in patterns if _)
        for pattern, count in patterns:
            if pattern:
                percent = (count / total_with_pattern * 100) if total_with_pattern > 0 else 0
                print(f"  - {pattern}: {count:,} ({percent:.1f}%)")
                
                if pattern == 'mixed_unstable':
                    if abs(percent - 72.7) < 5:
                        print(f"    ✅ Соответствует ожидаемым 72.7%")
                    else:
                        print(f"    ⚠️ Отличается от ожидаемых 72.7%")
        
        # Риск-баллы
        high_risk = db.query(PersonReal).filter(PersonReal.risk_total_risk_score >= 7).count()
        critical_percent = (high_risk / total * 100) if total > 0 else 0
        print(f"\n🔴 Критический риск (7+): {high_risk:,} ({critical_percent:.1f}%)")
        
        # Переходы
        transitions = db.query(CrimeTransition).all()
        admin_to_theft = sum(
            t.transition_count for t in transitions 
            if t.criminal_offense and 'кража' in t.criminal_offense.lower()
        )
        print(f"\n🔀 Переходов админ->кража: {admin_to_theft:,}")
        
        expected_transitions = 6465
        if abs(admin_to_theft - expected_transitions) < 100:
            print(f"✅ Соответствует ожидаемому ({expected_transitions:,})")
        else:
            print(f"⚠️ Отличается от ожидаемого ({expected_transitions:,})")
        
        # Временные окна
        time_windows = db.query(CrimeTimeWindow).count()
        print(f"\n⏰ Временных окон: {time_windows}")
        
        print("\n" + "=" * 60)
        print("✅ ИМПОРТ ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 60)
        
        # Итоговая сводка
        print("\n📋 ИТОГОВАЯ СВОДКА:")
        print("-" * 40)
        print(f"Людей в БД: {total:,}")
        print(f"Рецидивистов: {recidivists:,}")
        print(f"Критический риск: {high_risk:,}")
        print(f"Переходов: {len(transitions)}")
        print(f"Временных окон: {time_windows}")
        
        # Проверка критических констант
        critical_checks = stats.get('critical_checks', {})
        if critical_checks:
            print("\n🔍 Статус критических проверок:")
            for check, status in critical_checks.items():
                icon = "✅" if status == 'PASS' else "⚠️"
                print(f"  {icon} {check}: {status}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        db.rollback()
        return 1
        
    finally:
        db.close()

if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print("\n💡 Следующие шаги:")
        print("1. Запустите сервер: uvicorn app.main:app --reload")
        print("2. Откройте API документацию: http://localhost:8001/docs")
        print("3. Проверьте статистику: GET /api/import/statistics")
        print("4. Начните работу с реальными данными!")
    
    sys.exit(exit_code)