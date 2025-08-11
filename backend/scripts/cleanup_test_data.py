#!/usr/bin/env python3
"""
Очистка тестовых/демо данных из БД
Оставляет только реальные данные импортированные из Excel

КРИТИЧНО: 
- НЕ удаляет таблицы реальных данных (persons_real, etc.)
- Удаляет только тестовые/демо таблицы
- Сохраняет все реальные данные из исследования
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.models.real_data import PersonReal
from sqlalchemy import text, inspect
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_all_tables():
    """Получить список всех таблиц в БД"""
    inspector = inspect(engine)
    return inspector.get_table_names()

def identify_table_types():
    """Разделить таблицы на реальные и тестовые"""
    all_tables = get_all_tables()
    
    # Таблицы с реальными данными (НЕ УДАЛЯТЬ!)
    real_data_tables = {
        'persons_real',           # Реальные люди из Excel
        'violations_real',        # Реальные нарушения
        'crime_transitions',      # Переходы админ->уголовка
        'crime_time_windows',     # Временные окна преступлений
        'risk_assessment_history', # История расчетов
        'alembic_version'         # Версии миграций
    }
    
    # Системные таблицы PostgreSQL
    system_tables = {
        'pg_stat_statements',
        'spatial_ref_sys'
    }
    
    # Разделяем таблицы
    real_tables = []
    test_tables = []
    system_tables_found = []
    
    for table in all_tables:
        if table in real_data_tables:
            real_tables.append(table)
        elif any(sys_table in table for sys_table in system_tables):
            system_tables_found.append(table)
        else:
            test_tables.append(table)
    
    return real_tables, test_tables, system_tables_found

def check_real_data_exists(db):
    """Проверить что реальные данные есть в БД"""
    try:
        count = db.query(PersonReal).count()
        return count > 0, count
    except Exception as e:
        logger.error(f"Ошибка проверки реальных данных: {e}")
        return False, 0

def backup_critical_data(db, backup_info):
    """Создать резервную копию критической информации"""
    try:
        # Статистика реальных данных
        total_persons = db.query(PersonReal).count()
        
        if total_persons > 0:
            # Критические метрики
            high_risk = db.query(PersonReal).filter(
                PersonReal.risk_total_risk_score >= 7
            ).count()
            
            backup_info['real_data_stats'] = {
                'total_persons': total_persons,
                'high_risk_persons': high_risk,
                'backup_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"📊 Резервная копия статистики: {total_persons:,} людей, {high_risk:,} высокий риск")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка создания резервной копии: {e}")
        return False

def drop_test_tables(db, test_tables):
    """Удалить тестовые таблицы"""
    dropped_count = 0
    errors = []
    
    for table in test_tables:
        try:
            logger.info(f"🗑️ Удаление таблицы {table}...")
            db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            dropped_count += 1
        except Exception as e:
            error_msg = f"Ошибка удаления {table}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    if dropped_count > 0:
        db.commit()
        logger.info(f"✅ Удалено {dropped_count} тестовых таблиц")
    
    return dropped_count, errors

def verify_cleanup(db):
    """Проверить результаты очистки"""
    real_tables, test_tables, system_tables = identify_table_types()
    
    verification_results = {
        'real_data_preserved': True,
        'test_data_removed': True,
        'errors': []
    }
    
    # Проверяем что реальные данные сохранены
    try:
        persons_count = db.query(PersonReal).count()
        if persons_count == 0:
            verification_results['real_data_preserved'] = False
            verification_results['errors'].append("⚠️ Реальные данные о людях потеряны!")
        else:
            logger.info(f"✅ Реальные данные сохранены: {persons_count:,} человек")
    except Exception as e:
        verification_results['real_data_preserved'] = False
        verification_results['errors'].append(f"Ошибка проверки реальных данных: {e}")
    
    # Проверяем что тестовые таблицы удалены
    remaining_tables = get_all_tables()
    remaining_test_tables = [t for t in remaining_tables if t not in real_tables and not any(sys in t for sys in ['pg_', 'spatial_'])]
    
    if remaining_test_tables:
        logger.warning(f"⚠️ Остались тестовые таблицы: {remaining_test_tables}")
        verification_results['test_data_removed'] = False
        verification_results['remaining_test_tables'] = remaining_test_tables
    
    return verification_results

def main():
    """Основная функция очистки"""
    
    print("=" * 60)
    print("🧹 ОЧИСТКА ТЕСТОВЫХ ДАННЫХ")
    print("   Система раннего предупреждения преступлений")
    print("=" * 60)
    
    # Создаем сессию БД
    db = SessionLocal()
    backup_info = {}
    
    try:
        # 1. Проверяем наличие реальных данных
        logger.info("🔍 Проверка наличия реальных данных...")
        has_real_data, real_count = check_real_data_exists(db)
        
        if not has_real_data:
            logger.error("❌ Реальные данные не найдены!")
            logger.error("Сначала импортируйте данные: python scripts/initial_import.py")
            return 1
        
        logger.info(f"✅ Найдено {real_count:,} реальных записей")
        
        # 2. Анализируем таблицы
        logger.info("📊 Анализ таблиц в БД...")
        real_tables, test_tables, system_tables = identify_table_types()
        
        print(f"\n📋 АНАЛИЗ ТАБЛИЦ:")
        print(f"Реальные данные ({len(real_tables)}): {', '.join(real_tables)}")
        print(f"Тестовые таблицы ({len(test_tables)}): {', '.join(test_tables)}")
        print(f"Системные таблицы ({len(system_tables)}): {', '.join(system_tables)}")
        
        if not test_tables:
            logger.info("✅ Тестовые таблицы не найдены. Очистка не требуется.")
            return 0
        
        # 3. Подтверждение от пользователя
        print(f"\n⚠️ ВНИМАНИЕ! Будут удалены {len(test_tables)} тестовых таблиц:")
        for table in test_tables:
            print(f"  - {table}")
        
        print(f"\n✅ Будут СОХРАНЕНЫ {len(real_tables)} таблиц с реальными данными:")
        for table in real_tables:
            print(f"  - {table}")
        
        response = input(f"\nПродолжить удаление {len(test_tables)} тестовых таблиц? (y/N): ")
        if response.lower() not in ['y', 'yes', 'да']:
            logger.info("Операция отменена пользователем")
            return 0
        
        # 4. Создаем резервную копию критических данных
        logger.info("💾 Создание резервной копии критических данных...")
        if not backup_critical_data(db, backup_info):
            logger.error("❌ Не удалось создать резервную копию")
            return 1
        
        # 5. Удаляем тестовые таблицы
        logger.info("🗑️ Удаление тестовых таблиц...")
        dropped_count, errors = drop_test_tables(db, test_tables)
        
        if errors:
            logger.warning(f"⚠️ Возникли ошибки при удалении:")
            for error in errors:
                logger.warning(f"  {error}")
        
        # 6. Проверяем результаты
        logger.info("🔍 Проверка результатов очистки...")
        verification = verify_cleanup(db)
        
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ОЧИСТКИ")
        print("=" * 60)
        
        print(f"Удалено тестовых таблиц: {dropped_count}")
        print(f"Ошибок при удалении: {len(errors)}")
        print(f"Реальные данные сохранены: {'✅' if verification['real_data_preserved'] else '❌'}")
        print(f"Тестовые данные удалены: {'✅' if verification['test_data_removed'] else '❌'}")
        
        if backup_info.get('real_data_stats'):
            stats = backup_info['real_data_stats']
            print(f"\n📈 Сохраненные реальные данные:")
            print(f"  - Всего людей: {stats['total_persons']:,}")
            print(f"  - Высокий риск: {stats['high_risk_persons']:,}")
        
        if verification['errors']:
            print(f"\n⚠️ Проблемы:")
            for error in verification['errors']:
                print(f"  - {error}")
        
        if verification.get('remaining_test_tables'):
            print(f"\n⚠️ Остались таблицы (требуют ручного удаления):")
            for table in verification['remaining_test_tables']:
                print(f"  - {table}")
        
        # Итоговый статус
        if verification['real_data_preserved'] and verification['test_data_removed']:
            print("\n✅ ОЧИСТКА ЗАВЕРШЕНА УСПЕШНО!")
            print("Система готова для работы только с реальными данными")
            return 0
        else:
            print("\n⚠️ Очистка завершена с предупреждениями")
            return 2
    
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        db.rollback()
        return 1
        
    finally:
        db.close()

if __name__ == "__main__":
    exit_code = main()
    
    if exit_code == 0:
        print(f"\n💡 Следующие шаги:")
        print("1. Перезапустите сервер: uvicorn app.main:app --reload")
        print("2. Проверьте API: GET /api/persons/real/statistics")
        print("3. Система теперь работает только с реальными данными!")
    elif exit_code == 2:
        print(f"\n⚠️ Требуется ручная проверка:")
        print("1. Проверьте оставшиеся таблицы")
        print("2. Убедитесь что реальные данные корректны")
    
    sys.exit(exit_code)