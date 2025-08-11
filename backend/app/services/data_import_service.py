"""
Сервис импорта реальных данных из Excel
КРИТИЧНО: Сохраняем ВСЕ данные без потерь
Проверяем соответствие критическим константам из исследования
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.real_data import (
    PersonReal, ViolationReal, CrimeTransition, 
    CrimeTimeWindow, RiskAssessmentHistory,
    CRITICAL_TIME_WINDOWS
)
import logging
import json

logger = logging.getLogger(__name__)

class DataImportService:
    """Сервис для импорта данных из Excel с сохранением всех критических констант"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_dir = Path("data")
        self.import_stats = {
            'total_processed': 0,
            'successfully_imported': 0,
            'updated': 0,
            'errors': [],
            'warnings': [],
            'critical_checks': {}
        }
        
    def import_risk_analysis_results(self, filepath: Path = None) -> Dict:
        """
        Импорт RISK_ANALYSIS_RESULTS.xlsx
        КРИТИЧНО: Сохраняем все 146,570 записей
        """
        
        if not filepath:
            filepath = self.data_dir / "RISK_ANALYSIS_RESULTS.xlsx"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Файл {filepath} не найден")
        
        logger.info(f"🚀 Начинаем импорт из {filepath}")
        
        try:
            # Читаем Excel с различными вариантами
            df = pd.read_excel(filepath, engine='openpyxl')
            logger.info(f"📊 Загружено {len(df)} записей")
            
            # Сохраняем информацию о колонках
            logger.info(f"Колонки в файле: {list(df.columns)}")
            
            # Обрабатываем данные пакетами для оптимизации
            batch_size = 1000
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                self._process_person_batch(batch, filepath.name)
                
                # Коммитим каждый batch
                self.db.commit()
                logger.info(f"✅ Импортировано {min(i+batch_size, len(df))}/{len(df)}")
            
            self.import_stats['total_processed'] = len(df)
            
            # КРИТИЧНО: Проверяем соответствие константам из исследования
            self._verify_critical_constants()
            
        except Exception as e:
            logger.error(f"❌ Ошибка импорта: {e}")
            self.db.rollback()
            raise
        
        return self.import_stats
    
    def _process_person_batch(self, batch: pd.DataFrame, source_file: str):
        """Обработка пакета записей о людях"""
        
        for _, row in batch.iterrows():
            try:
                # Подготавливаем данные, адаптируя под различные форматы колонок
                person_data = self._prepare_person_data(row, source_file)
                
                if not person_data.get('iin'):
                    self.import_stats['errors'].append({
                        'row': _,
                        'error': 'Отсутствует ИИН'
                    })
                    continue
                
                # Проверяем существование
                existing = self.db.query(PersonReal).filter_by(
                    iin=person_data['iin']
                ).first()
                
                if existing:
                    # Обновляем существующую запись
                    for key, value in person_data.items():
                        setattr(existing, key, value)
                    self.import_stats['updated'] += 1
                else:
                    # Создаем новую запись
                    person = PersonReal(**person_data)
                    self.db.add(person)
                    self.import_stats['successfully_imported'] += 1
                    
            except Exception as e:
                logger.error(f"Ошибка обработки строки: {e}")
                self.import_stats['errors'].append({
                    'row': _,
                    'error': str(e),
                    'iin': row.get('ИИН', 'Unknown')
                })
    
    def _prepare_person_data(self, row: pd.Series, source_file: str) -> Dict:
        """Подготовка данных для записи в БД с адаптацией под различные форматы"""
        
        # Конвертируем pandas объекты в сериализуемые типы
        raw_dict = row.to_dict()
        serializable_dict = {}
        for key, value in raw_dict.items():
            if pd.isna(value):
                serializable_dict[key] = None
            elif hasattr(value, 'isoformat'):  # datetime/Timestamp
                serializable_dict[key] = value.isoformat()
            else:
                serializable_dict[key] = value
        
        person_data = {
            'source_file': source_file,
            'import_date': datetime.utcnow(),
            'raw_data': serializable_dict
        }
        
        # Маппинг возможных названий колонок
        column_mappings = {
            'iin': ['ИИН', 'IIN', 'iin', 'person_iin'],
            'last_name': ['Фамилия', 'last_name', 'surname'],
            'first_name': ['Имя', 'first_name', 'name'],
            'middle_name': ['Отчество', 'middle_name', 'patronymic'],
            'current_age': ['current_age', 'age', 'Возраст'],
            'gender': ['gender', 'Пол', 'sex'],
            'region': ['region', 'Регион', 'Oblast'],
            'pattern_type': ['pattern_type', 'behavior_pattern', 'Pattern'],
            'total_cases': ['total_cases', 'total_violations', 'Всего дел'],
            'criminal_count': ['criminal_count', 'criminal_cases', 'Уголовные'],
            'admin_count': ['admin_count', 'admin_cases', 'Административные'],
            'risk_total_risk_score': ['risk_total_risk_score', 'risk_score', 'total_risk_score', 'Risk Score'],
            'days_since_last': ['days_since_last', 'days_since_last_violation'],
            'has_property': ['has_property', 'property_owner'],
            'has_job': ['has_job', 'employed'],
            'has_family': ['has_family', 'married'],
        }
        
        # Применяем маппинг
        for db_field, excel_columns in column_mappings.items():
            for excel_col in excel_columns:
                if excel_col in row.index and pd.notna(row[excel_col]):
                    value = row[excel_col]
                    
                    # Очистка и преобразование значений
                    if db_field == 'iin':
                        # Очищаем ИИН от лишних символов
                        value = str(value).replace('-', '').replace(' ', '').strip()
                    elif db_field in ['current_age', 'total_cases', 'criminal_count', 'admin_count', 'days_since_last']:
                        # Преобразуем в целые числа
                        try:
                            value = int(float(value))
                        except:
                            value = 0
                    elif db_field == 'risk_total_risk_score':
                        # Преобразуем в float
                        try:
                            value = float(value)
                        except:
                            value = 0.0
                    elif db_field in ['has_property', 'has_job', 'has_family']:
                        # Преобразуем в 0/1
                        value = 1 if value in [1, '1', 'Yes', 'Да', True] else 0
                    
                    person_data[db_field] = value
                    break
        
        # Создаем полное ФИО
        if all(k in person_data for k in ['last_name', 'first_name']):
            person_data['full_name'] = f"{person_data.get('last_name', '')} {person_data.get('first_name', '')} {person_data.get('middle_name', '')}".strip()
        
        # Определяем категорию риска
        risk_score = person_data.get('risk_total_risk_score', 0)
        if risk_score >= 7:
            person_data['risk_category'] = 'critical'
        elif risk_score >= 5:
            person_data['risk_category'] = 'high'
        elif risk_score >= 3:
            person_data['risk_category'] = 'medium'
        else:
            person_data['risk_category'] = 'low'
        
        # Вычисляем качество данных
        required_fields = ['iin', 'last_name', 'first_name', 'current_age', 'gender', 
                          'total_cases', 'risk_total_risk_score']
        filled_fields = sum(1 for f in required_fields if person_data.get(f))
        person_data['data_quality_score'] = filled_fields / len(required_fields)
        
        return person_data
    
    def _verify_critical_constants(self):
        """
        Проверка критических констант из исследования
        КРИТИЧНО: Должны совпадать с исследованием!
        """
        
        logger.info("🔍 Проверка критических констант...")
        
        # 1. Общее количество записей (должно быть ~146,570)
        total_count = self.db.query(PersonReal).count()
        expected_total = 146570
        diff_percent = abs(total_count - expected_total) / expected_total * 100
        
        if diff_percent < 1:  # Допуск 1%
            logger.info(f"✅ Всего записей: {total_count:,} (ожидалось {expected_total:,})")
            self.import_stats['critical_checks']['total_count'] = 'PASS'
        else:
            logger.warning(f"⚠️ Всего записей: {total_count:,} (ожидалось {expected_total:,}, разница {diff_percent:.1f}%)")
            self.import_stats['warnings'].append(f"Количество записей отличается на {diff_percent:.1f}%")
            self.import_stats['critical_checks']['total_count'] = 'WARNING'
        
        # 2. Процент нестабильного паттерна (должен быть ~72.7%)
        unstable_count = self.db.query(PersonReal).filter(
            PersonReal.pattern_type == 'mixed_unstable'
        ).count()
        
        if total_count > 0:
            unstable_percent = (unstable_count / total_count) * 100
            expected_percent = 72.7
            
            if abs(unstable_percent - expected_percent) < 5:  # Допуск 5%
                logger.info(f"✅ Нестабильный паттерн: {unstable_percent:.1f}% (ожидалось {expected_percent}%)")
                self.import_stats['critical_checks']['unstable_pattern'] = 'PASS'
            else:
                logger.warning(f"⚠️ Нестабильный паттерн: {unstable_percent:.1f}% (ожидалось {expected_percent}%)")
                self.import_stats['warnings'].append(f"Процент нестабильного паттерна: {unstable_percent:.1f}%")
                self.import_stats['critical_checks']['unstable_pattern'] = 'WARNING'
        
        # 3. Количество рецидивистов (должно быть ~12,333)
        recidivists = self.db.query(PersonReal).filter(
            PersonReal.total_cases > 1
        ).count()
        expected_recidivists = 12333
        
        if abs(recidivists - expected_recidivists) < 500:  # Допуск 500
            logger.info(f"✅ Рецидивистов: {recidivists:,} (ожидалось {expected_recidivists:,})")
            self.import_stats['critical_checks']['recidivists'] = 'PASS'
        else:
            logger.warning(f"⚠️ Рецидивистов: {recidivists:,} (ожидалось {expected_recidivists:,})")
            self.import_stats['warnings'].append(f"Количество рецидивистов: {recidivists:,}")
            self.import_stats['critical_checks']['recidivists'] = 'WARNING'
        
        # 4. Распределение по категориям риска
        risk_distribution = self.db.query(
            PersonReal.risk_category,
            func.count(PersonReal.id)
        ).group_by(PersonReal.risk_category).all()
        
        logger.info("📊 Распределение по категориям риска:")
        for category, count in risk_distribution:
            percent = (count / total_count * 100) if total_count > 0 else 0
            logger.info(f"  - {category}: {count:,} ({percent:.1f}%)")
        
        # 5. Критический риск (7+)
        critical_risk = self.db.query(PersonReal).filter(
            PersonReal.risk_total_risk_score >= 7
        ).count()
        critical_percent = (critical_risk / total_count * 100) if total_count > 0 else 0
        logger.info(f"🔴 Критический риск (7+): {critical_risk:,} ({critical_percent:.1f}%)")
    
    def import_crime_transitions(self, filepath: Path = None) -> Dict:
        """
        Импорт данных о переходах админ->уголовка
        КРИТИЧНО: 6,465 переходов админ->кража
        """
        
        if not filepath:
            filepath = self.data_dir / "crime_analysis_results.xlsx"
        
        if not filepath.exists():
            logger.warning(f"Файл {filepath} не найден")
            return {'status': 'file_not_found'}
        
        logger.info(f"📊 Импорт переходов из {filepath}")
        
        try:
            # Читаем лист с эскалацией
            df = pd.read_excel(filepath, sheet_name="Эскалация")
            
            for _, row in df.iterrows():
                transition_data = {
                    'admin_violation': row.get('Административное', row.get('admin_type')),
                    'criminal_offense': row.get('Уголовное', row.get('criminal_type')),
                    'transition_count': int(row.get('Количество переходов', row.get('count', 0))),
                    'avg_days': float(row.get('Среднее время', row.get('avg_days', 0))),
                    'min_days': int(row.get('Мин время', row.get('min_days', 0))),
                    'max_days': int(row.get('Макс время', row.get('max_days', 0))),
                    'preventable_percent': float(row.get('Предотвратимость', row.get('preventable', 0))),
                    'source_file': filepath.name,
                    'import_date': datetime.utcnow()
                }
                
                # Проверяем существование
                existing = self.db.query(CrimeTransition).filter_by(
                    admin_violation=transition_data['admin_violation'],
                    criminal_offense=transition_data['criminal_offense']
                ).first()
                
                if existing:
                    for key, value in transition_data.items():
                        setattr(existing, key, value)
                else:
                    transition = CrimeTransition(**transition_data)
                    self.db.add(transition)
            
            self.db.commit()
            
            # Проверяем критическую константу
            admin_to_theft = self.db.query(CrimeTransition).filter(
                CrimeTransition.criminal_offense.like('%кража%')
            ).all()
            
            total_transitions = sum(t.transition_count for t in admin_to_theft)
            logger.info(f"✅ Импортировано переходов админ->кража: {total_transitions:,} (ожидалось 6,465)")
            
            if abs(total_transitions - 6465) > 100:
                logger.warning(f"⚠️ Количество переходов админ->кража отличается от ожидаемого")
            
            return {'status': 'success', 'imported': len(df)}
            
        except Exception as e:
            logger.error(f"❌ Ошибка импорта переходов: {e}")
            self.db.rollback()
            return {'status': 'error', 'error': str(e)}
    
    def import_time_windows(self):
        """Импорт критических временных окон из исследования"""
        
        logger.info("⏰ Импорт временных окон...")
        
        for crime_type, days in CRITICAL_TIME_WINDOWS.items():
            existing = self.db.query(CrimeTimeWindow).filter_by(
                crime_type=crime_type
            ).first()
            
            if not existing:
                window = CrimeTimeWindow(
                    crime_type=crime_type,
                    window_days=days,
                    median_days=days,  # Используем как медиану
                    preventability_score=97.0 if crime_type != "Убийство" else 82.3,  # Из исследования
                    source="research_2024"
                )
                self.db.add(window)
        
        self.db.commit()
        logger.info(f"✅ Импортировано {len(CRITICAL_TIME_WINDOWS)} временных окон")
    
    def get_import_summary(self) -> Dict:
        """Получение сводки по импортированным данным"""
        
        summary = {
            'persons': {
                'total': self.db.query(PersonReal).count(),
                'with_high_risk': self.db.query(PersonReal).filter(
                    PersonReal.risk_total_risk_score >= 7
                ).count(),
                'recidivists': self.db.query(PersonReal).filter(
                    PersonReal.total_cases > 1
                ).count()
            },
            'transitions': {
                'total': self.db.query(CrimeTransition).count(),
                'admin_to_theft': self.db.query(CrimeTransition).filter(
                    CrimeTransition.criminal_offense.like('%кража%')
                ).count()
            },
            'time_windows': self.db.query(CrimeTimeWindow).count(),
            'import_stats': self.import_stats
        }
        
        return summary