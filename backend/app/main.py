"""
Crime Prevention System API

ОСНОВАНО НА: Анализе 146,570 правонарушений и 12,333 рецидивистов
ПОРТИРОВАНО ИЗ: Streamlit приложения utils/risk_calculator.py

FastAPI приложение для системы раннего предупреждения преступлений
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import traceback
from datetime import datetime

# Импорт роутеров
from app.api.endpoints import risks, forecasts, statistics, persons, data_import, interventions

# Импорт констант для проверки загрузки
from app.core.constants import (
    TOTAL_VIOLATIONS_ANALYZED, 
    TOTAL_RECIDIVISTS,
    PREVENTABLE_CRIMES_PERCENT,
    PATTERN_DISTRIBUTION,
    RISK_WEIGHTS,
    CRIME_TIME_WINDOWS
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager для FastAPI приложения
    Проверяет загрузку всех критических констант при старте
    """
    logger.info("🚀 Запуск Crime Prevention System API...")
    
    try:
        # Проверяем загрузку критических констант
        assert TOTAL_VIOLATIONS_ANALYZED == 146570, "Неверное количество проанализированных нарушений"
        assert TOTAL_RECIDIVISTS == 12333, "Неверное количество рецидивистов"
        assert PREVENTABLE_CRIMES_PERCENT == 97.0, "Неверный процент предотвратимых преступлений"
        
        # Проверяем веса (должны в сумме давать 1.0)
        weights_sum = sum(RISK_WEIGHTS.values())
        assert abs(weights_sum - 1.0) < 0.001, f"Сумма весов не равна 1.0: {weights_sum}"
        
        # Проверяем временные окна
        assert len(CRIME_TIME_WINDOWS) == 8, f"Неверное количество временных окон: {len(CRIME_TIME_WINDOWS)}"
        
        # Проверяем паттерны
        assert len(PATTERN_DISTRIBUTION) >= 5, "Не все паттерны поведения загружены"
        
        logger.info("✅ Все критические константы загружены корректно")
        logger.info(f"📊 Проанализировано нарушений: {TOTAL_VIOLATIONS_ANALYZED:,}")
        logger.info(f"👥 Рецидивистов в выборке: {TOTAL_RECIDIVISTS:,}")
        logger.info(f"🎯 Предотвратимых преступлений: {PREVENTABLE_CRIMES_PERCENT}%")
        
        yield
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка при запуске: {e}")
        logger.error(traceback.format_exc())
        raise
    
    logger.info("🛑 Завершение работы Crime Prevention System API")


# Создание FastAPI приложения
app = FastAPI(
    title="Crime Prevention System API",
    description=f"""
    ## 🚔 Система раннего предупреждения преступлений

    REST API для расчета рисков рецидива и прогнозирования преступлений.
    
    **Основано на научном исследовании:**
    - 📊 {TOTAL_VIOLATIONS_ANALYZED:,} проанализированных правонарушений
    - 👥 {TOTAL_RECIDIVISTS:,} рецидивистов в выборке  
    - 🎯 {PREVENTABLE_CRIMES_PERCENT}% предотвратимых преступлений
    
    **Ключевые возможности:**
    - 🔢 Расчет риск-баллов (0-10) с детализацией по компонентам
    - 📅 Прогнозирование временных окон до преступлений
    - 📈 Быстрая оценка и пакетная обработка
    - 📋 Календарь профилактических мероприятий
    - 📊 Статистика из исследования
    
    **Технические детали:**
    - Портировано из проверенного Streamlit приложения
    - Идентичные алгоритмы расчета рисков
    - Валидация входных данных через Pydantic
    - Полное логирование и аудит расчетов
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React development
        "http://localhost:5173",    # Vite development  
        "http://localhost:8080",    # Alternative frontend
        "https://localhost:3000",   # HTTPS variants
        "https://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request, call_next):
    """Логирование всех HTTP запросов"""
    start_time = datetime.utcnow()
    
    # Логируем входящий запрос
    logger.info(f"📝 {request.method} {request.url.path} от {request.client.host}")
    
    try:
        response = await call_next(request)
        
        # Вычисляем время обработки
        process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Логируем ответ
        logger.info(f"✅ {request.method} {request.url.path} -> {response.status_code} [{process_time:.1f}ms]")
        
        # Добавляем заголовок с временем обработки
        response.headers["X-Process-Time"] = f"{process_time:.1f}ms"
        
        return response
        
    except Exception as e:
        process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"💥 {request.method} {request.url.path} -> ERROR [{process_time:.1f}ms]: {e}")
        raise


# Подключение роутеров (префиксы уже определены в самих роутерах)
app.include_router(risks.router)
app.include_router(forecasts.router)
app.include_router(statistics.router)
app.include_router(persons.router)
app.include_router(interventions.router)
app.include_router(data_import.router)


# Базовые endpoints
@app.get(
    "/",
    summary="Информация об API",
    description="Основная информация о системе предупреждения преступлений"
)
async def root():
    """Корневой endpoint с информацией об API"""
    return {
        "name": "Crime Prevention System API",
        "version": "2.0.0",
        "description": "API для расчета рисков рецидива и прогнозирования преступлений",
        "research_base": {
            "total_analyzed": TOTAL_VIOLATIONS_ANALYZED,
            "total_recidivists": TOTAL_RECIDIVISTS,
            "preventable_percent": PREVENTABLE_CRIMES_PERCENT
        },
        "endpoints": {
            "risks": "/api/risks",
            "forecasts": "/api/forecasts",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get(
    "/health",
    summary="Проверка работоспособности",
    description="Комплексная проверка всех компонентов системы"
)
async def health_check():
    """
    Комплексная проверка работоспособности API
    
    Returns:
        Dict: Подробная информация о статусе всех компонентов
    """
    try:
        from app.services.risk_service import RiskService
        
        # Проверяем сервис расчета рисков
        service = RiskService()
        
        # Тестовый расчет для проверки работоспособности
        test_data = {
            'pattern_type': 'mixed_unstable',
            'total_cases': 3,
            'current_age': 25,
            'criminal_count': 1,
            'admin_count': 2,
            'days_since_last': 60
        }
        
        # Проверяем валидацию
        is_valid, errors = service.validate_person_data(test_data)
        
        # Проверяем расчет риска
        if is_valid:
            result = service.calculate_risk_for_person_dict(test_data)
            risk_calculation_works = 0 <= result['risk_score'] <= 10
        else:
            risk_calculation_works = False
        
        # Проверяем прогнозирование
        forecasts = service.forecaster.forecast_crime_timeline(test_data)
        forecasting_works = len(forecasts) == len(CRIME_TIME_WINDOWS)
        
        # Общий статус
        all_healthy = (
            is_valid and 
            risk_calculation_works and 
            forecasting_works and
            len(RISK_WEIGHTS) == 6 and
            len(CRIME_TIME_WINDOWS) == 8
        )
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "constants_loaded": {
                    "status": "operational",
                    "total_analyzed": TOTAL_VIOLATIONS_ANALYZED,
                    "total_recidivists": TOTAL_RECIDIVISTS,
                    "weights_loaded": len(RISK_WEIGHTS),
                    "time_windows_loaded": len(CRIME_TIME_WINDOWS)
                },
                "risk_calculation": {
                    "status": "operational" if risk_calculation_works else "error",
                    "validation_working": is_valid,
                    "test_calculation": result['risk_score'] if risk_calculation_works else None
                },
                "crime_forecasting": {
                    "status": "operational" if forecasting_works else "error", 
                    "forecasts_generated": len(forecasts),
                    "expected_forecasts": len(CRIME_TIME_WINDOWS)
                },
                "api_endpoints": {
                    "risks_router": "mounted",
                    "forecasts_router": "mounted"
                }
            },
            "performance": {
                "test_calculation_completed": risk_calculation_works,
                "test_forecasting_completed": forecasting_works
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "components": {
                "constants_loaded": len(RISK_WEIGHTS) == 6 and len(CRIME_TIME_WINDOWS) == 8,
                "risk_calculation": "error",
                "crime_forecasting": "error",
                "api_endpoints": "unknown"
            }
        }


@app.get(
    "/version",
    summary="Информация о версии",
    description="Детальная информация о версии API и компонентах"
)
async def get_version():
    """Информация о версии API и его компонентах"""
    return {
        "api_version": "2.0.0",
        "python_version": "3.8+",
        "fastapi_version": "FastAPI",
        "research_version": "2024",
        "data_sources": {
            "violations_analyzed": TOTAL_VIOLATIONS_ANALYZED,
            "recidivists_analyzed": TOTAL_RECIDIVISTS,
            "analysis_period": "2019-2024",
            "coverage": "Национальная выборка"
        },
        "algorithm_versions": {
            "risk_calculator": "2.0",
            "crime_forecaster": "2.0", 
            "constants": "2024.01"
        },
        "build_info": {
            "built_at": datetime.utcnow().isoformat(),
            "environment": "production"
        }
    }


# Обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик исключений"""
    logger.error(f"Необработанная ошибка в {request.method} {request.url.path}: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Обработчик 404
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Обработчик для несуществующих endpoints"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"Endpoint {request.url.path} не найден",
            "available_endpoints": {
                "risks": "/api/risks",
                "forecasts": "/api/forecasts",
                "docs": "/docs",
                "health": "/health"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Запуск Crime Prevention System API в режиме отладки")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )