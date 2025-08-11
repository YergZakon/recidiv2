#!/usr/bin/env python3
"""
Скрипт для исправления ИИН в базе данных
Добавляет ведущие нули к коротким ИИН до 12 символов
"""
import sqlite3
import sys
from pathlib import Path

def fix_short_iin():
    """Исправляет короткие ИИН, добавляя ведущие нули"""
    
    db_path = "crime_prevention.db"
    if not Path(db_path).exists():
        print(f"❌ База данных {db_path} не найдена!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Находим все записи с короткими ИИН
        cursor.execute("SELECT id, iin, full_name FROM persons_real WHERE length(iin) < 12")
        short_iin_records = cursor.fetchall()
        
        if not short_iin_records:
            print("✅ Все ИИН уже имеют правильную длину")
            return True
            
        print(f"🔧 Найдено {len(short_iin_records)} записей с короткими ИИН")
        
        # Создаем backup таблицу
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS persons_real_backup AS 
            SELECT * FROM persons_real WHERE 1=0
        """)
        
        # Копируем данные в backup
        cursor.execute("DELETE FROM persons_real_backup")
        cursor.execute("INSERT INTO persons_real_backup SELECT * FROM persons_real")
        
        fixed_count = 0
        failed_count = 0
        
        for record_id, old_iin, full_name in short_iin_records:
            try:
                # Определяем сколько нулей добавить
                current_length = len(old_iin)
                
                if current_length < 12:
                    # Добавляем ведущие нули
                    new_iin = old_iin.zfill(12)
                    
                    # Проверяем, что новый ИИН уникален
                    cursor.execute("SELECT COUNT(*) FROM persons_real WHERE iin = ? AND id != ?", (new_iin, record_id))
                    count = cursor.fetchone()[0]
                    
                    if count == 0:
                        # Обновляем запись
                        cursor.execute("UPDATE persons_real SET iin = ? WHERE id = ?", (new_iin, record_id))
                        print(f"✅ {full_name}: {old_iin} → {new_iin}")
                        fixed_count += 1
                    else:
                        print(f"⚠️  {full_name}: {old_iin} → {new_iin} (конфликт - уже существует)")
                        failed_count += 1
                        
            except Exception as e:
                print(f"❌ Ошибка для {full_name} ({old_iin}): {e}")
                failed_count += 1
        
        # Подтверждаем изменения
        conn.commit()
        
        print(f"\n📊 Результаты:")
        print(f"   Исправлено: {fixed_count}")
        print(f"   Ошибок: {failed_count}")
        print(f"   Всего обработано: {len(short_iin_records)}")
        
        # Проверяем финальное состояние
        cursor.execute("SELECT COUNT(*) FROM persons_real WHERE length(iin) < 12")
        remaining_short = cursor.fetchone()[0]
        
        if remaining_short == 0:
            print("✅ Все ИИН теперь имеют правильную длину!")
        else:
            print(f"⚠️  Осталось {remaining_short} записей с короткими ИИН")
            
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        # Откатываем изменения
        conn.rollback()
        return False
        
    finally:
        conn.close()

def verify_iin_fix():
    """Проверяет результат исправления ИИН"""
    
    conn = sqlite3.connect("crime_prevention.db")
    cursor = conn.cursor()
    
    try:
        # Статистика по длине ИИН
        cursor.execute("""
            SELECT length(iin) as iin_length, COUNT(*) as count
            FROM persons_real 
            GROUP BY length(iin) 
            ORDER BY iin_length
        """)
        
        stats = cursor.fetchall()
        
        print("\n📈 Статистика длины ИИН после исправления:")
        total = 0
        for length, count in stats:
            print(f"   {length} символов: {count} записей")
            total += count
            
        print(f"   Всего записей: {total}")
        
        # Проверяем примеры исправленных ИИН
        cursor.execute("""
            SELECT iin, full_name 
            FROM persons_real 
            WHERE iin LIKE '0%' 
            LIMIT 5
        """)
        
        examples = cursor.fetchall()
        if examples:
            print("\n🔍 Примеры исправленных ИИН (начинающихся с 0):")
            for iin, name in examples:
                print(f"   {iin} - {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Запуск исправления ИИН в базе данных")
    print("=" * 50)
    
    if fix_short_iin():
        verify_iin_fix()
        print("\n✅ Исправление завершено успешно!")
    else:
        print("\n❌ Исправление не удалось!")
        sys.exit(1)