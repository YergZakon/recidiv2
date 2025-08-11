#!/usr/bin/env python3
"""
Скрипт проверки констант системы раннего предупреждения преступлений

Демонстрирует что все критические значения из исследования 146,570 правонарушений
точно перенесены в backend модуль
"""

import sys
import os
sys.path.insert(0, '.')

def main():
    print("🚨 ПРОВЕРКА КОНСТАНТ СИСТЕМЫ РАННЕГО ПРЕДУПРЕЖДЕНИЯ ПРЕСТУПЛЕНИЙ")
    print("=" * 80)
    
    try:
        # Импорт через core модуль
        from app.core import (
            TOTAL_VIOLATIONS_ANALYZED, TOTAL_RECIDIVISTS, PREVENTABLE_CRIMES_PERCENT,
            UNSTABLE_PATTERN_PERCENT, ADMIN_TO_THEFT_TRANSITIONS, AVG_DAYS_TO_MURDER,
            CRIME_TIME_WINDOWS, PREVENTION_RATES, RISK_WEIGHTS, PATTERN_RISKS,
            PATTERN_DISTRIBUTION, get_risk_category_by_score, print_constants_summary
        )
        
        print("✅ Все модули загружены успешно!\n")
        
        # Основная статистика
        print("📊 ОСНОВНАЯ СТАТИСТИКА ИССЛЕДОВАНИЯ:")
        print(f"   • Всего проанализировано: {TOTAL_VIOLATIONS_ANALYZED:,} правонарушений")
        print(f"   • Рецидивистов в базе: {TOTAL_RECIDIVISTS:,}")
        print(f"   • Процент предотвратимых преступлений: {PREVENTABLE_CRIMES_PERCENT}%")
        print(f"   • Нестабильный паттерн поведения: {UNSTABLE_PATTERN_PERCENT}%")
        print(f"   • Переходы административное → кража: {ADMIN_TO_THEFT_TRANSITIONS:,}")
        print(f"   • Среднее время до убийства: {AVG_DAYS_TO_MURDER} дней\n")
        
        # Временные окна
        print("⏰ ВРЕМЕННЫЕ ОКНА ДО ПРЕСТУПЛЕНИЙ:")
        for crime_type in ['Мошенничество', 'Кража', 'Убийство', 'Грабеж', 'Разбой']:
            days = CRIME_TIME_WINDOWS[crime_type]
            preventable = PREVENTION_RATES[crime_type]
            print(f"   • {crime_type}: {days} дней ({preventable}% предотвратимо)")
        print()
        
        # Веса факторов
        print("⚖️ ВЕСА ФАКТОРОВ РИСКА:")
        total_weight = 0
        for weight_name, weight_value in RISK_WEIGHTS.items():
            print(f"   • {weight_name}: {weight_value}")
            total_weight += weight_value
        print(f"   • СУММА: {total_weight:.3f} (должна быть 1.000)\n")
        
        # Паттерны поведения
        print("📈 ПАТТЕРНЫ КРИМИНАЛЬНОГО ПОВЕДЕНИЯ:")
        total_percent = 0
        for pattern, percent in PATTERN_DISTRIBUTION.items():
            risk = PATTERN_RISKS[pattern]
            print(f"   • {pattern}: {percent}% (риск: {risk})")
            total_percent += percent
        print(f"   • СУММА: {total_percent}% (должна быть 100%)\n")
        
        # Тест категорий риска
        print("🚦 ТЕСТ КАТЕГОРИЙ РИСКА:")
        test_scores = [0.5, 2.5, 4.0, 6.0, 8.5]
        for score in test_scores:
            category = get_risk_category_by_score(score)
            print(f"   • Балл {score}: {category}")
        print()
        
        # Критические проверки
        print("🔍 КРИТИЧЕСКИЕ ПРОВЕРКИ:")
        
        checks = [
            (TOTAL_VIOLATIONS_ANALYZED == 146570, "Количество правонарушений = 146,570"),
            (TOTAL_RECIDIVISTS == 12333, "Количество рецидивистов = 12,333"),
            (PREVENTABLE_CRIMES_PERCENT == 97.0, "Процент предотвратимых = 97.0"),
            (UNSTABLE_PATTERN_PERCENT == 72.7, "Нестабильный паттерн = 72.7%"),
            (CRIME_TIME_WINDOWS['Убийство'] == 143, "Время до убийства = 143 дня"),
            (PREVENTION_RATES['Убийство'] == 97.0, "Предотвратимость убийства = 97.0%"),
            (abs(sum(RISK_WEIGHTS.values()) - 1.0) < 0.001, "Сумма весов = 1.0"),
            (abs(sum(PATTERN_DISTRIBUTION.values()) - 100.0) < 0.1, "Сумма паттернов = 100%")
        ]
        
        all_passed = True
        for passed, description in checks:
            if passed:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")
                all_passed = False
        
        print("\n" + "=" * 80)
        
        if all_passed:
            print("🎉 ВСЕ КРИТИЧЕСКИЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
            print("   Константы из исследования 146,570 правонарушений сохранены точно.")
        else:
            print("💥 КРИТИЧЕСКАЯ ОШИБКА: Некоторые проверки не прошли!")
            print("   НЕМЕДЛЕННО проверьте константы!")
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"💥 ОШИБКА ПРИ ПРОВЕРКЕ КОНСТАНТ: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)