#!/usr/bin/env python3
"""
Анализ структуры реальных Excel файлов
ВАЖНО: Не изменяем структуру, адаптируем код под неё
"""
import pandas as pd
import os
import sys
from pathlib import Path
import json

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = Path("../data")

def analyze_excel_files():
    """Анализируем все Excel файлы и их структуру"""
    
    files_info = {
        "RISK_ANALYSIS_RESULTS.xlsx": None,
        "ML_DATASET_COMPLETE.xlsx": None,
        "crime_analysis_results.xlsx": None,
        "serious_crimes_analysis.xlsx": None,
        "risk_escalation_matrix.xlsx": None
    }
    
    for filename in files_info.keys():
        filepath = DATA_DIR / filename
        if filepath.exists():
            print(f"\n📁 Анализ {filename}:")
            print("=" * 60)
            
            try:
                # Читаем файл
                excel_file = pd.ExcelFile(filepath)
                
                # Информация о листах
                print(f"Листы: {excel_file.sheet_names}")
                
                file_data = {
                    'sheets': {},
                    'main_sheet': None,
                    'total_rows': 0
                }
                
                # Анализ каждого листа
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(filepath, sheet_name=sheet)
                    print(f"\n  Лист '{sheet}':")
                    print(f"  - Строк: {len(df)}")
                    print(f"  - Колонок: {len(df.columns)}")
                    print(f"  - Колонки (первые 10): {list(df.columns)[:10]}")
                    
                    sheet_info = {
                        'row_count': len(df),
                        'columns': list(df.columns),
                        'has_iin': False,
                        'has_risk_score': False,
                        'sample_data': {}
                    }
                    
                    # Проверяем ключевые поля
                    if 'ИИН' in df.columns:
                        print(f"  - ✅ Найдено поле ИИН")
                        sheet_info['has_iin'] = True
                        # Проверяем формат ИИН
                        sample_iin = df['ИИН'].dropna().iloc[0] if len(df['ИИН'].dropna()) > 0 else None
                        print(f"  - Пример ИИН: {sample_iin}")
                        sheet_info['sample_data']['iin'] = str(sample_iin) if sample_iin else None
                        file_data['main_sheet'] = sheet
                    
                    # Проверяем различные варианты полей с риск-баллом
                    risk_fields = ['risk_total_risk_score', 'risk_score', 'total_risk_score', 'Risk Score']
                    for risk_field in risk_fields:
                        if risk_field in df.columns:
                            print(f"  - ✅ Найдено поле риска: {risk_field}")
                            sheet_info['has_risk_score'] = True
                            sheet_info['risk_field_name'] = risk_field
                            print(f"  - Диапазон: {df[risk_field].min():.2f} - {df[risk_field].max():.2f}")
                            sheet_info['sample_data']['risk_range'] = {
                                'min': float(df[risk_field].min()),
                                'max': float(df[risk_field].max()),
                                'mean': float(df[risk_field].mean())
                            }
                            break
                    
                    # Проверяем поля паттернов
                    pattern_fields = ['pattern_type', 'behavior_pattern', 'Pattern']
                    for pattern_field in pattern_fields:
                        if pattern_field in df.columns:
                            print(f"  - ✅ Найдено поле паттерна: {pattern_field}")
                            unique_patterns = df[pattern_field].unique()
                            print(f"  - Уникальные паттерны: {unique_patterns[:5]}")
                            sheet_info['sample_data']['patterns'] = list(unique_patterns[:5])
                            break
                    
                    file_data['sheets'][sheet] = sheet_info
                    file_data['total_rows'] += len(df)
                
                files_info[filename] = file_data
                
            except Exception as e:
                print(f"  ❌ Ошибка при чтении файла: {e}")
                files_info[filename] = {'error': str(e)}
        else:
            print(f"\n❌ Файл {filename} не найден в {DATA_DIR.absolute()}")
            files_info[filename] = {'error': 'File not found'}
    
    return files_info

def check_critical_constants(files_info):
    """Проверяем критические константы из исследования"""
    print("\n" + "=" * 60)
    print("🔍 ПРОВЕРКА КРИТИЧЕСКИХ КОНСТАНТ")
    print("=" * 60)
    
    # Ищем файл с основными данными
    main_file = None
    for filename, info in files_info.items():
        if info and info.get('main_sheet'):
            main_file = filename
            break
    
    if main_file:
        filepath = DATA_DIR / main_file
        df = pd.read_excel(filepath, sheet_name=files_info[main_file]['main_sheet'])
        
        total_records = len(df)
        print(f"\n📊 Всего записей: {total_records:,}")
        
        # Проверяем соответствие исследованию
        expected_total = 146570
        if abs(total_records - expected_total) < 1000:  # Допуск 1000 записей
            print(f"✅ Соответствует ожидаемому количеству (~{expected_total:,})")
        else:
            print(f"⚠️ Отличается от ожидаемого ({expected_total:,})")
        
        # Проверяем паттерны если есть
        pattern_fields = ['pattern_type', 'behavior_pattern', 'Pattern']
        for pattern_field in pattern_fields:
            if pattern_field in df.columns:
                pattern_counts = df[pattern_field].value_counts()
                total_with_pattern = pattern_counts.sum()
                
                if 'mixed_unstable' in pattern_counts.index:
                    unstable_count = pattern_counts['mixed_unstable']
                    unstable_percent = (unstable_count / total_with_pattern) * 100
                    print(f"\n🔄 Нестабильный паттерн: {unstable_percent:.1f}%")
                    
                    if abs(unstable_percent - 72.7) < 5:  # Допуск 5%
                        print(f"✅ Соответствует ожидаемым 72.7%")
                    else:
                        print(f"⚠️ Отличается от ожидаемых 72.7%")
                break
        
        # Проверяем количество рецидивистов
        if 'total_cases' in df.columns:
            recidivists = df[df['total_cases'] > 1]
            recidivist_count = len(recidivists)
            print(f"\n👥 Рецидивистов: {recidivist_count:,}")
            
            expected_recidivists = 12333
            if abs(recidivist_count - expected_recidivists) < 500:
                print(f"✅ Соответствует ожидаемому количеству (~{expected_recidivists:,})")
            else:
                print(f"⚠️ Отличается от ожидаемого ({expected_recidivists:,})")

if __name__ == "__main__":
    print("🚀 Начинаем анализ структуры Excel файлов")
    print("=" * 60)
    
    structure = analyze_excel_files()
    
    # Проверяем критические константы
    check_critical_constants(structure)
    
    # Сохраняем структуру для использования в импорте
    output_file = Path('data_structure.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✅ Структура сохранена в {output_file.absolute()}")
    print("\n📋 РЕЗЮМЕ:")
    print("-" * 40)
    
    for filename, info in structure.items():
        if info and not info.get('error'):
            print(f"✅ {filename}: {info.get('total_rows', 0):,} записей")
        elif info and info.get('error'):
            print(f"❌ {filename}: {info['error']}")
        else:
            print(f"❌ {filename}: Не найден")