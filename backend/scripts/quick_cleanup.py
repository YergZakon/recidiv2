#!/usr/bin/env python3
"""
Быстрая очистка тестовых данных
Простой скрипт для удаления тестовых таблиц с минимальными вопросами
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.real_data import PersonReal
from sqlalchemy import text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_cleanup():
    """Быстрая очистка тестовых данных"""
    
    db = SessionLocal()
    
    try:
        # Проверяем реальные данные
        real_count = db.query(PersonReal).count()
        if real_count == 0:
            print("❌ Реальные данные не найдены!")
            print("Сначала импортируйте: python scripts/initial_import.py")
            return False
        
        print(f"✅ Найдено {real_count:,} реальных записей")
        
        # Получаем все таблицы
        inspector = inspect(db.get_bind())
        all_tables = inspector.get_table_names()
        
        # Реальные таблицы (НЕ ТРОГАЕМ)
        real_tables = {
            'persons_real', 'violations_real', 'crime_transitions',
            'crime_time_windows', 'risk_assessment_history', 'alembic_version'
        }
        
        # Находим тестовые
        test_tables = [t for t in all_tables if t not in real_tables and not t.startswith('pg_')]
        
        if not test_tables:
            print("✅ Тестовые таблицы не найдены. Очистка не требуется.")
            return True
        
        print(f"🗑️ Найдено {len(test_tables)} тестовых таблиц:")
        for table in test_tables:
            print(f"  - {table}")
        
        # Подтверждение
        response = input(f"\nУдалить {len(test_tables)} тестовых таблиц? (y/N): ")
        if response.lower() not in ['y', 'yes', 'да']:
            print("Отменено")
            return False
        
        # Удаляем
        dropped = 0
        for table in test_tables:
            try:
                db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                dropped += 1
                print(f"✅ Удалена: {table}")
            except Exception as e:
                print(f"❌ Ошибка удаления {table}: {e}")
        
        db.commit()
        
        # Финальная проверка
        final_count = db.query(PersonReal).count()
        if final_count == real_count:
            print(f"\n✅ ОЧИСТКА ЗАВЕРШЕНА!")
            print(f"Удалено тестовых таблиц: {dropped}")
            print(f"Реальные данные сохранены: {final_count:,} человек")
            return True
        else:
            print(f"⚠️ Предупреждение: количество реальных данных изменилось!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Быстрая очистка тестовых данных")
    print("=" * 40)
    
    success = quick_cleanup()
    
    if success:
        print("\n💡 Следующие шаги:")
        print("1. Перезапустите сервер")
        print("2. Проверьте: GET /api/persons/real/statistics")
    else:
        print("\nДля детальной диагностики запустите:")
        print("python scripts/cleanup_test_data.py")
    
    sys.exit(0 if success else 1)